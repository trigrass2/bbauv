#!/usr/bin/env python2

import roslib; roslib.load_manifest('mission_planner')
import rospy
from bbauv_msgs.srv import *
from bbauv_msgs.msg import *
from move_base_msgs.msg import MoveBaseAction, MoveBaseGoal
from tf.transformations import quaternion_from_euler, quaternion_about_axis
import dynamic_reconfigure.client
from math import pi
import subprocess

import actionlib
import smach
import smach_ros
import bbauv_msgs
import bbauv_msgs.msg
from nav_msgs.msg import Odometry
from bbauv_msgs.msg import depth
from bbauv_msgs.msg import imu_data

class Countdown(smach.State):
    def __init__(self, sleep=1.0):
        smach.State.__init__(self, outcomes=['succeeded'])
        self.sleep_time = sleep
    
    def execute(self, userdata):
        
        #This is to allow enough time for ethernet cable to be removed
        rospy.loginfo("Going for COUNTDOWN")        
        r = rospy.Rate(1)
        start_time = rospy.get_time()
        while (rospy.get_time() - start_time) < self.sleep_time:
            r.sleep()
            rospy.loginfo("%d Elapsed" % (rospy.get_time() - start_time))
        subproces.call(['./bbauv_workspace/bbauv/ros_bbauv2012/Scripts/bag-it-autonomously'])
        rospy.loginfo('Beginning to log')
        return 'succeeded'        

class Start(smach.State):
    def __init__(self, timeout, start_depth, start_heading):
        smach.State.__init__(self, outcomes=['start_complete'])
        self.name = self.__class__.__name__
        self.timeout = timeout                
        self.start_depth = start_depth
        self.start_heading = start_heading        
                
    def execute(self,userdata):
#        return 'start_complete'
        global locomotionGoal
        global locomotion_client
        global set_ConPIDMode
        rospy.loginfo('Executing state START')

        #Setting PID (Fwd? Side? Head? Depth? Pitch?) and modes (Topside? Nav?)
        try:
            resp = set_ConPIDMode(True, True, True, True, True, False, False)
            rospy.loginfo("PID and Mode is set")
        except rospy.ServiceException, e:
            rospy.loginfo("PID and Mode NOT set: %s" % e)
        
        #Key in starting position here
        goal = bbauv_msgs.msg.ControllerGoal(forward_setpoint=0, sidemove_setpoint=0,
                                            depth_setpoint= self.start_depth, 
                                            heading_setpoint = self.start_heading                                            
                                            )
        
        #Reset DVL and Earth Odom here
        drClient_DVL = dynamic_reconfigure.client.Client("WH_DVL")
        drClient_DVL.update_configuration({"zero_distance":True})
        drClient_Earth = dynamic_reconfigure.client.Client("earth_odom")
        drClient_Earth.update_configuration({"zero_distance":True})        
                
        locomotion_client.send_goal(goal)
        locomotion_client.wait_for_result(rospy.Duration(self.timeout,0))
        rospy.loginfo("Dive Dive Dive!")
        
        locomotionGoal.depth_setpoint = self.start_depth
        locomotionGoal.heading_setpoint = self.start_heading
        locomotionGoal.sidemove_setpoint = 0
        locomotionGoal.forward_setpoint = 0
        return 'start_complete'

class GoToDepth(smach.State):
    def __init__(self, timeout=3, depth=None, surface=False):
        smach.State.__init__(self, outcomes=['depth_complete'])
        self.depth = depth
        self.timeout = timeout
        self.surface = surface
        
    def execute(self,userdata):
        global locomotionGoal
        global locomotion_client

        if self.depth == None:
            if locomotionGoal.depth_setpoint > 0 :
                self.depth = locomotionGoal.depth_setpoint
            if locomotionGoal.depth_setpoint <=0:
                if self.surface == True:
                    self.depth = locomotionGoal.depth_setpoint
                if self.surface == False:
                    self.depth = 0.5
                    rospy.loginfo('Trying to surface PREMATURELY! Depth constrained to 0.5 meters')
        
        #seed goal
        goal = bbauv_msgs.msg.ControllerGoal(forward_setpoint=0,
                                            sidemove_setpoint=0,
                                            depth_setpoint=self.depth,
                                            heading_setpoint=locomotionGoal.heading_setpoint)
        rospy.loginfo('Going to depth %2.5f' % self.depth)
        locomotion_client.send_goal(goal)
        locomotion_client.wait_for_result(rospy.Duration(self.timeout,0))
        
        #Updating locomotionGoal
        locomotionGoal.depth_setpoint = goal.depth_setpoint        
        return 'depth_complete'

