import rospy
import smach, smach_ros
import numpy as np

from comms import Comms
from vision import LaneMarkerVision
from utils.utils import Utils

import time
import math
from collections import deque

""" The entry script and smach StateMachine for the task"""

class MedianFilter:
    staleDuration = 3.0

    def __init__(self, sampleWindow=30):
        self.samples = deque()
        self.sampleWindow = sampleWindow
        self.lastSampled = time.time()

    def newSample(self, sample):
        curTime = time.time()
        # Discard previous samples if we only sampled them a long time ago
        if (curTime - self.lastSampled) > self.staleDuration:
            self.samples = deque()

        self.lastSampled = curTime
        if len(self.samples) >= self.sampleWindow:
            self.samples.popleft()
        self.samples.append(sample)

    def getMedian(self):
        return np.median(self.samples)

    def getVariance(self):
        if len(self.samples) >= self.sampleWindow:
            return np.var(self.samples)
        else:
            return 999 # Just a big value

class Disengage(smach.State):
    def __init__(self, comms):
        smach.State.__init__(self, outcomes=['started', 'killed'])
        self.comms = comms

    def execute(self, userdata):
        while self.comms.isAborted:
            if self.comms.isKilled:
                return 'killed'
            rospy.sleep(rospy.Duration(0.3))

        self.comms.register()
        return 'started'

class Search(smach.State):
    timeout = 7

    def __init__(self, comms):
        smach.State.__init__(self, outcomes=['foundLanes',
                                              'timeout',
                                              'aborted'])
        self.comms = comms

    def execute(self, userdata):
        start = time.time()

        while not self.comms.retVal or \
              len(self.comms.retVal['foundLines']) == 0:
            if self.comms.isKilled or \
               self.comms.isAborted or \
               (time.time() - start) > self.timeout:
                self.comms.isAborted = True
                return 'aborted'
            rospy.sleep(rospy.Duration(0.3))

        return 'foundLanes'

class Stablize(smach.State):
    maxdx = 0.2
    maxdy = 0.2
    width = LaneMarkerVision.screen['width']
    height = LaneMarkerVision.screen['height']

    xcoeff = 2.0
    ycoeff = 1.5

    def __init__(self, comms):
        smach.State.__init__(self, outcomes=['stablized',
                                             'stablizing',
                                             'lost',
                                             'aborted'])
        self.comms = comms

    def execute(self, userdata):
        if self.comms.isKilled or self.comms.isAborted:
            return 'aborted'

        if not self.comms.retVal or \
           len(self.comms.retVal['foundLines']) == 0:
            return 'lost'

        centroid = self.comms.retVal['centroid']
        dX = (centroid[0] - self.width/2) / self.width
        dY = (centroid[1] - self.height/2) / self.height
        rospy.loginfo("x-off: %lf, y-off: %lf", dX, dY)

        if abs(dX) < self.maxdx and abs(dY) < self.maxdy:
            return 'stablized'

        f_setpoint = math.copysign(self.ycoeff * abs(dY), -dY)
        sm_setpoint = math.copysign(self.xcoeff * abs(dX), dX)
        self.comms.sendMovement(f=f_setpoint, sm=sm_setpoint, blocking=False)
        return 'stablizing'

class Align(smach.State):
    def __init__(self, comms):
        smach.State.__init__(self, outcomes=['aligned',
                                             'aligning',
                                             'lost',
                                             'aborted'])
        self.comms = comms
        self.angleSampler = MedianFilter()

    def execute(self, userdata):
        if self.comms.isKilled or self.comms.isAborted:
            return 'aborted'

        if not self.comms.retVal or \
           len(self.comms.retVal['foundLines']) == 0:
               return 'lost'

        lines = self.comms.retVal['foundLines']
        if len(lines) == 1 or self.comms.expectedLanes == 1:
            self.angleSampler.newSample(lines[0]['angle'])
        elif len(lines) >= 2:
            left = lines[0]['angle']
            right = lines[1]['angle']
            if lines[0]['pos'][0] > lines[1]['pos'][0]:
                left, right = right, left

            crossPt = self.comms.retVal['crossPt']
            if crossPt and \
               crossPt[1] < lines[0]['pos'][1] or \
               crossPt[1] < lines[1]['pos'][1]:
                left, right = right, left

            if self.comms.chosenLane == self.comms.LEFT:
                self.angleSampler.newSample(lines[0]['angle'])
            elif self.comms.chosenLane == self.comms.RIGHT:
                self.angleSampler.newSample(lines[1]['angle'])
            else:
                rospy.loginfo("Something goes wrong with chosenLane")

        if (self.angleSampler.getVariance() < 1.0):
            dAngle = Utils.toHeadingSpace(self.angleSampler.getMedian())
            adjustHeading = Utils.normAngle(self.comms.curHeading + dAngle)

            self.comms.sendMovement(h=adjustHeading, blocking=True)
            return 'aligned'
        else:
            return 'aligning'


class Forward(smach.State):
    def __init__(self, comms):
        smach.State.__init__(self, outcomes=['completed',
                                              'aborted'])
        self.comms = comms

    def execute(self, userdata):
        if self.comms.isKilled or self.comms.isAborted:
            return 'aborted'

        self.comms.sendMovement(f=5.0)
        return 'completed'

def main():
    rospy.init_node('lane_marker_node')
    myCom = Comms()

    sm = smach.StateMachine(outcomes=['succeeded', 'aborted', 'killed'])
    with sm:
        smach.StateMachine.add('DISENGAGE',
                               Disengage(myCom),
                               transitions={'started':'SEARCH',
                                            'killed':'killed'})
        smach.StateMachine.add('SEARCH',
                               Search(myCom),
                               transitions={'foundLanes':'STABLIZE',
                                            'timeout':'DISENGAGE',
                                            'aborted':'DISENGAGE'})
        smach.StateMachine.add('STABLIZE',
                               Stablize(myCom),
                               transitions={'stablized':'ALIGN',
                                            'stablizing':'STABLIZE',
                                            'lost':'SEARCH',
                                            'aborted':'DISENGAGE'})
        smach.StateMachine.add('ALIGN',
                               Align(myCom),
                               transitions={'aligned':'FORWARD',
                                            'aligning':'ALIGN',
                                            'lost':'SEARCH',
                                            'aborted':'DISENGAGE'})
        smach.StateMachine.add('FORWARD',
                               Forward(myCom),
                               transitions={'completed':'DISENGAGE',
                                            'aborted':'DISENGAGE'})

    introServer = smach_ros.IntrospectionServer('mission_server',
                                                sm,
                                                '/MISSION/LANE_MARKER')
    introServer.start()

    sm.execute()
    rospy.signal_shutdown("lane_marker task ended")