import rospy

from bbauv_msgs.msg import manipulator

from vision import BinsVision
from bot_common.bot_comms import GenericComms

class Comms(GenericComms):
    """ Class to facilitate communication b/w ROS and task submodules """

    def __init__(self):
        GenericComms.__init__(self, BinsVision(self))
        self.defaultDepth = 3.0

        #TODO: Communicate with mission planner

    def handleSrv(self, data):
        pass

    def drop(self):
        maniPub = rospy.Publisher("/manipulators", manipulator)
        maniPub.publish(0 | 8)

def main():
    testCom = Comms()
