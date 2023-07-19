#include <SparkFun_ADS1015_Arduino_Library.h>

#include <Wire.h>
#include <SparkFun_ADS1015_Arduino_Library.h> //Click here to get the library: http://librarymanager/All#SparkFun_ADS1015

ADS1015 adcSensor;

#define MCP4725_ADDR 0x60   

int lookup = 0;
char user_input;
bool val;
float volt;

void setup()
{
  Wire.begin();
  Serial.begin(9600);
  pinMode(8, OUTPUT);
  pinMode(A1, INPUT);

  if (adcSensor.begin(0x48) == true)
  {
    Serial.println("Device found. I2C connections are good.");
  }
  else
  {
    Serial.println("Device not found. Check wiring.");
    while (1); 
  }
  adcSensor.setGain(ADS1015_CONFIG_PGA_1); 
  cerearValor();

}
//---------------------------------------------------
void loop()
{
  //volt = 0.005;
  //lookup = (volt + 0.0007)/0.001235; Formula de conversión del DAC donde Lookup es ADU
  
  val = digitalRead(A1); //El valor leido del pulsador de emergencia
  if(lookup==0){
      digitalWrite(8, LOW); 
  }
  else {
    digitalWrite(8, HIGH); 
  }
  int16_t channel_A0 = adcSensor.getSingleEnded(0);
  volt=0.001995951417*channel_A0 + 0.000032388664;
  Serial.print("El valor del voltaje es:");
  Serial.println(volt);
  delay(50);
  if(val==HIGH) resetValorBoton();
  while(Serial.available()){
      user_input = Serial.read(); 
       if (user_input =='1') aumentarValor();
       if(user_input =='2') disminuirValor();
       if(user_input =='3') resetValor();   
      } 
}

void  aumentarValor()
{
  lookup = lookup+10;
  Wire.beginTransmission(MCP4725_ADDR);
  Wire.write(64);                     // cmd to update the DAC
  Wire.write(lookup >> 4);        // the 8 most significant bits...
  Wire.write((lookup & 15) << 4); // the 4 least significant bits...
  Wire.endTransmission();
}

void  disminuirValor()
{
  lookup = lookup-10;
  Wire.beginTransmission(MCP4725_ADDR);
  Wire.write(64);                     // cmd to update the DAC
  Wire.write(lookup >> 4);        // the 8 most significant bits...
  Wire.write((lookup & 15) << 4); // the 4 least significant bits...
  Wire.endTransmission(); 
}

void  resetValor()
{
  while(lookup > 0) 
  {
    lookup=lookup-10;
    Wire.beginTransmission(MCP4725_ADDR);
    Wire.write(64);                     // cmd to update the DAC
    Wire.write(lookup >> 4);        // the 8 most significant bits...
    Wire.write((lookup & 15) << 4); // the 4 least significant bits...
    Wire.endTransmission();
    int16_t channel_A0 = adcSensor.getSingleEnded(0);
  volt=0.00199595*channel_A0 + 0.00003238864;
  Serial.print("El valor del voltaje es:");
  Serial.println(volt);
  delay(300);  
  }

  Serial.println("Se ha reseteado el sistema");
}

void  resetValorBoton()
{
  while(lookup > 0) 
  {
    lookup=lookup-10;
    Wire.beginTransmission(MCP4725_ADDR);
    Wire.write(64);                     // cmd to update the DAC
    Wire.write(lookup >> 4);        // the 8 most significant bits...
    Wire.write((lookup & 15) << 4); // the 4 least significant bits...
    Wire.endTransmission();
    int16_t channel_A0 = adcSensor.getSingleEnded(0);
  volt=0.00199595*channel_A0 + 0.00003238864;
  Serial.print("El valor del voltaje es:");
  Serial.println(volt);
  delay(300);  
  }

  Serial.println("Se ha reseteado el sistema");
  delay(1000);
}

void  cerearValor()
{
  lookup = 0;
  Wire.beginTransmission(MCP4725_ADDR);
  Wire.write(64);                     // cmd to update the DAC
  Wire.write(lookup >> 4);        // the 8 most significant bits...
  Wire.write((lookup & 15) << 4); // the 4 least significant bits...
  Wire.endTransmission();
  
}
