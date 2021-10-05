/*
 * Switch_Test.ino
 * Used for 1st checkoff for ECE 1896: Interface with mode switches and LEDs
 * Created By: Dylan Butler
 * Last Modified: 10/5/2021
 */

// Define Global Constants
#define SWITCH_RIGHT_PIN 2
#define SWITCH_LEFT_PIN 3
#define LED_PAN_PIN 4
#define LED_ZOOM_PIN 5
#define LED_ORBIT_PIN 6

// Global variables for interrupt
volatile byte modeCounter = 0;

// Global variables
byte modeNumber = 0;

void setup() {
  Serial.begin(115200);

  pinMode(SWITCH_RIGHT_PIN, INPUT);
  pinMode(SWITCH_LEFT_PIN, INPUT);
  pinMode(LED_PAN_PIN, OUTPUT);
  pinMode(LED_ZOOM_PIN, OUTPUT);
  pinMode(LED_ORBIT_PIN, OUTPUT);

  attachInterrupt(digitalPinToInterrupt(SWITCH_RIGHT_PIN), updateSwitchRight, RISING);
  attachInterrupt(digitalPinToInterrupt(SWITCH_LEFT_PIN), updateSwitchLeft, RISING);

  ledsOff();
}

void loop() {
  Serial.print("Current Mode: ");
  Serial.print(modeCounter);
  Serial.print(" Mode Number: ");
  modeNumber = modeCounter % 3;
  Serial.println(modeNumber);
  updateLeds();
  updateSwitchRight();
  delay(1000);
}

void updateSwitchRight(){
  if(++modeCounter == 255){
    modeCounter = 0;
  }
}

void updateSwitchLeft(){
  if(--modeCounter == 255){
    modeCounter = 254;
  }
}

void updateLeds(){
  if(modeNumber == 0){
    Serial.println("Orbit LED");
    digitalWrite(LED_ORBIT_PIN, HIGH);
    digitalWrite(LED_PAN_PIN, LOW);
    digitalWrite(LED_ZOOM_PIN, LOW);
  }
  else if(modeNumber == 1){
    Serial.println("Pan LED");
    digitalWrite(LED_ORBIT_PIN, LOW);
    digitalWrite(LED_PAN_PIN, HIGH);
    digitalWrite(LED_ZOOM_PIN, LOW);
  }
  else if(modeNumber == 2){
    Serial.println("Zoom LED");
    digitalWrite(LED_ORBIT_PIN, LOW);
    digitalWrite(LED_PAN_PIN, LOW);
    digitalWrite(LED_ZOOM_PIN, HIGH);
  }
}

void ledsOff(){
  digitalWrite(LED_PAN_PIN, LOW);
  digitalWrite(LED_ZOOM_PIN, LOW);
  digitalWrite(LED_ORBIT_PIN, LOW);
}

void ledsOn(){
  digitalWrite(LED_PAN_PIN, HIGH);
  digitalWrite(LED_ZOOM_PIN, HIGH);
  digitalWrite(LED_ORBIT_PIN, HIGH);
}
