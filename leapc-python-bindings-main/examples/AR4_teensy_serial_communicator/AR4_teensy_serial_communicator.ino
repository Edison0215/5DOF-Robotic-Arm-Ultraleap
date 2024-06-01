/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//Library Declaration
/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#include <PWMServo.h>
#include <AccelStepper.h> 

/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//Motor Pin Definition
/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
const int J1stepPin = 0;  //motor X
const int J1dirPin = 1;   //motor X
const int J2stepPin = 2;  //motor Z
const int J2dirPin = 3;   //motor Z
const int J3stepPin = 4;  //motor Y
const int J3dirPin = 5;   //motor Y
const int J4stepPin = 6;  //motor Arm
const int J4dirPin = 7;   //motor Arm
const int J5stepPin = 8;  //motor Wrist
const int J5dirPin = 9;   //motor Wrist
const int J6stepPin = 10; //unused motor
const int J6dirPin = 11;  //unused motor
const int J7stepPin = 12; //unused motor
const int J7dirPin = 13;  //unused motor
const int J8stepPin = 32; //unused motor
const int J8dirPin = 33;  //unused motor
const int J9stepPin = 34; //unused motor
const int J9dirPin = 35;  //unused motor
const int servoPin = 36;  //motor Clamp

/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//Limit Switch Definition
/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
const int switch1 = 26; 
const int switch2 = 27;
const int switch3 = 28;
const int switch4 = 29;
const int switch5 = 30;
const int switch6 = 31; //unused switch
const int switch8 = 37; //unused switch
const int switch9 = 38; //unused switch
int limit1 = 0;
int limit2 = 0;
int limit3 = 0;
int limit4 = 0;
int limit5 = 0;

/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//Coordination Data Variables
/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
long receivedStep1 = 0;
long receivedStep2 = 0;
long receivedStep3 = 0;
long receivedStep4 = 0;
long receivedStep5 = 0;
long receivedClamp = 0;

int rotation_value1 = 0;
int rotation_value2= 0;
int rotation_value3 = 0;
int rotation_value4 = 0;
int rotation_value5 = 0;
int rotation_clamp = 0;
long initial_homing = 1;

/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//Serial Input Receivers
/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
char receivedCommand;             
const byte numChars = 200;        // data size of serial input
char receivedChars[numChars];
char tempChars[numChars];         // temporary array for use when parsing
bool newData, runallowed = false; // booleans for new data from serial, and runallowed flag

/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//Motor Driver Definition
/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
AccelStepper stepper1(AccelStepper::DRIVER, J1stepPin, J1dirPin);
AccelStepper stepper2(AccelStepper::DRIVER, J2stepPin, J2dirPin);
AccelStepper stepper3(AccelStepper::DRIVER,J3stepPin, J3dirPin);
AccelStepper stepper4(AccelStepper::DRIVER, J4stepPin, J4dirPin);
AccelStepper stepper5(AccelStepper::DRIVER, J5stepPin, J5dirPin);
PWMServo servo;

