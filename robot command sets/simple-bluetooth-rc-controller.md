# Набор команд, по умолчанию используемый при управлением роботом при помощи программы Bluetooth RC Controller на телефоне

* `'S'`-стоп
* `'F'`-вперёд
* `'B'`-назад
* `'R'`-поворот направо
* `'L'`-поворот налево
* `'I'`-по дуге вперёд вправо
* `'G'`-по дуге вперёд влево
* `'H'`-по дуге назад влево
* `'J'`-по дуге назад вправо
* `'W','w'`-удар ударным механизмом
* `'x','X'`-удар резким движением вперёд-назад
* `'0'..'9'`-выставление уровня скорости

## Пример кода, реализующего этот набор команд

```cpp
#include "DualMC33926MotorShield.h"

DualMC33926MotorShield md;

void setupMotors(){
  md.init();
}

void motors(float _rPower, float _lPower){
  md.setSpeeds(constrain(round(_lPower*400),-400,400),-constrain(round(_rPower*400),-400,400));
}

//********************************************************************

unsigned long lastTime=0;
 
#define STOP_WHEN_KICK

#define SPEED_RANGES 10
float MS_MIN[SPEED_RANGES] = {0, 0.15, 0.20, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9};
float MS_MAX[SPEED_RANGES] = {0, 0.20, 0.35, 0.5, 0.7, 0.8, 0.9, 1.0, 1.0, 1.0};
#define TS_MIN 0.3
#define TS_MAX 0.5
#define DS_MIN 0.1
#define DS_MAX 0.3

int speedRange = 4;

#define MAX_SPEED_TIME 2000

#define KICK_PIN 11

unsigned long prevKick=0;
void kick(){
  if(millis()-prevKick>500){
    digitalWrite(KICK_PIN,HIGH);
    delay(200);
    digitalWrite(KICK_PIN,LOW);
    prevKick=millis();
  }
}

void kick2(){
  if(millis()-prevKick>500){
    motors(1.0,1.0);
    delay(250);
    motors(0,0);
    delay(100);
    motors(-1.0,-1.0);
    delay(250);
    motors(0,0);
    prevKick=millis();
  }
}

  
void setup()
{
  Serial.begin(9600);
  setupMotors();
  pinMode(KICK_PIN,OUTPUT);
}

int prevCmd=0;
unsigned long cmdTime=0;
void checkCmd(int _cmd){
  if((_cmd!=prevCmd) && ((_cmd <'0') || (_cmd>'9'))){
    cmdTime=millis();
    prevCmd=_cmd;
  }
}
  
void loop(){
  if(Serial.available()){
    lastTime=millis();
    int inByte=Serial.read(); 
//    Serial.write(inByte);
     checkCmd(inByte);
     switch (inByte){
      case 'S':
        motors(0,0);
        break;
      case 'F':
        motors(constrain(MS_MIN[speedRange]+(MS_MAX[speedRange]-MS_MIN[speedRange])*(millis()-cmdTime)/MAX_SPEED_TIME,MS_MIN[speedRange],MS_MAX[speedRange]),constrain(MS_MIN[speedRange]+(MS_MAX[speedRange]-MS_MIN[speedRange])*(millis()-cmdTime)/MAX_SPEED_TIME,MS_MIN[speedRange],MS_MAX[speedRange]));
        break;
      case 'B':
        motors(-constrain(MS_MIN[speedRange]+(MS_MAX[speedRange]-MS_MIN[speedRange])*(millis()-cmdTime)/MAX_SPEED_TIME,MS_MIN[speedRange],MS_MAX[speedRange]),-constrain(MS_MIN[speedRange]+(MS_MAX[speedRange]-MS_MIN[speedRange])*(millis()-cmdTime)/MAX_SPEED_TIME,MS_MIN[speedRange],MS_MAX[speedRange]));
        break;
      case 'R':
        motors(-constrain(TS_MIN+(TS_MAX-TS_MIN)*(millis()-cmdTime)/MAX_SPEED_TIME,TS_MIN,TS_MAX),constrain(TS_MIN+(TS_MAX-TS_MIN)*(millis()-cmdTime)/MAX_SPEED_TIME,TS_MIN,TS_MAX));
        break;
      case 'L':
        motors(constrain(TS_MIN+(TS_MAX-TS_MIN)*(millis()-cmdTime)/MAX_SPEED_TIME,TS_MIN,TS_MAX),-constrain(TS_MIN+(TS_MAX-TS_MIN)*(millis()-cmdTime)/MAX_SPEED_TIME,TS_MIN,TS_MAX));
        break;
      case 'I':
        motors(constrain(MS_MIN[speedRange]+(MS_MAX[speedRange]-MS_MIN[speedRange])*(millis()-cmdTime)/MAX_SPEED_TIME,MS_MIN[speedRange],MS_MAX[speedRange])-constrain(DS_MIN+(DS_MAX-DS_MIN)*(millis()-cmdTime)/MAX_SPEED_TIME,DS_MIN,MS_MAX[speedRange]),
               constrain(MS_MIN[speedRange]+(MS_MAX[speedRange]-MS_MIN[speedRange])*(millis()-cmdTime)/MAX_SPEED_TIME,MS_MIN[speedRange],MS_MAX[speedRange])+constrain(DS_MIN+(DS_MAX-DS_MIN)*(millis()-cmdTime)/MAX_SPEED_TIME,DS_MIN,MS_MAX[speedRange]));
        break;
      case 'G':
        motors(constrain(MS_MIN[speedRange]+(MS_MAX[speedRange]-MS_MIN[speedRange])*(millis()-cmdTime)/MAX_SPEED_TIME,MS_MIN[speedRange],MS_MAX[speedRange])+constrain(DS_MIN+(DS_MAX-DS_MIN)*(millis()-cmdTime)/MAX_SPEED_TIME,DS_MIN,MS_MAX[speedRange]),
               constrain(MS_MIN[speedRange]+(MS_MAX[speedRange]-MS_MIN[speedRange])*(millis()-cmdTime)/MAX_SPEED_TIME,MS_MIN[speedRange],MS_MAX[speedRange])-constrain(DS_MIN+(DS_MAX-DS_MIN)*(millis()-cmdTime)/MAX_SPEED_TIME,DS_MIN,MS_MAX[speedRange]));
        break;
      case 'H':
        motors(-constrain(MS_MIN[speedRange]+(MS_MAX[speedRange]-MS_MIN[speedRange])*(millis()-cmdTime)/MAX_SPEED_TIME,MS_MIN[speedRange],MS_MAX[speedRange])+constrain(DS_MIN+(DS_MAX-DS_MIN)*(millis()-cmdTime)/MAX_SPEED_TIME,DS_MIN,MS_MAX[speedRange]),
               -constrain(MS_MIN[speedRange]+(MS_MAX[speedRange]-MS_MIN[speedRange])*(millis()-cmdTime)/MAX_SPEED_TIME,MS_MIN[speedRange],MS_MAX[speedRange])-constrain(DS_MIN+(DS_MAX-DS_MIN)*(millis()-cmdTime)/MAX_SPEED_TIME,DS_MIN,MS_MAX[speedRange]));
        break;
      case 'J':
        motors(-constrain(MS_MIN[speedRange]+(MS_MAX[speedRange]-MS_MIN[speedRange])*(millis()-cmdTime)/MAX_SPEED_TIME,MS_MIN[speedRange],MS_MAX[speedRange])-constrain(DS_MIN+(DS_MAX-DS_MIN)*(millis()-cmdTime)/MAX_SPEED_TIME,DS_MIN,MS_MAX[speedRange]),
               -constrain(MS_MIN[speedRange]+(MS_MAX[speedRange]-MS_MIN[speedRange])*(millis()-cmdTime)/MAX_SPEED_TIME,MS_MIN[speedRange],MS_MAX[speedRange])+constrain(DS_MIN+(DS_MAX-DS_MIN)*(millis()-cmdTime)/MAX_SPEED_TIME,DS_MIN,MS_MAX[speedRange]));
        break;
      case 'W':
        kick();
        break;
      case 'w': 
        kick();
        break;
      case 'x':
        kick2();
        break;
      case 'X': 
        kick2();
        break;
      case '0':
        speedRange=0;
        break;
      case '1':
        speedRange=1;
        break;
      case '2':
        speedRange=2;
        break;
      case '3':
        speedRange=3;
        break;
      case '4':
        speedRange=4;
        break;
      case '5':
        speedRange=5;
        break;
      case '6':
        speedRange=6;
        break;
      case '7':
        speedRange=7;
        break;
      case '8':
        speedRange=8;
        break;
      case '9':
        speedRange=9;
        break;
    }
  }
  if(millis()-lastTime>5000){
    motors(0,0);
  }
//  delay(100);
}
```
