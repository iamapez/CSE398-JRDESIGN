//import the library in the sketch 
#include <SharpIR.h> 
#include <Servo.h>

SharpIR front( SharpIR::GP2Y0A41SK0F, A0 ); 
SharpIR back( SharpIR::GP2Y0A41SK0F, A1 ); 
Servo motor;
int state = 0;

void setup() {
  // put your setup code here, to run once:
  Serial.begin( 9600 ); //Enable the serial comunication 
  motor.attach(9); //enable pin D9 for pwm signal in Servo Motor
}

void loop() {
  // put your main code here, to run repeatedly:
  String data;
  if (Serial.available() > 0) {
    data = Serial.readStringUntil('\n');
    //Serial.println(data);
  }
  if (data == "opengate" && state != 1){
    state = 1;
    openGate();
    Serial.println("inside open gate if");
  }
  if (data == "closegate" && state == 1){
    state = 0;
    closeGate();
    Serial.println("inside close gate if");
  }

  int frontDist = front.getDistance();
  int backDist = back.getDistance();
  
  if(frontDist > 3 && frontDist < 6){
    Serial.println("frontsensoractive");
    delay(1000);
    }
  
  if(backDist > 3 && backDist < 6){
    Serial.println("rearsensoractive");
    delay(1000);
   }
 
  
}

void openGate() {
  motor.write(0);
}

void closeGate() {
  motor.write(90);
}
