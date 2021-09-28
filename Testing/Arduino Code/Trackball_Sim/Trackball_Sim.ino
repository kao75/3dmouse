// Trackball_Sim.ino

#define POT_PIN A0
#define SERIAL_BAUD 115200

char incomingChar = 'w';

void setup() {
  Serial.begin(SERIAL_BAUD);
}

void loop() {
    sendData();

    if (Serial.available() > 0) {
      incomingChar = Serial.read();
      Serial.print("received: ");
      Serial.println(incomingChar);
      // send request to mouse
  }

    delay(100);
}

void sendData(){
    int potVal = analogRead(POT_PIN);   // 0 - 1023
    int x_test = potVal;                // 0 - 1023
    int y_test = (potVal * 3) % 1023;   // 0 - 1023
    int z_test = (potVal + 650) % 1023; // 0 - 1023
    int modeOfOperation = 1;            // 1 - 3

    Serial.print(modeOfOperation, DEC);
    Serial.print('\t');
    Serial.print(x_test, DEC);
    Serial.print('\t');
    Serial.print(y_test, DEC);
    Serial.print('\t');
    Serial.print(z_test, DEC);
    Serial.print('\n');
}
