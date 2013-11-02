#include <QApplication>
#include <QFileDialog>
#include "auv_gui.h"
#include "ros/ros.h"
#include "std_msgs/String.h"

static Ui::Vision ui;

static void chatterCallback(const std_msgs::String::ConstPtr& msg)
{
	ROS_INFO("I heard: [%s]", msg->data.c_str());
}

static void selectBottomFilter(int selectedIndex){
	ui.bottomfilter->setItemText(selectedIndex,"Hello");
}

static void openFile(){
	//QFileDialog to open file
	QString filename = QFileDialog::getOpenFileName(this, tr("Open bag file"), QDir::currentPath(), 
		tr("Bag files (*.bag);; All files (*.*)")
		0, QFileDialog::DontUseNativeDialog);
	if (!filename.isNull()) { qDebug.toAscii(); }
	//Try to run the bag file from a new terminal in rosrun
	char command[500];
	strcpy(command, "gnome-terminal -e 'bash -c " + "\"" + "rosbag play "  + filename + "; exec bash\"" + "'");
	system(command);
}

int main(int argc, char **argv)
{
	ros::init(argc, argv, "auv_gui");

	//Initiate QAppication and UI
	QApplication app(argc, argv);
	QMainWindow *window = new QMainWindow;
	ui.setupUi(window);
	
	QObject::connect(ui.bottomfilter, static_cast<void (QComboBox::*)(int)>(&QComboBox::currentIndexChanged), selectBottomFilter);
	QObject::connect(ui.actionOpen, static_cast<void(QAction::*)(bool)>(&QAction::triggered), openFile);

	window->show();


	ros::NodeHandle node;
	//Subscribe to a topic "chatter", with queue size 10 and callback chatterCallback
	ros::Subscriber sub = node.subscribe("chatter", 10, chatterCallback);
	return app.exec();
}

