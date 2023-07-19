/****************************************************************************** 
Programa para minimo para mover el motor por milimetro en una u otra direccion
******************************************************************************/
//Declare pin functions on Redboard
#include "DHT.h"

#define DHT11_PIN1 A0
#define DHT11_PIN2 A1
#define stp 9
#define dir 10
#define fan1 4
#define fan2 3
#define fan3 2
#define DHT1TYPE DHT11   
#define DHT2TYPE DHT11   
char user_input;
long x;
int y;
int state;

DHT dht1(DHT11_PIN1, DHT1TYPE);
DHT dht2(DHT11_PIN2, DHT2TYPE);

void setup() {
  pinMode(stp, OUTPUT);
  pinMode(dir, OUTPUT);
  pinMode(fan1, OUTPUT);
  pinMode(fan2, OUTPUT);
  pinMode(fan3, OUTPUT);
  resetEDPins(); //Set step, direction, microstep and enable pins to default states
  Serial.begin(9600); //Open Serial connection for debugging
  dht1.begin();
  dht2.begin();
 
}

//Main loop
void loop() {
  Serial.println("Ventiladores apagados");
  delay(5000);
  float t1 = dht1.readTemperature();
  float t2 = dht2.readTemperature();
  digitalWrite(fan1, HIGH);
  digitalWrite(fan2, HIGH);
  digitalWrite(fan3, HIGH);
  Serial.println("Ventiladores encendidos");
  delay(5000);
  // if(t2>25){
  //   digitalWrite(fan2, HIGH);
  // }
  // else{
  //   digitalWrite(fan2, LOW);
  // }
  // if(t1>25){
  //   digitalWrite(fan3, HIGH);
  // }
  // else{
  //   digitalWrite(fan3, LOW);
  // }
  
  // while(Serial.available()){
  //     user_input = Serial.read(); //Read user input and trigger appropriate function
  //       if (user_input =='1') StepForwardDefault();
  //       if(user_input =='2') ReverseStepDefault();
  //     }
      resetEDPins();
  }


//Reset Easy Driver pins to default states
void resetEDPins()
{
  digitalWrite(stp, LOW);
  digitalWrite(dir, LOW);
  digitalWrite(fan1, LOW); 
  digitalWrite(fan2, LOW); 
  digitalWrite(fan3, LOW); 
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