/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//Setup Function
/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
void setup()
{
  //set limit switch pin as input
  pinMode(switch1, INPUT);
  pinMode(switch2, INPUT);
  pinMode(switch3, INPUT);
  pinMode(switch4, INPUT);
  pinMode(switch5, INPUT);

  //set minimum pulse width for each stepper motor
  stepper1.setMinPulseWidth(10);
  stepper2.setMinPulseWidth(10);
  stepper3.setMinPulseWidth(10);
  stepper4.setMinPulseWidth(10);
  stepper5.setMinPulseWidth(10);

  //define servo pin
  servo.attach(servoPin);

  //define baud rate
  Serial.begin(9600);

  //define speed and acceleration for each stepper motor
  //SPEED = Steps / second
  //ACCELERATION = Steps /(second)^2
  stepper1.setMaxSpeed(4000);
  stepper1.setAcceleration(3800);
  stepper2.setMaxSpeed(2000);
  stepper2.setAcceleration(1800);
  stepper3.setMaxSpeed(2000);
  stepper3.setAcceleration(1800);
  stepper4.setMaxSpeed(2000);
  stepper4.setAcceleration(1800);
  stepper5.setMaxSpeed(2000);
  stepper5.setAcceleration(1800); 

  //check whether limit switch is pressed
  limit1 = digitalRead(switch1);
  limit2 = digitalRead(switch2); //<x,z,y,w>
  limit3 = digitalRead(switch3);
  limit4 = digitalRead(switch4);
  limit5 = digitalRead(switch5);

  //move motor Wrist to inital point
  while (limit5 == 0){
    stepper5.moveTo(initial_homing); 
    initial_homing++;
    stepper5.run();
    delay(1);
    limit5 = digitalRead(switch5);
  }

  //move motor Z to inital point
  initial_homing = 1;
  while (limit2 == 0){
    stepper2.moveTo(initial_homing); 
    initial_homing++;
    stepper2.run();
    delay(1);
    limit2 = digitalRead(switch2);
  }

  //move motor Arm to inital point
  initial_homing = -1;
  while (limit4 == 0){
    stepper4.moveTo(initial_homing); 
    initial_homing--;
    stepper4.run();
    delay(1);
    limit4 = digitalRead(switch4);
  }

  //move motor Y to inital point
  initial_homing = -1;
  while (limit3 == 0){
    stepper3.moveTo(initial_homing); 
    initial_homing--;
    stepper3.run();
    delay(1);
    limit3 = digitalRead(switch3);
  }

  //move motor X to inital point
  initial_homing =- 1;
  while (limit1 == 0){
    stepper1.moveTo(initial_homing); 
    initial_homing--;
    stepper1.run();
    delay(1);
    limit1 = digitalRead(switch1);
  }

  //set current position for each motor as 0 (setup mode)
  stepper1.setCurrentPosition(0);
  stepper1.disableOutputs(); //disable outputs
  stepper2.setCurrentPosition(0);
  stepper2.disableOutputs(); //disable outputs
  stepper3.setCurrentPosition(0);
  stepper3.disableOutputs(); //disable outputs
  stepper4.setCurrentPosition(0);
  stepper4.disableOutputs(); //disable outputs
  stepper5.setCurrentPosition(0);
  servo.write(0);
  stepper5.disableOutputs(); //disable outputs
}

/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//Loop Function
/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
void loop()
{
  //Constantly looping through these 2 functions.
  //only use non-blocking commands, so something else (should also be non-blocking) can be done during the movement of the motor
  checkSerial(); //check serial port for new commands
  RunTheMotor(); //function to handle the motor 
}

/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//RunTheMotor Function
/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
void RunTheMotor()
{
  if (runallowed == true)
  {
    //enable motor
    //step the motor (this will step the motor by 1 step at each loop)
    stepper1.enableOutputs();
    stepper1.run();
    stepper2.enableOutputs();
    stepper2.run();
    stepper3.enableOutputs();
    stepper3.run();
    stepper4.enableOutputs();
    stepper4.run();
    stepper5.enableOutputs();
    stepper5.run(); 
  }
  else //program enters this part if the runallowed is FALSE, no operation
  {
    return;
  }
}

