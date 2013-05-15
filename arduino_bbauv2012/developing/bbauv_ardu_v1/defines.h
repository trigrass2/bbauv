#ifndef _DEFINES_H
#define _DEFINES_H

#define ATM 99974 //Pascals or 14.5PSI
#define PSI100 689475
#define PSI30 206842
#define LPF_CONSTANT 0.7
#define PRESSURE_TYPE_ABSOLUTE_100 0
#define PRESSURE_TYPE_GAUGE_30 1
#define WaterPin1 26 // green
#define WaterPin2 25 // yellow
#define WaterPin3 27 // orange
#define waterLedPin 7
#define TempAddr1 0x49 // V+
#define TempAddr2 0x4A	// SDA
#define TempAddr3 0x4B	// SCL
#define ADC_16 0x48 //
#define NORMAL 0
#define DEBUG_BB 1

/*------------Servo Definitions-------------------*/
#define SERVO_1 14
#define SERVO_2 15
#define SERVO_3 16
#define SERVO_4 17
#define SERVO_5 18
#define SERVO_6 19

#endif // _DEFINES_H