class GoToHeading(smach.State):
    def __init__(self, timeout=3, heading=None):
        smach.State.__init__(self, outcomes=['heading_complete'])
        self.heading = heading
        self.timeout = timeout
        
    def execute(self,userdata):
        global locomotionGoal
        global locomotion_client
        
        if self.heading == None:
            self.heading = locomotionGoal.heading_setpoint
        
        goal = bbauv_msgs.msg.ControllerGoal(forward_setpoint=0,
                                            sidemove_setpoint=0,
                                            depth_setpoint=locomotionGoal.depth_setpoint,
                                            heading_setpoint=self.heading)

        rospy.loginfo('Going to heading %2.5f' % self.heading)                                            
        locomotion_client.send_goal(goal)
        locomotion_client.wait_for_result(rospy.Duration(self.timeout,0))
        
        #Updating locomotionGoal
        locomotionGoal.heading_setpoint = goal.heading_setpoint      
        return 'heading_complete'

#class Hover(smach.State):

class StoreGlobalCoord(smach.State):
    def __init__(self, task_name):
        smach.State.__init__(self, outcomes=['store_complete'])
        self.name = self.__class__.__name__ 
        self.task_name = task_name
        self.x = None
        self.y = None
        self.depth = None
        self.heading = None
        
    def odomCallback(self, msg):
        self.x =  msg.pose.pose.position.x
        self.y = msg.pose.pose.position.y
                
    def depthCallback(self, msg):
        self.depth = msg.depth
        
    def AHRSCallback(self,msg):
        self.heading = msg.orientation.z * (180/pi)
    
    def execute(self, userdata):
        
        odom_sub = rospy.Subscriber('/earth_odom', Odometry, self.odomCallback)
        depth_sub = rospy.Subscriber('/depth', depth, self.depthCallback)
        AHRS_sub = rospy.Subscriber('/AHRS8_data_e', imu_data, self.AHRSCallback)
        
        rospy.sleep(2)
        rospy.loginfo('x=%2.5f y=%2.5f depth=%2.5f heading=%2.5f' % (self.x, self.y, self.depth, self.heading))
        rospy.set_param(self.task_name+'/x', self.x)
        rospy.set_param(self.task_name+'/y', self.y)
        rospy.set_param(self.task_name+'/depth', self.depth)
        rospy.set_param(self.task_name+'/heading', self.heading)
    
        odom_sub.unregister()
        depth_sub.unregister()
        AHRS_sub.unregister()
        
        return 'store_complete'
        
class LinearSearch(smach.State):
    def __init__(self, task_name, timeout, distance, direction, attempts, use_left=False, num_lanes=0, start_depth=None, start_heading=None):
        smach.State.__init__(self, outcomes=['linear_complete','failed','attempts_none'], input_keys=['attempt_counter'], output_keys=['attempt_counter'])
        self.name = self.__class__.__name__
        self.task_name = task_name
        self.timeout = timeout        
        self.task_srv_name = task_name + '_srv'
        self.task_srv = None
        self.distance = distance
        self.direction = direction
        self.attempts = attempts
        self.use_left = use_left
        self.num_lanes = num_lanes
        self.start_depth = start_depth
        self.start_heading = start_heading
                   
    def execute(self, userdata):
