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
#define stp 7
#define dir 8
#define stpb 11  
#define dirb 12
#define MS1 A2
#define MS2 A1
#define EN  6
#define stepsPerMM 200
#define horizontalMinMM 10
#define horizontalMaxMM 190
#define bufferSize 8 // Receive up to 7 bytes

//Declare variables for functions
char user_input;
long x;
int y;
int state;

int n = 155; 
int angularPosition = 0;
long int horizontalPosition = 0;
int flag = n + 1;
float inputPos = 0;

void PrintStatus() {
  Serial.println();
  Serial.println("CONTROL SYSTEM TO MOVE THE MOTORS: PRESS THE NUMBER OF THE ACTION TO BE DONE");
  Serial.println("1. Calibrate horizontal position of the system.");
  Serial.println("2. Move the system horizontally 1 cm towards the motor.");
  Serial.println("3. Move the system horizontally 1 cm away from the motor.");
  Serial.println("4. Move the system horizontally to user defined position.");
  Serial.println("5. Reset the angular count variable to 0º.");
  Serial.println("6. Rotate the system 10º clock-wise.");
  Serial.println("7. Rotate the system 10º anticlock-wise.");
  Serial.println("8. Ajuste fino en sentido horario.");
  Serial.println("9. Ajuste fino en sentido antihorario.");
  Serial.print("Current angle (º): ");
  Serial.println(angularPosition * 1.0112);
  Serial.print("Current angle (steps): ");
  Serial.println(angularPosition);
  Serial.print("Current horizontal position (cm): ");
  Serial.println(0.1 * horizontalPosition / stepsPerMM);
  Serial.print("Current horizontal position (steps): ");
  Serial.println(horizontalPosition);
}

void setup() {
  pinMode(stp, OUTPUT);
  pinMode(dir, OUTPUT);
  pinMode(stpb, OUTPUT);
  pinMode(dirb, OUTPUT);
  pinMode(MS1, OUTPUT);
  pinMode(MS2, OUTPUT);
  pinMode(EN, OUTPUT);
  resetEDPins(); //Set step, direction, microstep and enable pins to default states
  Serial.begin(9600); //Open Serial connection for debugging
  PrintStatus();
}

//Main loop
void loop() {
  PrintStatus();
  while(Serial.available() == 0) {}
  user_input = Serial.read(); //Read user input and trigger appropriate function
  digitalWrite(EN, LOW); //Pull enable pin low to allow motor control
  Serial.println();
  if(angularPosition <= 10000) {
    if(user_input == '1') setHorizontalPosition();
    if(user_input == '2') stepForwardDefault();
    if(user_input == '3') stepReverseDefault();
    if(user_input == '4') horizontalUserPosition();
    if(user_input == '5')
    {
      angularPosition = 0;
      Serial.print("Angular position set to 0º: ");
      Serial.println(angularPosition);
      resetEDPins();
    }
    if(user_input == '6') rotateClk();
    if(user_input == '7') rotateAntiClk();
    if(user_input == '8') ajusteFinoClk();
    if(user_input == '9') ajusteFinoAntiClk();
  }
  if(0) {
      Serial.println("Se ha alcanzado el límite de pasos del sistema");
      Serial.println();
      Serial.println("Luego de 30 segundos el sistema volverá al origen");
      delay(300);
      toOrigin();
      angularPosition=0;
  }
  resetEDPins();
  Serial.println("\n \n");
  delay(1000);
}

//Reset Easy Driver pins to default states
void resetEDPins() {
  digitalWrite(stp, LOW);
  digitalWrite(dir, LOW);
  digitalWrite(stpb, LOW);
  digitalWrite(dirb, LOW);
  digitalWrite(MS1, LOW);
  digitalWrite(MS2, LOW);
  digitalWrite(EN, HIGH);
}

void setHorizontalPosition() {
  char buffer[bufferSize];
  do {
    delay(100);
    Serial.print("Write the current horizontal position of the system in mm. Range: [ ");
    Serial.print(horizontalMinMM);
    Serial.print(" , ");
    Serial.print(horizontalMaxMM);
    Serial.println(" ] mm.");
    for(int i = 0; i < bufferSize; i++) {
      buffer[i] = ' ';
    }
    while(Serial.available() == 0) {}
    Serial.readBytesUntil('\n', buffer, bufferSize);
    Serial.println(buffer);
    inputPos = atof(buffer);
    Serial.println(inputPos);
  }while(inputPos < horizontalMinMM || inputPos > horizontalMaxMM);
  horizontalPosition = (long int)round(inputPos*stepsPerMM);
//  Serial.println(inputPos*stepsPerMM);
//  Serial.println(round(inputPos*stepsPerMM));
//  Serial.println(horizontalPosition);
  Serial.print("Horizontal position of the system has been successfully calibrated to ");
  Serial.print(horizontalPosition / stepsPerMM);
  Serial.println(" mm.");
}

//Default microstep mode function
void stepForwardDefault() {
  Serial.println("System is moving 1 cm towards the motor.");
  digitalWrite(dir, HIGH); //Pull direction pin low to move "forward"
  for(int i = 0; i < 2000; i++) { //Loop the forward stepping enough times for motion to be 1cm
    digitalWrite(stp, HIGH); //Trigger one step forward
    delay(1);
    digitalWrite(stp, LOW); //Pull step pin low so it can be triggered again
    delay(1);
    horizontalPosition++;
  }
  Serial.println("System successfully moved 1 cm towards the motor.");
}

