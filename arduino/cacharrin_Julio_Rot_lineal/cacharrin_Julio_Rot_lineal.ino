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
#define STEPSPERMM 2000

//Declare variables for functions
char user_input;
long x;
int y;
int state;

int n=155; 
int count=0;
int HorizontalPosition=0;
int flag= n+1;

void PrintStatus()
{
  Serial.println();
  Serial.println("SISTEMA DE CONTROL PARA MOVER EL MOTOR: PRECIONE EL NUMERO DE LA ACCIÓN A REALIZAR");
  Serial.println("1. Mover el filtro horizontalmente hacia el motor.");
  Serial.println("2. Mover el horizontalmente alejandolo del motor .");
  Serial.println("3. El sistema de rotacion gira n grados en sentido antihorario.");
  Serial.println("4. El sistema de rotacion gira n grados en sentido horario.");
  Serial.println("5. Resetea origen a 0º (angular).");
  Serial.println("6. Ajuste fino en sentido antihorario.");
  Serial.println("7. Ajuste fino en sentido horario.");
  Serial.println("8. Calibrar posición horizontal.");
  Serial.println("Angulo actual (º):");
  Serial.println(count*1.0112);
  Serial.println("Angulo actual (steps):");
  Serial.println(count);
  Serial.println("Posición horizontal actual (cm):");
  Serial.println(1.0*HorizontalPosition*0.1/STEPSPERMM);
  Serial.println("Posición horizontal actual (steps):");
  Serial.println(HorizontalPosition);
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
  while(Serial.available()){
      PrintStatus();
      user_input = Serial.read(); //Read user input and trigger appropriate function
      digitalWrite(EN, LOW); //Pull enable pin low to allow motor control
      //Serial.println(count);
      Serial.println();
      
      if (count<=10000)
      { 
//        PrintStatus();
        if (user_input =='1') StepForwardDefault();
        if(user_input =='2') ReverseStepDefault();
        if(user_input =='3') rotateClk();
        if(user_input =='4') rotateAntiClk();
        if(user_input == '5')
        {
          count=0;
          Serial.println("Counter set to 0: ");
          Serial.println(count);
          resetEDPins();
        }
        if(user_input == '6') ajusteFinoClk();
        if(user_input == '7') ajusteFinoAntiClk();
        if(user_input == '8') SetHorizontalPosition();
        
        
      }
      if(0)
      {
          Serial.println("Se ha alcanzado el límite de pasos del sistema");
          Serial.println();
          Serial.println("Luego de 30 segundos el sistema volverá al origen");
          delay(300);
          toOrigin();
          count=0;
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
  digitalWrite(MS1, LOW);
  digitalWrite(MS2, LOW);
  digitalWrite(EN, HIGH);
}

//Default microstep mode function
void StepForwardDefault()
{
  Serial.println("El sistema se está desplazando 1 cm para adelante.");
  digitalWrite(dir, HIGH); //Pull direction pin low to move "forward"
  for(x= 0; x<2000; x++)  //Loop the forward stepping enough times for motion to be visible
  {
    digitalWrite(stp,HIGH); //Trigger one step forward
    delay(1);
    digitalWrite(stp,LOW); //Pull step pin low so it can be triggered again
    delay(1);
    HorizontalPosition++;
    
  }
}

void ReverseStepDefault()
{
  Serial.println("El sistema se está desplazando 1 cm para adelante.");
  digitalWrite(dir, LOW); //Pull direction pin low to move "forward"
  for(x= 0; x<2000; x++)  //Loop the forward stepping enough times for motion to be visible 2000 pasos por cm
  {
    digitalWrite(stp,HIGH); //Trigger one step forward
    delay(1);
    digitalWrite(stp,LOW); //Pull step pin low so it can be triggered again
    delay(1);
    HorizontalPosition--;
  }
  Serial.println("Estoy fuera del camino del monocromador");
  Serial.println();
}
void SetHorizontalPosition()
{
  Serial.println("Introduce la posición actual del filtro en mm");
  int inputpos = Serial.read(); //Read user input and trigger appropriate function
  HorizontalPosition=(float)inputpos*STEPSPERMM; // 200 pasos por mm
}

void rotateClk()
{
  Serial.println("El sistema se está desplazando 10º en sentido horario.");
  digitalWrite(dirb, LOW); //Pull direction pin low to move "forward"
  for(int i=0; i<10; i++)
  {
    for(int j= 0; j<9; j++)  //Loop the forward stepping enough times for motion to be visible
    {
      digitalWrite(stpb,HIGH); //Trigger one step forward
      delay(1);
      digitalWrite(stpb,LOW); //Pull step pin low so it can be triggered again
      delay(1);
    }
  count = count+1;
  delay(100);
  Serial.println("Estoy en el angulo");
  Serial.println(count*1.0112); //Calibrar el angulo
  Serial.println(count); //Calibrar el angulo
  Serial.println();
  delay(1000);
  }
}

//Reverse default microstep mode function
void rotateAntiClk()
{
  Serial.println("El sistema se está desplazando 10º en sentido horario.");
  digitalWrite(dirb, HIGH); //Pull direction pin low to move "forward"
  for(int i=0; i<10; i++){
    for(int j= 0; j<9; j++)  //Loop the forward stepping enough times for motion to be visible
    {
      digitalWrite(stpb,HIGH); //Trigger one step forward
      delay(1);
      digitalWrite(stpb,LOW); //Pull step pin low so it can be triggered again
      delay(1);
    }
  count = count-1;
  delay(100);
   Serial.println("Estoy en el angulo");
  Serial.println(count*1.0112); //Calibrar el angulo
  Serial.println(count); //Calibrar el angulo
  Serial.println();
  delay(1000);
 }
}


void toOrigin()
{
  Serial.println("El sistema se está moviendo al origen por alcanzar el límite.");
  digitalWrite(dirb, HIGH); //Pull direction pin high to move in "reverse"
  for(x= 0; x<(flag*10); x++)  //Loop the stepping enough times for motion to be visible
  {
    digitalWrite(stpb,HIGH); //Trigger one step
    delay(1);
    digitalWrite(stpb,LOW); //Pull step pin low so it can be triggered again
    delay(1);
  }
  Serial.println("Es posible comenzar de nuevo con la medida");
  Serial.println();
  
}

void ajusteFinoClk()
{
  Serial.println("El sistema se está ajustando finamente en sentido horario.");
  digitalWrite(dirb, LOW); //Pull direction pin low to move "forward"
  for(int j= 0; j<1; j++)  //Loop the forward stepping enough times for motion to be visible
  {
    digitalWrite(stpb,HIGH); //Trigger one step forward
    delay(1);
    digitalWrite(stpb,LOW); //Pull step pin low so it can be triggered again
    delay(1);
  }
}

void ajusteFinoAntiClk()
{
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