/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//checkSerial Function
/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
void checkSerial() {
  recvWithStartEndMarkers();
  if (newData == true) { //when data for one line is ready 
    strcpy(tempChars, receivedChars);
    // this temporary copy is necessary to protect the original data
    // because strtok() used in parseData() replaces the commas with \0
    parseData();

    //stepper motor X
    receivedStep1 = rotation_value1;
    if (receivedStep1 >=0 && receivedStep1 <=90000){
      RotateRelative();
    }

    //stepper motor Z
    receivedStep2 = -rotation_value2;
    if (receivedStep2 >=-9000 && receivedStep2 <=0){
      RotateRelative();
    }
    
    //stepper motor Y
    receivedStep3 = rotation_value3;
    if (receivedStep3 >=0 && receivedStep3 <=8000){
      RotateRelative();
    }

    //stepper motor Arm
    receivedStep4 = rotation_value4;
    if (receivedStep4 >=0 && receivedStep4 <=3744){
      RotateRelative();
    }

    //stepper motor Wrist (currently disabled)
    receivedStep5 = - rotation_value5;
    if (receivedStep5 >=-2000 && receivedStep5 <=0){
      RotateRelative();
    }

    receivedClamp = rotation_clamp;
    servo.write(receivedClamp);
    newData = false;
  }    
}

/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//recWithStartEndMarkers Function
/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//Command recevied format: <"rotation_value5","rotation_value2","rotation_value3","rotation_value4","rotation_clamp","rotation_value1">
//                       : <wrist, Z, Y, arm, clamp, X>
void recvWithStartEndMarkers() { 
  static boolean recvInProgress = false;
  static byte ndx = 0; //data size counter for each character per line
  char startMarker = '<'; //data initiator
  char endMarker = '>';   //data terminator
  char rc;

  while (Serial.available() > 0 && newData == false) { //when serial buffer is not empty and receiving data still in progress
    rc = Serial.read(); //get character one by one from serial buffer

    if (recvInProgress == true) { //if data receiving is still in progress
        if (rc != endMarker) { //if the character is not the terminator  '>'
            receivedChars[ndx] = rc; //keep on receiving the character, storing into array
            ndx++; //increment the character counter
            if (ndx >= numChars) { //if character counter equal or exceeds 200 characters
                ndx = numChars - 1; //limit the character counter 
            }
        }
        else { //if the character is the terminator '>'
            receivedChars[ndx] = '\0'; // terminate the string
            recvInProgress = false; //indicate data receiving is completed
            ndx = 0; //reset character counter
            newData = true; //indicate new data is ready
        }
    }

    else if (rc == startMarker) { //is character is the initiator '<'
        recvInProgress = true; //indicate data receiving is in progress
    }
  }
}

/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//parseData Function
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// split the serial received data into its parts
void parseData() {               

  char *strtokIndx;                        // this is used by strtok() as an index    
  strtokIndx = strtok(tempChars,",");      // get the stepper motor wrist position (first part)
  rotation_value5 = atoi(strtokIndx);      // convert this part to an integer

  strtokIndx = strtok(NULL, ",");          // get the stepper motor Z position (second part)
  rotation_value2 = atoi(strtokIndx);      // convert this part to an integer

  strtokIndx = strtok(NULL, ",");          // get the stepper motor Y position (third part)
  rotation_value3 = atoi(strtokIndx);      // convert this part to an integer

  strtokIndx = strtok(NULL, ",");          // get the stepper motor Arm position (forth part)
  rotation_value4 = atoi(strtokIndx);      // convert this part to an integer

  strtokIndx = strtok(NULL, ",");          // get the stepper motor Clamp position (fifth part)
  rotation_clamp = atoi(strtokIndx);       // convert this part to an integer

  strtokIndx = strtok(NULL, ",");          // get the stepper motor X position (sixth part)
  rotation_value1 = atoi(strtokIndx);      // convert this part to an integer
}

/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//RotateRelative Function
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//parse position data to each stepper motor
void RotateRelative(){
  runallowed = true;
  stepper1.setMaxSpeed(3000);
  stepper1.moveTo(receivedStep1);
  stepper2.setMaxSpeed(2000);
  stepper2.moveTo(receivedStep2);
  stepper3.setMaxSpeed(2000);
  stepper3.moveTo(receivedStep3);  
  stepper4.setMaxSpeed(2000);
  stepper4.moveTo(receivedStep4); 
  stepper5.setMaxSpeed(2000);
  stepper5.moveTo(receivedStep5);
}


