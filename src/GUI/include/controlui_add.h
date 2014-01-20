/* 
	controlui_add.cpp
	Header file for Control UI 
	Date created: 9 Jan 2014
	Author: Lynnette
*/

#include <QApplication>
#include <QFileDialog>
#include <QMessageBox>
#include <QImage>
#include <QPixmap>
#include <QDebug>
#include <QLineEdit>
#include <QVector>
#include <QTimer>
#include <QObject>

#include "../src/controlui.h"

#include <ros/ros.h>
#include <std_msgs/String.h>
#include <std_msgs/Float32.h>
#include <std_msgs/Bool.h>

#include <actionlib/client/simple_action_client.h>
#include <actionlib/client/terminal_state.h>
#include <bbauv_msgs/ControllerAction.h>
#include <bbauv_msgs/thruster.h>

#include <stdio.h>
#include <cstdlib>
#include <string.h>
#include <stdlib.h>
#include <iostream>
#include <fstream>
#include <time.h>
#include <boost/algorithm/string/split.hpp>
#include <boost/algorithm/string/classification.hpp>
#include <boost/lexical_cast.hpp>
#include <vector>
#include <sstream>
#include <iomanip>

using namespace std;

string getdate();
void saveFile();
void openTheFile();
void fire();
void enableButton();
void sendButton();
void tuneButton();
void dofSelected(int index);
void mouseMoved(QMouseEvent*);
//Qt UI callbacks
void updateGraph();
