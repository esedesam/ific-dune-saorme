/****************************************************************************** 
SparkFun Easy Driver Basic Demo
Toni Klopfenstein @ SparkFun Electronics
March 2015
https://github.com/sparkfun/Easy_Driver

Simple demo sketch to demonstrate how 5 digital pins can drive a bipolar stepper motor,
using the Easy Driver (https://www.sparkfun.com/products/12779). Also shows the ability to change
microstep size, and direction of motor movement.

Development environment specifics:
Written in Arduino 1.6.0

This code is beerware; if you see me (or any other SparkFun employee) at the local, and you've found our code helpful, please buy us a round!
Distributed as-is; no warranty is given.

Example based off of demos by Brian Schmalz (designer of the Easy Driver).
http://www.schmalzhaus.com/EasyDriver/Examples/EasyDriverExamples.html
******************************************************************************/
//Declare pin functions on Redboard
#define stp 11
#define dir 12
#define stpb 7  
#define dirb 8
#define stpc 9  
#define dirc 10
#define MS1 4
#define MS2 5
#define EN  6

//Declare variables for functions
char user_input;
long x;
int y;
int state;

int n=15; 
int count=0;
int flag= n+1;

void setup() {
  pinMode(stp, OUTPUT);
  pinMode(dir, OUTPUT);
  pinMode(stpb, OUTPUT);
  pinMode(dirb, OUTPUT);
  resetEDPins(); //Set step, direction, microstep and enable pins to default states
  Serial.begin(9600); //Open Serial connection for debugging
 
  printMenu();
}

//Main loop
void loop() {
  while(Serial.available()){
      printMenu();
      user_input = Serial.read(); //Read user input and trigger appropriate function
      digitalWrite(EN, LOW); //Pull enable pin low to allow motor control
      //Serial.println(count);
      Serial.println(); 
      if (user_input =='1')
      {
        stepForwardMotor1();
      }
      else if(user_input =='2')
      {
        stepReverseMotor1();
      }
      else if(user_input =='3')
      {
        stepForwardMotor2();
      }
      else if(user_input =='4')
      {
        stepReverseMotor2();
      }
      else
      {
        Serial.println();
      }
      resetEDPins();
    }
  }


//Reset Easy Driver pins to default states
void resetEDPins()
{
  digitalWrite(stp, LOW);
  digitalWrite(dir, LOW);
  digitalWrite(stpb, LOW);
  digitalWrite(dirb, LOW);
}

void printMenu() {
  Serial.println();
  //Print function list for user selection
  Serial.println("SISTEMA DE CONTROL PARA MOVER EL MOTOR: PRECIONE EL NUMERO DE LA ACCIÓN A REALIZAR");
  Serial.println("1. Mover 10º el motor 1 (PMT) clock-wise.");
  Serial.println("2. Mover 10º el motor 1 (PMT) anticlock-wise.");
  Serial.println("3. Mover 10º el motor 2 (MUESTRAS) clock-wise.");
  Serial.println("4. Mover 10º el motor 2 (MUESTRAS) anticlock-wise.");
  Serial.println();
}

//Default microstep mode function
void stepForwardDefaultMotor1()
{
  Serial.println("El sistema se está desplazando 1 cm para adelante.");
  digitalWrite(dir, LOW); //Pull direction pin low to move "forward"
  for(x= 0; x<90; x++)  //Loop the forward stepping enough times for motion to be visible
  {
    digitalWrite(stp,HIGH); //Trigger one step forward
    delay(1);
    digitalWrite(stp,LOW); //Pull step pin low so it can be triggered again
    delay(1);
  }
}

//Reverse default microstep mode function
void ReverseStepDefault()
{
  Serial.println("El sistema se está desplazando 1 cm para atrás.");
  digitalWrite(dir, HIGH); //Pull direction pin high to move in "reverse"
  for(x= 0; x<90; x++)  //Loop the stepping enough times for motion to be visible
  {
    digitalWrite(stp,HIGH); //Trigger one step
    delay(1);
    digitalWrite(stp,LOW); //Pull step pin low so it can be triggered again
    delay(1);
  }
}

void StepForwardDefaultB()
{
  Serial.println("El sistema se está desplazando 1 cm para adelante.");
  digitalWrite(dirb, LOW); //Pull direction pin low to move "forward"
  for(x= 0; x<90; x++)  //Loop the forward stepping enough times for motion to be visible
  {
    digitalWrite(stpb,HIGH); //Trigger one step forward
    delay(1);
    digitalWrite(stpb,LOW); //Pull step pin low so it can be triggered again
    delay(1);
  }
}

//Reverse default microstep mode function
void ReverseStepDefaultB()
{
  Serial.println("El sistema se está desplazando 1 cm para atrás.");
  digitalWrite(dirb, HIGH); //Pull direction pin high to move in "reverse"
  for(x= 0; x<90; x++)  //Loop the stepping enough times for motion to be visible
  {
    digitalWrite(stpb,HIGH); //Trigger one step
    delay(1);
    digitalWrite(stpb,LOW); //Pull step pin low so it can be triggered again
    delay(1);
  }
}
