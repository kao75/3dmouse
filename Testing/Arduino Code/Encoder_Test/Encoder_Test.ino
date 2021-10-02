// Encoder_Test.ino
// Used for 1st checkoff for ECE 1896: Interface with mechanical trackball and rotary encoders

// Include the SPI library in this sketch
#include <SPI.h>

// Define global constants
#define X_CONNECTED 1
#define Y_CONNECTED 0
#define Z_CONNECTED 0

#define X_CS_PIN 10
#define Y_CS_PIN 9
#define Z_CS_PIN 8
#define MOSI_PIN 11
#define MISO_PIN 12
#define SCK_PIN 13

void setup() {
    Serial.begin(115200);
    SPI.begin();
    pinMode(X_CS_PIN, OUTPUT);
    pinMode(Y_CS_PIN, OUTPUT);
    pinMode(Z_CS_PIN, OUTPUT);

    digitalWrite(X_CS_PIN, HIGH);
    digitalWrite(Y_CS_PIN, HIGH);
    digitalWrite(Z_CS_PIN, HIGH);

    delay(2000);
}

void loop() {
    if(X_CONNECTED){
        int xPos = getPosData(X_CS_PIN);
        Serial.print("X axis: ");
        Serial.println(xPos);
    }
    if(Y_CONNECTED){
        int yPos = getPosData(Y_CS_PIN);
        Serial.print("Y axis: ");
        Serial.println(yPos);
    }
    if(Z_CONNECTED){
        int zPos = getPosData(Z_CS_PIN);
        Serial.print("Z axis: ");
        Serial.println(zPos);
    }
    delay(50);
}


int getPosData(int csPin){
    SPISettings spiSettings(1000000, MSBFIRST, SPI_MODE1);
    
    SPI.beginTransaction(spiSettings);
    digitalWrite(csPin, LOW);
    SPI.transfer16(0xFFFF); // Set read address
    digitalWrite(csPin, HIGH);
    digitalWrite(csPin, LOW);
    int data = SPI.transfer16(0xC000); // Read data with no-op command
    digitalWrite(csPin, HIGH);
    SPI.endTransaction();

    Serial.print("Raw Data: ");
    Serial.println(data, BIN);
    
    //Check for parity errors
    if(((data >> 14) & 0x1) == 1){
    data = -1;
    }
    else{
    data = data & 0x3FFF;
    }
    
    return data;
}
