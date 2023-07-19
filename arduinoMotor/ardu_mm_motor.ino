/****************************************************************************** 
Programa para minimo para mover el motor por milimetro en una u otra direccion
******************************************************************************/
//Declare pin functions on Redboard
#define stp 9
#define dir 10
char user_input;
long x;
int y;
int state;


void setup() {
  pinMode(stp, OUTPUT);
  pinMode(dir, OUTPUT);
  resetEDPins(); //Set step, direction, microstep and enable pins to default states
  Serial.begin(9600); //Open Serial connection for debugging
 
}

//Main loop
void loop() {
  while(Serial.available()){
      user_input = Serial.read(); //Read user input and trigger appropriate function
        if (user_input =='1') StepForwardDefault();
        if(user_input =='2') ReverseStepDefault();
      }
      resetEDPins();
  }


//Reset Easy Driver pins to default states
void resetEDPins()
{
  digitalWrite(stp, LOW);
  digitalWrite(dir, LOW);
}

//Default microstep mode function
void StepForwardDefault()
{
  digitalWrite(dir, HIGH); //Pull direction pin low to move "forward"
  for(x= 0; x<200; x++)  //Loop the forward stepping enough times for motion to be visible
  {
    digitalWrite(stp,HIGH); //Trigger one step forward
    delay(1);
    digitalWrite(stp,LOW); //Pull step pin low so it can be triggered again
    delay(1);;
    
  }
}

void ReverseStepDefault()
{

  digitalWrite(dir, LOW); //Pull direction pin low to move "forward"
  for(x= 0; x<200; x++)  //Loop the forward stepping enough times for motion to be visible 2000 pasos por cm
  {
    digitalWrite(stp,HIGH); //Trigger one step forward
    delay(1);
    digitalWrite(stp,LOW); //Pull step pin low so it can be triggered again
    delay(1);
  }
}
