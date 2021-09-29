// Trackball_Sim.ino

#define SERIAL_BAUD 115200
#define X_POT_PIN A0
#define Y_POT_PIN A1
#define Z_POT_PIN A2


char incomingChar = '\0';

void setup() {
  Serial.begin(SERIAL_BAUD);
  while (!Serial) {
  }
//  Serial.write("ready");
}

void loop() {
    // recieved new command
    if (Serial.available() > 0) {
      incomingChar = Serial.read();

      if (incomingChar == 'w') {  // recieved 'w' command
        // send data request to mouse, get new data
        sendData();     // send new data
      }
    }
    delay(100);
}

void sendData(){
    int x = analogRead(X_POT_PIN);         // 0 - 1023
    int y = analogRead(Y_POT_PIN);         // 0 - 1023
    int z = analogRead(Z_POT_PIN);         // 0 - 1023
    int mode = 1;                          // 1 - 3

    // send mode\tx\ty\tz\n
    Serial.print(mode, DEC);
    Serial.print('\t');
    Serial.print(x, DEC);
    Serial.print('\t');
    Serial.print(y, DEC);
    Serial.print('\t');
    Serial.print(z, DEC);
    Serial.print('\n');
}