#        return 'linear_complete'
        global locomotionGoal
        global locomotion_client
        global set_ConPIDMode
        global lane_srv
        global isSearchDone
        isSearchDone = False
        
        rospy.loginfo("Entering %s %s state" % (self.task_name, self.name))  
        
        if userdata.attempt_counter > self.attempts:
            return 'attempts_none'
        if userdata.attempt_counter <= self.attempts:
            userdata.attempt_counter += 1

        #Setting PID (Fwd? Side? Head? Depth? Pitch?) and modes (Topside? Nav?)
        try:
            resp = set_ConPIDMode(True, True, True, True, True, False, False)
            rospy.loginfo("PID and Mode is set")
        except rospy.ServiceException, e:
            rospy.loginfo("PID and Mode NOT set: %s" % e)
        
        #connecting to task server            
        if self.task_name != 'lane':
            rospy.wait_for_service(self.task_srv_name)   
            self.task_srv = rospy.ServiceProxy(self.task_srv_name, mission_to_vision)
            rospy.loginfo('Mission Connected to %s Server' % self.task_name)
        
        #Seeding goal
        goal = bbauv_msgs.msg.ControllerGoal()
        if self.start_heading == None: goal.heading_setpoint = locomotionGoal.heading_setpoint
        if self.start_heading != None: goal.heading_setpoint = locomotionGoal.heading_setpoint = self.start_heading
        if self.start_depth == None: goal.depth_setpoint = locomotionGoal.depth_setpoint
        if self.start_depth != None: goal.depth_setpoint = locomotionGoal.depth_setpoint = self.start_depth
        rospy.logdebug("start_heading = %2.5f, start_depth = %2.5f" % (goal.heading_setpoint, goal.depth_setpoint))
                
        #Begin Searching For Task
        if self.task_name == 'lane':
            try:
                resp = lane_srv(True,locomotionGoal,self.use_left,self.num_lanes,False)
            except rospy.ServiceException, e:
                rospy.loginfo("Failed to start Search" % e)  
        if self.task_name != 'lane':
            try:
                resp = self.task_srv(True, locomotionGoal, False)
                rospy.loginfo("Searching for %s" % self.task_name)
            except rospy.ServiceException, e:
                rospy.loginfo("Failed to start Search" % e)  
   
        r = rospy.Rate(30)
        start_time = rospy.get_time()
        rospy.loginfo("Moving Fwd to search for %s" % self.task_name)
        while (not rospy.is_shutdown()) and ((rospy.get_time()-start_time) <= self.timeout):
            if not isSearchDone:
                #Implement callback method?
                if self.direction == 'fwd':
                    goal.forward_setpoint = self.distance
                    goal.sidemove_setpoint = 0
                    locomotion_client.send_goal(goal)
                    locomotion_client.wait_for_result(rospy.Duration(2,0))        
                if self.direction == 'sway':
                    goal.forward_setpoint = 0
                    goal.sidemove_setpoint = self.distance
                    locomotion_client.send_goal(goal)
                    locomotion_client.wait_for_result(rospy.Duration(2,0))        
                                    
            if isSearchDone:                
                rospy.loginfo("Found %s. %d of %d secs elapsed" % (self.task_name, rospy.get_time()-start_time, self.timeout))
                return 'linear_complete'
            r.sleep()
        
        #Timed out
        if self.task_name == 'lane':
            try:
                rospy.loginfo('Failed to find %s' % self.task_name)
                resp = lane_srv(False, None, None, None, True)            
                return 'failed'              
            except rospy.ServiceException, e:
                rospy.loginfo("Failed to abort: %s" % e)            
        if self.task_name != 'lane':
            try:
                rospy.loginfo('Failed to find %s' % self.task_name)
                resp = self.task_srv(False, None, True)            
                return 'failed'              
            except rospy.ServiceException, e:
                rospy.loginfo("Failed to abort: %s" % e)
        
class WaitOut(smach.State):
    def __init__(self, task_name, timeout):
        smach.State.__init__(self, outcomes=['task_complete','failed'])
        self.name = self.__class__.__name__ 
        self.task_name = task_name
        self.task_srv_name = task_name + '_srv'
        self.task_srv = None
        self.timeout = timeout    
        
    def execute(self, userdata):
