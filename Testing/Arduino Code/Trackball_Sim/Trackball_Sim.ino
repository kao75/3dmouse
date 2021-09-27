// Trackball_Sim.ino

#define POT_PIN A0
#define SERIAL_BAUD 115200

void setup() {
    Serial.begin(SERIAL_BAUD);
}

void loop() {
    sendData();
    delay(100);
}

void sendData(){
    int potVal = analogRead(POT_PIN);
    Serial.println(potVal);
}
