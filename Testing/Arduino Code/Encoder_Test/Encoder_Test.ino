// Encoder_Test.ino
// Used for 1st checkoff for ECE 1896: Interface with mechanical trackball and rotary encoders

// Include the SPI library in this sketch
#include <SPI.h>

// Define global constants
#define X_CONNECTED 1
#define Y_CONNECTED 1
#define Z_CONNECTED 1

// Pin definitions
#define X_CS_PIN 10
#define Y_CS_PIN 9
#define Z_CS_PIN 8
#define MOSI_PIN 11
#define MISO_PIN 12
#define SCK_PIN 13

// AS5147 Register addresses
#define AS5147_REG_SIZE 14
#define NOP_REG 0x0000
#define ERRFL_REG 0x0001
#define PROG_REG 0x0003
#define DIAAGC_REG 0x3FFC
#define MAG_REG 0x3FFD
#define ANDLEUNC_REG 0x3FFE
#define ANGLECOM_REG 0x3FFF

#define WRAP_VALUE 8192
#define MAX_VALUE 16384

// Global variables
int xPrev = 0, yPrev = 0, zPrev = 0;


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
    int xPos = 0, yPos = 0, zPos = 0;
    unsigned long startTime = micros();
    
    if(X_CONNECTED){
        xPos = getData(X_CS_PIN, ANGLECOM_REG);
        if(xPos == -1){
            int xErr = getData(X_CS_PIN, ERRFL_REG);
            Serial.print("X axis SPI error: ");
            Serial.println(xErr, HEX);
        }
        // USED FOR DEBUGGING
//        Serial.print("X axis position: ");
//        Serial.println(xPos);
    }
    if(Y_CONNECTED){
        yPos = getData(Y_CS_PIN, ANGLECOM_REG);
        if(yPos == -1){
            int yErr = getData(Y_CS_PIN, ERRFL_REG);
            Serial.print("Y axis SPI error: ");
            Serial.println(yErr, HEX);
        }
        // USED FOR DEBUGGING
//        Serial.print("Y axis position: ");
//        Serial.println(yPos);
    }
    if(Z_CONNECTED){
        zPos = getData(Z_CS_PIN, ANGLECOM_REG);
        if(zPos == -1){
            int zErr = getData(Z_CS_PIN, ERRFL_REG);
            Serial.print("Z axis SPI error: ");
            Serial.println(zErr, HEX);
        }
        // USED FOR DEBUGGING
//        Serial.print("Z axis position: ");
//        Serial.println(zPos);
    }

    unsigned long endTime = micros();
    unsigned long elapsedTime = (endTime - startTime);
    Serial.print("Elapsed time to read positions: ");
    Serial.print(elapsedTime);
    Serial.println(" microsecs");

    int xRel = calcRelData(xPos, &xPrev);
    int yRel = calcRelData(yPos, &yPrev);
    Serial.print("(x,y,z): (");
    Serial.print(xRel);
    Serial.print(", ");
    Serial.print(yRel);
    Serial.print(", ");
    Serial.print(zRel);
    Serial.println(")");
    delay(200);
}

int isWrapAround(int val, int valPrev){
    int valRel = val - valPrev;

    if(abs(valRel) < WRAP_VALUE){
        return 0;
    }
    
    return valRel;
}

int calcRelData(int val, int * valPrev){
    int valRel = val - *valPrev;
    int wrapAround = isWrapAround(val, *valPrev);
    // Wrap around case 1: 16383 -> 0
    if(wrapAround < 0){
        valRel = (MAX_VALUE - *valPrev) + val;
    }
    // Wrap around case 2: 0 -> 16383
    else if(wrapAround > 0){
        valRel = -1 * ((MAX_VALUE - val) + *valPrev);
    }
    *valPrev = val;
    
    return valRel;
}

int getData(int csPin, unsigned int addrToRead){
    SPISettings spiSettings(8000000, MSBFIRST, SPI_MODE1);
    
    addrToRead = getAddrWParity(addrToRead);
    
    SPI.beginTransaction(spiSettings);
    digitalWrite(csPin, LOW);
    SPI.transfer16(addrToRead); // Set read address
    digitalWrite(csPin, HIGH);
    digitalWrite(csPin, LOW);
    int data = SPI.transfer16(0xC000); // Read data with no-op command
    digitalWrite(csPin, HIGH);
    SPI.endTransaction();

    // USED FOR DEBUGGING
//    Serial.print("Raw Data: ");
//    Serial.println(data, BIN);
    
    // Check for parity errors
    return ((data >> AS5147_REG_SIZE) & 0x1 ? -1 : data & 0x3FFF);
}

unsigned int getAddrWParity(int addrToRead){
    int bitCount = 0;
    addrToRead |= 0x4000; // Set Read bit in command frame
    unsigned int bitsToCount = addrToRead;
    for(int i = AS5147_REG_SIZE; i > 0; i--){
        bitCount += (addrToRead & 1 ? 1 : 0);
        bitsToCount >>= 1;
    }

    return (bitCount % 2 ? addrToRead : addrToRead | 0x8000);
}