#        return 'task_complete'
        global lane_srv
        global isTaskComplete
        global locomotion_client
        global locomotionGoal
        isTaskComplete = False        
        rospy.loginfo("Entering %s %s state" % (self.task_name, self.name))  
        
        #connecting to task server
        rospy.wait_for_service(self.task_srv_name)   
        self.task_srv = rospy.ServiceProxy(self.task_srv_name, mission_to_vision)
        rospy.loginfo('Mission Connected to %s Server' % self.task_name)        
        
        #Waiting Out
        r = rospy.Rate(0.5)
        start_time = rospy.get_time()
        rospy.loginfo("^%s: Found. Task Controlling Vehicle" % (self.task_name))
        while (not rospy.is_shutdown()) and ((rospy.get_time()-start_time) <= self.timeout):
            if isTaskComplete:
                rospy.loginfo("Completed %s. %d of %d secs elapsed" % (self.task_name, rospy.get_time()-start_time, self.timeout))
                if self.task_name == 'lane':
                    goal = bbauv_msgs.msg.ControllerGoal(forward_setpoint=0,sidemove_setpoint=0,depth_setpoint=locomotionGoal.depth_setpoint,heading_setpoint=locomotionGoal.heading_setpoint)
                    locomotion_client.send_goal(goal)
                    locomotion_client.wait_for_result(rospy.Duration(5,0))
                    return 'task_complete'
            r.sleep()
            
        if self.task_name == 'lane':
            try:
                rospy.loginfo('Failed to complete %s' % self.task_name)
#                resp = self.task_srv(False, None, None, None,True)            
                return 'failed'              
            except rospy.ServiceException, e:
                rospy.loginfo("Failed to abort: %s" % e)            
        if self.task_name != 'lane':
            try:
                rospy.loginfo('Failed to complete %s' % self.task_name)
                resp = self.task_srv(False, None, True)            
                return 'failed'              
            except rospy.ServiceException, e:
                rospy.loginfo("Failed to abort: %s" % e)            
        return 'failed'                    

class NavMoveBase(smach.State):
    def __init__ (self, prep_timeout, nav_timeout, x=0, y=0, depth = 0.5, start_heading=0, place= None): #yaw here is BBAUV's controller convention'
        smach.State.__init__(self, outcomes=['nav_complete','failed'])
        self.name = self.__class__.__name__
        self.x = x
        self.y = y
        self.start_heading = start_heading
        self.depth = depth
        self.place = place
        self.prep_timeout = prep_timeout    
        self.nav_timeout = nav_timeout    
        
    def execute (self, userdata):
        global movebase_client
        global locomotion_client
        global locomotionGoal
        global set_ConPIDMode
        movebaseGoal = MoveBaseGoal()
        
        #Check is need to get cooridnate from param server; if place is not None but a string, use string to query param server for nav coords; if place is None, use x,y and yaw            
        if self.place != None:        
            self.x = rospy.get_param(self.place + '/x')
            self.y = rospy.get_param(self.place + '/y')
            self.depth = rospy.get_param(self.place + '/depth')
            self.start_heading = rospy.get_param(self.place + '/heading')

        #Change Depth and Face Heading First
        goal = bbauv_msgs.msg.ControllerGoal(forward_setpoint=0,sidemove_setpoint=0,depth_setpoint=self.depth,heading_setpoint=self.start_heading)

        locomotion_client.send_goal(goal)
        rospy.loginfo('Going to depth %2.5f m. Facing yaw=%2.5f deg' % (self.depth, self.start_heading))
        locomotion_client.wait_for_result(rospy.Duration(self.prep_timeout,0))

        #convert yaw to move_base convention
        rospy.loginfo("start_heading is =%2.5f radians" % self.start_heading)          
        x,y,z,w = quaternion_from_euler(0,0,self.start_heading * (pi/180)) #input must be radians
        rospy.logdebug('z= %2.5f w= %2.5f' % (z,w))

        #Setting PID (Fwd? Side? Head? Depth? Pitch?) and modes (Topside? Nav?)
        try:
            resp = set_ConPIDMode(True, True, True, True, True, False, True)
            rospy.loginfo("PID and Mode is set")
        except rospy.ServiceException, e:
            rospy.loginfo("PID and Mode NOT set: %s" % e)
                        
        #Execute Nav
        movebaseGoal.target_pose.header.frame_id = 'map'
        movebaseGoal.target_pose.header.stamp = rospy.Time.now()
        movebaseGoal.target_pose.pose.position.x = -1 * self.x
        movebaseGoal.target_pose.pose.position.y = self.y 
        movebaseGoal.target_pose.pose.orientation.x = 0
        movebaseGoal.target_pose.pose.orientation.y = 0
        movebaseGoal.target_pose.pose.orientation.z = z
        movebaseGoal.target_pose.pose.orientation.w = w
        
        movebase_client.send_goal(movebaseGoal)
        rospy.loginfo('Going to x=%2.5f y=%2.5f. Facing yaw=%2.5f' % (self.x, self.y, self.start_heading))
        movebase_client.wait_for_result(rospy.Duration(self.nav_timeout,0))

        #Setting PID (Fwd? Side? Head? Depth? Pitch?) and modes (Topside? Nav?)
        try:
            resp = set_ConPIDMode(True, True, True, True, True, False, False)
            rospy.loginfo("PID and Mode is set")
        except rospy.ServiceException, e:
            rospy.loginfo("PID and Mode NOT set: %s" % e)
            
        goal.depth_setpoint = self.depth
        goal.heading_setpoint = self.start_heading
        locomotion_client.send_goal(goal)
        rospy.loginfo('Going to depth %2.5f. Facing yaw=%2.5f' % (self.depth, self.start_heading))
        locomotion_client.wait_for_result(rospy.Duration(self.prep_timeout,0))
        rospy.loginfo('Reached depth %2.5f. Facing yaw=%2.5f' % (self.depth, self.start_heading))            
        
        locomotionGoal.depth_setpoint = self.depth
        locomotionGoal.heading_setpoint = self.start_heading
        return 'nav_complete'
     
