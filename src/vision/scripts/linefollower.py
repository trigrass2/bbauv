#!/usr/bin/env python

import roslib; roslib.load_manifest('vision')
import rospy

import sys
import smach
import smach_ros
import math
import os

from bbauv_msgs.msg import *
from bbauv_msgs.srv import *

import numpy as np
from rospy.timer import sleep

from linefollower_vision import LineFollower

class Disengage(smach.State):
    timeout = 1500

    def __init__(self, lf):
        smach.State.__init__(self, outcomes=['start_complete', 'complete_outcome', 'aborted'])
        self.linefollower = lf

    def execute(self, userdata):
        self.linefollower.unregisterSubscribers()
        #Stay in Disengage state until isAborted is False or
        #timeout after waiting for too long
        timecount = 0
        while self.linefollower.isAborted:
            if timecount > self.timeout:
                return 'aborted'
            rospy.sleep(rospy.Duration(0.1)) 
            timecount += 1
        
        self.linefollower.registerSubscribers()
        return 'start_complete'

class Searching(smach.State):
    timeout = 50 #5 seconds time out before aborting
    
    def __init__(self, lf):
        smach.State.__init__(self, outcomes=['line_found', 'aborted'])
        self.linefollower = lf

    def execute(self, userdata):
        #Check for aborted signal
        if self.linefollower.isAborted:
            return 'aborted'

        #Check if blackline is found or timeout
        timecount = 0
        while not self.linefollower.rectData['detected']:
            if timecount > self.timeout:
                self.linefollower.abortMission()
                return 'aborted'
            rospy.sleep(rospy.Duration(0.1))
            timecount += 1
        
        return 'line_found'
    
class FollowingLine(smach.State):
    def __init__(self, lf):
        smach.State.__init__(self, outcomes=['following_line', 'lost_line', 'aborted'])
        self.linefollower = lf
        self.deltaThresh = 0.15
        self.prevAngle = [] 

    def execute(self, userdata):
        #Check for aborted signal
        if self.linefollower.isAborted:
            return 'aborted'

        #Check if blackline is found
        rectData = self.linefollower.rectData
        if not rectData['detected']:
            self.prevAngle = []
            return 'lost_line'

        #Follow line!
        screenWidth = self.linefollower.screen['width']
        screenCenterX = screenWidth / 2
        deltaX = (rectData['centroid'][0] - screenCenterX) / screenWidth
        angle = rectData['angle']

        #If the rect is too far off center, do agressive sidemove
        if abs(deltaX) > 0.3:
            rospy.loginfo("Too far of center! Argressive sidemove")
            heading = normHeading(self.linefollower.curHeading - angle)
            sidemove = math.copysign(1.0, -deltaX)
            self.linefollower.sendMovement(h=heading, sm=sidemove)
            return 'following_line'

        if len(self.prevAngle) > 1:
            oppAngle = angle - 180 if angle > 0 else angle + 180
            if abs(angle - self.prevAngle[0]) > abs(oppAngle - self.prevAngle[0]):
                angle = oppAngle
                self.prevAngle[0] = angle
        else:
            self.prevAngle.append(angle)

        if deltaX < -self.deltaThresh:
            sidemove = 0.5
        elif deltaX > self.deltaThresh:
            sidemove = -0.5
        else:
            sidemove = 0.0

        if abs(angle) < 10:
            self.linefollower.sendMovement(f=0.9, sm=sidemove)
            rospy.loginfo("Forward! Sidemove: {}".format(sidemove))
        else:
            if sidemove == 0:
                sidemove = angle / 60 * 0.2
            else:
                if angle > 30:
                    angle = math.copysign(30, angle)
            
            heading = normHeading(self.linefollower.curHeading - angle)
            self.linefollower.sendMovement(h=heading, sm=sidemove)
            rospy.loginfo("Moving: {} side, {} heading".format(heading, sidemove))

        return 'following_line'

def normHeading(heading):
    if heading > 360:
        return heading - 360
    elif heading < 0:
        return heading + 360
    else:
        return heading

def main():
    rospy.init_node("linefollower")
    linefollower = LineFollower();
    

    #Creating a State Machine Container
    sm = smach.StateMachine(outcomes=['complete_line', 'aborted']) 

    with sm:
        smach.StateMachine.add("DISENGAGE", Disengage(linefollower),
                               transitions={'start_complete':'SEARCHING',
                                            'complete_outcome':'complete_line',
                                            'aborted':'aborted'})

        smach.StateMachine.add("SEARCHING", Searching(linefollower),
                               transitions={'line_found':'FOLLOWINGLINE',
                                            'aborted':'DISENGAGE'})

        smach.StateMachine.add("FOLLOWINGLINE", FollowingLine(linefollower),
                                transitions={'following_line':'FOLLOWINGLINE',
                                             'lost_line':'SEARCHING',
                                             'aborted':'DISENGAGE'})
    outcomes = sm.execute()

    rospy.spin()

if __name__ == "__main__":
    main()