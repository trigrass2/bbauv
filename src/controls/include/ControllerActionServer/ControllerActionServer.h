/*
 * ControllerActionServer.h
 *
 *  Created on: 2013-05-27
 *      Author: gohew
 */

#ifndef CONTROLLERACTIONSERVER_H_
#define CONTROLLERACTIONSERVER_H_
#include <ros/ros.h>
#include <actionlib/server/simple_action_server.h>
#include <bbauv_msgs/ControllerAction.h>


class ControllerActionServer {
public:
	ControllerActionServer(std::string name);
	void updateState(float forward,float sidemove,float forward_vel, float sidemove_vel,float heading,float depth);
	void setDispMode(bool isVelSide, bool isVelFwd);
	void setNavigation(bool nav);
	void executeCB(const bbauv_msgs::ControllerGoalConstPtr &goal);
	float getForward();
	float getSidemove();
	float getHeading();
	float getDepth();
	float getForwardVel();
	float getSidemoveVel();
	virtual ~ControllerActionServer();

private:
	double wrapAngle360(double error, double heading);
	float _forward_input;
	float _sidemove_input;
	float _heading_input;
	float _depth_input;
	float _forward_vel_input;
	float _sidemove_vel_input;
	float _forward_setpoint;
	float _sidemove_setpoint;
	float _heading_setpoint;
	float _depth_setpoint;
	float _inNavigation;
	float MIN_FORWARD;
	float MIN_SIDEMOVE;
	float MIN_HEADING;
	float MIN_FORWARD_VEL;
	float MIN_SIDEMOVE_VEL;
	float MIN_DEPTH;
	bool  isFwdPos;
	bool  isFwdVel;
	bool  isSidePos;
	bool  isSideVel;

protected:

  ros::NodeHandle nh_;
  actionlib::SimpleActionServer<bbauv_msgs::ControllerAction> as_;
  std::string action_name_;
  int data_count_;
  float sum_, sum_sq_;
  bbauv_msgs::ControllerGoal goal_;
  bbauv_msgs::ControllerFeedback feedback_;
  bbauv_msgs::ControllerResult result_;
};

#endif /* CONTROLLERACTIONSERVER_H_ */