def handle_srv(req):
    global locomotionGoal
    global isSearchDone
    global isTaskComplete
    
    #Search completion request from Vision Node.
    if(req.search_request):
        isSearchDone = True
        rospy.logdebug("Search complete")
        return vision_to_missionResponse(True,False)
    
    #Task completion request from Vision Node.
    if(req.task_complete_request):
        rospy.logdebug("Task complete")
        locomotionGoal = req.task_complete_ctrl 
        isTaskComplete = True
        #Controller
        return vision_to_missionResponse(False,True)   

locomotion_client = None
locomotionGoal = controller()
movebase_client = None
set_ConPIDMode = None

mission_server = None
isSearchDone = False
isTaskComplete = False
lane_srv = None

if __name__ == '__main__':
    rospy.init_node('Mission_planner', log_level=rospy.INFO, anonymous=True)
    
    mission_server = rospy.Service('mission_srv', vision_to_mission, handle_srv)
    rospy.loginfo('MissionServer Initialized!')
    
    #Service Client for Lane; Lane task is the only task that will not be shutdown
    rospy.loginfo('Waiting for LaneServer to start up...')
    rospy.wait_for_service('lane_srv')
    lane_srv = rospy.ServiceProxy('lane_srv', mission_to_lane)
    rospy.loginfo('Mission Connected to LaneServer')
    
    # Action Client for PIDs
#     locomotion_client = actionlib.SimpleActionClient('LocomotionServer', bbauv_msgs.msg.ControllerAction)
#     locomotion_client.wait_for_server()
#     rospy.loginfo("Mission connected to LocomotionServer")
    
    #Service Client for PID & Modes
    rospy.loginfo('Waiting for Set Controller Service to start up...')
#     rospy.wait_for_service('set_controller_srv')
#     set_ConPIDMode = rospy.ServiceProxy('set_controller_srv', set_controller)
#     rospy.loginfo('Mission Connected to Set Controller Service')
    
    # Action Client for Move Base
#     movebase_client = actionlib.SimpleActionClient("move_base", MoveBaseAction)
#     movebase_client.wait_for_server()
#     rospy.loginfo("Mission connected to MovebaseServer")
    
    sm_mission = smach.StateMachine(outcomes=['mission_complete','mission_failed'])

    with sm_mission:
        smach.StateMachine.add('COUNTDOWN', Countdown(700), transitions={'succeeded':'START'})
        smach.StateMachine.add('START',Start(2,0.2,55),
                                transitions={'start_complete':'NAV_TO_GATE'})
                               
