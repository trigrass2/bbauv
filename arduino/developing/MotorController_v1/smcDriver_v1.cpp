#include <Arduino.h>
#include <SoftwareSerial.h>
#include "smcDriver.h"

smcDriver::smcDriver(int _rxPin, int _txPin): smcSerial(SoftwareSerial(_rxPin,_txPin))
{
  CRC7_POLY = 0x91;
  _thrusterRatio[0]=1;
  _thrusterRatio[1]=1;
  _thrusterRatio[2]=1;
  _thrusterRatio[3]=1;
  _thrusterRatio[4]=1;
  _thrusterRatio[5]=1;

}

void smcDriver::init()
{
  smcSerial.begin(19200);
  smcDriver::buildCRCTable();
  delay(5);
  
  exitSafeStart(1);
  exitSafeStart(2);
  exitSafeStart(3);
  exitSafeStart(4);
  exitSafeStart(5);
  exitSafeStart(6); 
}

//motorcontroller handling code!
//----------------------------------------------
void smcDriver::sendCommand(unsigned char message[], unsigned char length)
{
  unsigned char i=0;
  
  for(i=0;i<length;i++)
    smcSerial.write(message[i]);
}

// required to allow motors to move
// must be called when controller restarts and after any error
void smcDriver::exitSafeStart(uint8_t id)
{
  unsigned char message[4] = {0xAA,0x00,0x03};
  
  switch(id)
  {
    case 1: message[1]=0x01;
            break;
    case 2: message[1]=0x02;
            break;
    case 3: message[1]=0x03;
            break;
    case 4: message[1]=0x04;
            break;
    case 5: message[1]=0x05;
            break;
    case 6: message[1]=0x06;
            break;
  }
  smcDriver::sendCommand(message,3);
}
 
// speed should be a number from -3200 to 3200
void smcDriver::setMotorSpeed(uint8_t id, int speed)
{
  unsigned char speedmsg[6]={0xAA,0x00,0x06,0x00,0x00};
  //by default: motor reverse (0x06)
  
  switch(id)
  {
    case 1: speedmsg[1]=0x01;
            break;
    case 2: speedmsg[1]=0x02;
            break;
    case 3: speedmsg[1]=0x03;
            break;
    case 4: speedmsg[1]=0x04;
            break;
    case 5: speedmsg[1]=0x05;
            break;
    case 6: speedmsg[1]=0x06;
            break;
  }
  speed *= _thrusterRatio[id-1];
  if (speed < 0)
  {
    speed = -speed;  // make speed positive
  }
  else
  {
    speedmsg[2]=0x05; //change from reverse to forward
  }
  
  speedmsg[3]=speed&0x1F;
  speedmsg[4]=speed>>5;
  sendCommand(speedmsg,5);
}

void smcDriver::setThrusterRatio(float ratio[])
{
  _thrusterRatio[0]=ratio[0];
  _thrusterRatio[1]=ratio[1];
  _thrusterRatio[2]=ratio[2];
  _thrusterRatio[3]=ratio[3];
  _thrusterRatio[4]=ratio[4];
  _thrusterRatio[5]=ratio[5];
}
