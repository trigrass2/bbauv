#include "ros/ros.h"
#include "std_msgs/Duration.h"
#include "std_msgs/Time.h"
#include "core/TimeElapsed.h"
#include <sstream>

int main(int argc, char **argv)
{
	ros::init(argc, argv, "timer");
	ros::NodeHandle node;
	ros::Publisher timer_publisher = node.advertise<core::TimeElapsed>("timer", 10);
	ros::Duration loopDuration(1);

	ros::Time start_time = ros::Time::now();

	while(ros::ok())
	{
		//Calculate the duration elapsed since this node started
		ros::Duration duration = ros::Time::now() - start_time;
		core::TimeElapsed timeElapsed;
		timeElapsed.secondsElapsed = duration;
		//Publishes the calculated duration
		timer_publisher.publish(timeElapsed);

		ros::spinOnce();

		//Sleeps for 1 second
		loopDuration.sleep();
	}

	return 0;
}