#        gate = smach.StateMachine(outcomes=['gate_complete', 'gate_failed'])
#        with gate:
#            smach.StateMachine.add('GATE_LinearSearch', LinearSearch('gate', 120), transitions={'linear_complete':'GATE_WAITOUT', 'failed':'gate_failed'})
#            smach.StateMachine.add('GATE_WAITOUT', WaitOut('gate', 60), transitions={'task_complete':'gate_complete', 'failed':'gate_failed'})
#        smach.StateMachine.add('GATE', gate, transitions={'gate_complete':'mission_complete', 'gate_failed':'mission_failed'})

        smach.StateMachine.add('NAV_TO_GATE', NavMoveBase(3,30,6.3,9,0.5,55), transitions={'nav_complete':'LANE_GATE_TASK', 'failed':'HOME'})
        
        lane_gate = smach.StateMachine(outcomes=['lane_complete', 'lane_failed'])
        with lane_gate:
            smach.StateMachine.add('LANE_SEARCH', LinearSearch('lane', 10, 1, 'fwd', 8, False, 1), transitions={'linear_complete':'LANE_STORE', 'failed':'LANE_SEARCH2','attempts_none':'lane_failed'}, remapping={'attempt_counter':'lane1_searchAttempts'})
            smach.StateMachine.add('LANE_SEARCH2', LinearSearch('lane', 10, -1, 'sway', 8, False, 1), transitions={'linear_complete':'LANE_STORE', 'failed':'LANE_SEARCH3','attempts_none':'lane_failed'}, remapping={'attempt_counter':'lane1_searchAttempts'})
            smach.StateMachine.add('LANE_SEARCH3', LinearSearch('lane', 10, -1, 'fwd', 8, False, 1), transitions={'linear_complete':'LANE_STORE', 'failed':'LANE_SEARCH4','attempts_none':'lane_failed'}, remapping={'attempt_counter':'lane1_searchAttempts'})
            smach.StateMachine.add('LANE_SEARCH4', LinearSearch('lane', 10, 1, 'sway', 8, False, 1), transitions={'linear_complete':'LANE_STORE', 'failed':'LANE_SEARCH','attempts_none':'lane_failed'}, remapping={'attempt_counter':'lane1_searchAttempts'})
            smach.StateMachine.add('LANE_STORE', StoreGlobalCoord('lane1'), transitions={'store_complete':'LANE_GATE'})
            smach.StateMachine.add('LANE_GATE', WaitOut('lane', 60), transitions={'task_complete':'LANE_HEADINGCHANGE', 'failed':'lane_failed'})
            smach.StateMachine.add('LANE_HEADINGCHANGE', GoToHeading(3), transitions={'heading_complete':'lane_complete'})
        smach.StateMachine.add('LANE_GATE_TASK', lane_gate, transitions={'lane_complete':'PARK_TASK', 'lane_failed':'HOME'})        

        park = smach.StateMachine(outcomes=['park_complete', 'park_failed'])
        with park:
            smach.StateMachine.add('PARK_DEPTHCHANGE', GoToDepth(3,2), transitions={'depth_complete':'PARK_SEARCH'})
            smach.StateMachine.add('PARK_SEARCH', LinearSearch('park', 30, 1, 'fwd', 2), transitions={'linear_complete':'PARK_STORE', 'failed':'PARK_TO_LANE1','attempts_none':'park_failed'}, remapping={'attempt_counter':'park1_searchAttempts'})
            smach.StateMachine.add('PARK_TO_LANE1', NavMoveBase(1,30,place='lane1'), transitions={'nav_complete':'PARK_DEPTHCHANGE', 'failed':'park_failed'})
            smach.StateMachine.add('PARK_STORE', StoreGlobalCoord('park1'), transitions={'store_complete':'PARK'})            
            smach.StateMachine.add('PARK', WaitOut('park', 60), transitions={'task_complete':'park_complete', 'failed':'park_failed'})
        smach.StateMachine.add('PARK_TASK', park, transitions={'park_complete':'BACK_TO_LANE1', 'park_failed':'BACK_TO_LANE1'})
        
        smach.StateMachine.add('BACK_TO_LANE1', NavMoveBase(1,30,place='lane1'), transitions={'nav_complete':'HOME', 'failed':'mission_failed'})
        smach.StateMachine.add('HOME', NavMoveBase(1,50,0,0,0.5,55), transitions={'nav_complete':'SURFACE', 'failed':'mission_failed'})
        smach.StateMachine.add('SURFACE', GoToDepth(3,0), transitions={'depth_complete':'mission_complete'})

    # Create and start the introspection server
    sis = smach_ros.IntrospectionServer('mission_server', sm_mission, '/MISSION')
    sis.start()
    
    park.userdata.park1_searchAttempts = 0
    lane_gate.userdata.lane1_searchAttempts = 0

    try:
        outcome = sm_mission.execute()
        rospy.spin()
    except KeyboardInterrupt:
        print "Shutting down"

########################