void stepReverseDefault() {
  Serial.println("System is moving 1 cm away from the motor.");
  digitalWrite(dir, LOW); //Pull direction pin low to move "reverse"
  for(int i = 0; i < (10 * stepsPerMM); i++) { //Loop the forward stepping enough times for motion to be 1cm
    digitalWrite(stp, HIGH); //Trigger one step forward
    delay(1);
    digitalWrite(stp, LOW); //Pull step pin low so it can be triggered again
    delay(1);
    horizontalPosition--;
  }
  Serial.println("System successfully moved 1 cm away from the motor.");
}

void horizontalUserPosition() {
  char buffer[bufferSize];
  do {
    delay(100);
    Serial.print("Write the horizontal position of the system to be moved to in mm. Range: [ ");
    Serial.print(horizontalMinMM);
    Serial.print(" , ");
    Serial.print(horizontalMaxMM);
    Serial.println(" ] mm.");
    while(Serial.available() == 0) {}
    for(int i = 0; i < bufferSize; i++) {
      buffer[i] = ' ';
    }
    Serial.readBytesUntil('\n', buffer, bufferSize);
    inputPos = atof(buffer);
  } while(inputPos < horizontalMinMM | inputPos > horizontalMaxMM);
  long int auxPos = (long int) round(inputPos * stepsPerMM); // Round inputPos(mm) to the closest inputPos(step)
  Serial.println(buffer);
  Serial.println(inputPos);
  Serial.println(auxPos);
  long int movingSteps = auxPos - horizontalPosition;
  Serial.print("Me voy a mover ");
  Serial.println(movingSteps);
  if(movingSteps == 0) {
    Serial.print("System is currently in the desired position: ");
    Serial.print(horizontalPosition / stepsPerMM);
    Serial.println(" mm.");
  }
  else {
    if(movingSteps > 0) {
      digitalWrite(dir, HIGH); //Pull direction pin low to move "forward"
      for(int i = 0; i < movingSteps; i++) {      
        digitalWrite(stp, HIGH); //Trigger one step forward
        delay(1);
        digitalWrite(stp, LOW); //Pull step pin low so it can be triggered again
        delay(1);
        horizontalPosition++;
      }
    }
    else {
      digitalWrite(dir, LOW); //Pull direction pin low to move "reverse"
      for(int i = 0; i < -movingSteps; i++) {      
        digitalWrite(stp, HIGH); //Trigger one step forward
        delay(1);
        digitalWrite(stp, LOW); //Pull step pin low so it can be triggered again
        delay(1);
        horizontalPosition--;
      }
    }
    Serial.print("System moved to horizontal position: ");
    Serial.print(horizontalPosition / stepsPerMM);
    Serial.println(" mm.");
  }
}

void rotateClk() {
  Serial.println("System is rotating 10º clock-wise.");
  digitalWrite(dirb, LOW); //Pull direction pin low to move "clock"
  for(int i = 0; i < 10; i++) {
    for(int j = 0; j < 9; j++) { //Loop the forward stepping enough times for motion to be 1.0112º
      digitalWrite(stpb, HIGH); //Trigger one step forward
      delay(1);
      digitalWrite(stpb, LOW); //Pull step pin low so it can be triggered again
      delay(1);
    }
    angularPosition = angularPosition + 1;
    Serial.print("Current angle (º): ");
    Serial.println(angularPosition * 1.0112); //Calibrar el angulo
    delay(100);
  }
}

//Reverse default microstep mode function
void rotateAntiClk() {
  Serial.println("System is rotating 10º anticlock-wise.");
  digitalWrite(dirb, HIGH); //Pull direction pin low to move "anticlock"
  for(int i = 0; i < 10; i++) {
    for(int j = 0; j < 9; j++) { //Loop the forward stepping enough times for motion to be 1.0112º
      digitalWrite(stpb,HIGH); //Trigger one step forward
      delay(1);
      digitalWrite(stpb,LOW); //Pull step pin low so it can be triggered again
      delay(1);
    }
    angularPosition = angularPosition - 1;
    Serial.print("Current angle (º): ");
    Serial.println(angularPosition * 1.0112); //Calibrar el angulo
    delay(100);
 }
}

void toOrigin() {
  Serial.println("El sistema se está moviendo al origen por alcanzar el límite.");
  digitalWrite(dirb, HIGH); //Pull direction pin high to move in "reverse"
  for(x = 0; x < (flag*10); x++) { //Loop the stepping enough times for motion to be visible
    digitalWrite(stpb,HIGH); //Trigger one step
    delay(1);
    digitalWrite(stpb,LOW); //Pull step pin low so it can be triggered again
    delay(1);
  }
  Serial.println("Es posible comenzar de nuevo con la medida");
  Serial.println();
}

void ajusteFinoClk() {
  Serial.println("El sistema se está ajustando finamente en sentido horario.");
  digitalWrite(dirb, LOW); //Pull direction pin low to move "forward"
  for(int j = 0; j < 1; j++)  //Loop the forward stepping enough times for motion to be visible
  {
    digitalWrite(stpb,HIGH); //Trigger one step forward
    delay(1);
    digitalWrite(stpb,LOW); //Pull step pin low so it can be triggered again
    delay(1);
  }
}

void ajusteFinoAntiClk() {
  Serial.println("El sistema se está ajustando finamente en sentido horario.");
  digitalWrite(dirb, HIGH); //Pull direction pin low to move "forward"
  for(int j= 0; j<1; j++)  //Loop the forward stepping enough times for motion to be visible
  {
    digitalWrite(stpb,HIGH); //Trigger one step forward
    delay(1);
    digitalWrite(stpb,LOW); //Pull step pin low so it can be triggered again
    delay(1);
  }
}
