// ENEL 441 - Lab 2 - Closing the loop

// Load libraries to read encoder chips
#include <SPI.h>
#include "LS7366R.h"

// needed to convert bytes to floats
typedef union byteAndFloat{
  byte b[4];
  float f;
};

// class to read and store encoder values
LS7366R codeurs(47, MDR0_CONF, MDR1_CONF);

// Motor driver pins
#define MOTOR_DIRECTION_IN1 48
#define MOTOR_DIRECTION_IN2 46
#define MOTOR_SPEED_ENA 44


// Arduino Setup
void setup() {

  Serial.begin(115200);  
  Serial.setTimeout(0.1);

  pinMode(MOTOR_DIRECTION_IN1,OUTPUT);
  pinMode(MOTOR_DIRECTION_IN2,OUTPUT);
  pinMode(MOTOR_SPEED_ENA,OUTPUT);

  digitalWrite(MOTOR_DIRECTION_IN1,LOW);
  digitalWrite(MOTOR_DIRECTION_IN2,LOW);
  analogWrite(MOTOR_SPEED_ENA,0);
  
  delay(5000);
  Serial.println("Completed Setup.");

}

int N = 1000; // data length
int Ts = 10;  // sample period
byte reference_magnitude[1000];
bool reference_direction[1000];
int diskPosition[1000];
byte tt[1000];
byte msg3[2];  //dummy variable needed to convert data to int
float Kp = 0;  // gain of proportional controller

void loop() {

  // keep sending 'w' until Python noteboook acknowledges the Arduino by sending a 'c'
  while (!Serial.available()){
    Serial.println('w');
    delay(20);
  } 
  char ack = (char) Serial.read();
  //Serial.print("Received: ");
  //Serial.println(ack);
  if (ack == 'c') {
    Serial.println('c');
  }
  else {
    Serial.println("Did not receive correct acknowledgement.");
    Serial.println("Exiting.");
    delay(1000);
    exit(0);    
  }

  // receive the gain of the proportional controller from Python notebook
  Kp = read_float();
  Serial.println(Kp);
  delay(10);

  // receive the reference magnitude from Python notebook
  for (int ii=0; ii<N; ii++){
    while (!Serial.available()) { 
     delay(1);
    }
    reference_magnitude[ii] = Serial.read();
    Serial.write(reference_magnitude[ii]);
  }

  // receive the reference direction from Python notebook
  for (int ii=0; ii<N; ii++){
    while (!Serial.available()) { 
     delay(1);
    }
    reference_direction[ii] = (bool) Serial.read();
    Serial.write( (byte) reference_direction[ii]);
  }

  // variables needed to keep track of sampling period.
  unsigned long start_time = millis();
  unsigned long cur_time = millis();
  int ii = 0;

  // Set motor pins to rotate in the direction specified by the first value of the 
  // reference signal, but with magnitude of 0 (motor won't move yet).
  if (reference_direction[ii] == 1) {      
    digitalWrite(MOTOR_DIRECTION_IN1,HIGH);
    digitalWrite(MOTOR_DIRECTION_IN2,LOW);
  }
  else {
    digitalWrite(MOTOR_DIRECTION_IN1,LOW);
    digitalWrite(MOTOR_DIRECTION_IN2,HIGH);
  }

  // set up array for input applied to motor (it is determined by the controller)
  int reference = 0;
  int u[1000];
  int u_prev = 0;

  // This is the main loop. The loop will cycle through 1000 points. It will execute the 
  // loop and wait so that each pass through the loop is spaced T milliseconds apart.
  // In each pass through the loop, it will: 
  //           1. read the sensor, 
  //           2. calculate the input to apply to the motor, 
  //           3. apply that value to the motor, 
  //           4. send data back to Python.
  while (ii < N) {
    if ( (cur_time - start_time) >= Ts ) {   // sample and load every T milliseconds.
      
      // read disk position
      codeurs.sync();
      diskPosition[ii] = (int)codeurs.encoder1();
      

      // calculate reference signal at current time step
      reference = combine_sign_and_mag(reference_direction[ii],reference_magnitude[ii]);
      
      // convert reference from degrees to increments of 2048. Recall that the encoder 
      // outputs 2048 counts per revolution. So ref_cal_int and diskPosition will now have the 
      // same units.
      float ref_cal = ((float)reference)/360*2048;
      int ref_cal_int = (int)ref_cal;
      
      
      // DON'T CHANGE THE CODE ABOVE THIS POINT.

      // calculate input to apply to the motor 
      // This is the code that you will need to write. The only variables that you need 
      // in your calculation are: 
      //        u[ii] - the input applied to the motor
      //        ref_cal_int - the reference signal, aka desired position as an integer in lines per rotation, 
      //        diskPosition[ii] - the measured disk position in lines per rotation. 
      //        Kp - gain of the proportional controller (when you are implementing a proportional controller), 
      // The line below is the open loop case: the reference
      // is directly applied to the motor.        
      
      // open loop case
      u[ii] = ref_cal_int;

      // bang-bang controller
      // your code here


      // proportional control
      // your code here
      

      // DON'T CHANGE THE CODE BEYOND THIS POINT.
      // the input must be a number between -255 and 255 (8 bit number). 
      // So clip anything outside that range.
      u[ii] = min(u[ii],255);
      u[ii] = max(u[ii],-255);      

      // Apply input to the motor
      analogWrite(MOTOR_SPEED_ENA,abs(u[ii]));
      if (sign(u[ii]) != sign(u_prev)) {  
        if (sign(u[ii]) == 1) {      
          digitalWrite(MOTOR_DIRECTION_IN1,HIGH);
          digitalWrite(MOTOR_DIRECTION_IN2,LOW);
        }
        else {
          digitalWrite(MOTOR_DIRECTION_IN1,LOW);
          digitalWrite(MOTOR_DIRECTION_IN2,HIGH);
        }
      }   
      u_prev = u[ii];
      
      // Send disk position back to Python
      int2bytes(diskPosition[ii], msg3);
      Serial.write(msg3,2);

      // Send input to Python
      int2bytes(u[ii], msg3);
      Serial.write(msg3,2);

      // caluclate time and send to Python
      cur_time = millis();
      tt[ii] = (byte)(cur_time-start_time);

      int2bytes(tt[ii], msg3);
      Serial.write(msg3,2);

      start_time = cur_time;
      ii++;
    }
    else {
      cur_time = millis();
    }
  }

  digitalWrite(MOTOR_DIRECTION_IN1,LOW);
  digitalWrite(MOTOR_DIRECTION_IN2,LOW);
  analogWrite(MOTOR_SPEED_ENA,0);



  delay(5000);
  exit(0);
}
 

void int2bytes(int n, byte* b) {
  int mask = 255; 
  b[0] = (byte) (n & mask);
  b[1] = (byte) ((n >> 8) & mask);
}


int sign(int n) {
  if (n < 0) {
    return -1;
  }
  else {
    return 1;
  }
}

int combine_sign_and_mag(bool ss, byte mm) {
  int nn = 0;
  if (ss == false) {
    nn = -(int)mm;
  }
  else {
    nn = (int)mm;
  }
  return nn;
}

float read_float(void) {
  byteAndFloat received_float;
  for (int ii=0; ii<4; ii++){
    while (!Serial.available()) { 
      delay(1);
    }
    received_float.b[ii] = Serial.read();
    Serial.write(received_float.b[ii]);
  }
  return received_float.f;
}





