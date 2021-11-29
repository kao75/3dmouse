/*
 * 3DMouseTest.ino
 * Created By: Dylan Butler
 * Last Modified: 11/27/2021
 */

// Include the SPI library in this sketch
#include <SPI.h>

// Include the Arduino library in this sketch
#include <Arduino.h>

// Define ALTERNATE_PINS to use non-standard GPIO pins for SPI bus

//#ifdef ALTERNATE_PINS
//  #define HSPI_MISO   26
//  #define HSPI_MOSI   27
//  #define HSPI_SCLK   25
//  #define HSPI_SS     32
//#else
  #define HSPI_MISO   12
  #define HSPI_MOSI   13
  #define HSPI_SCLK   14
  #define HSPI_SS     15
//#endif

//uninitalised pointer to SPI object
SPIClass * hspi = NULL;

// Pin definitions
#define X_CS_PIN 15
#define Y_CS_PIN 16
#define Z_CS_PIN 17

// Switch Circuit Pin definitions
#define SWITCH_RIGHT_PIN 25
#define SWITCH_LEFT_PIN 26
#define LED_PAN_PIN 27
#define LED_ZOOM_PIN 32
#define LED_ORBIT_PIN 33

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

// Global variables for interrupt
volatile byte modeCounter = 0;

// Global variables
byte modeNumber = 0;
static const int SPI_CLK = 1000000; // 8 MHz
int xPrev = 0, yPrev = 0, zPrev = 0;
char incomingChar = '\0';


void setup() {
    Serial.begin(115200);

    disableCore0WDT();

    //initialize instance of the SPIClass attached to HSPI
    hspi = new SPIClass(HSPI);

//    #ifndef ALTERNATE_PINS
//        //initialise hspi with default pins
//        //SCLK = 14, MISO = 12, MOSI = 13, SS = 15
//        hspi->begin();
//    #else
        //alternatively route through GPIO pins
        hspi->begin(HSPI_SCLK, HSPI_MISO, HSPI_MOSI, HSPI_SS); //SCLK, MISO, MOSI, SS
//    #endif
  
    pinMode(X_CS_PIN, OUTPUT);
    pinMode(Y_CS_PIN, OUTPUT);
    pinMode(Z_CS_PIN, OUTPUT);

    digitalWrite(X_CS_PIN, HIGH);
    digitalWrite(Y_CS_PIN, HIGH);
    digitalWrite(Z_CS_PIN, HIGH);

    pinMode(SWITCH_RIGHT_PIN, INPUT);
    pinMode(SWITCH_LEFT_PIN, INPUT);
    attachInterrupt(SWITCH_RIGHT_PIN, updateSwitchRight, RISING);
    attachInterrupt(SWITCH_LEFT_PIN, updateSwitchLeft, RISING);
    
    pinMode(LED_PAN_PIN, OUTPUT);
    pinMode(LED_ZOOM_PIN, OUTPUT);
    pinMode(LED_ORBIT_PIN, OUTPUT);
  
    ledsOff();

    delay(2000);
}

void loop() {

    // recieved new command
    if (Serial.available() > 0) {
      incomingChar = Serial.read();

      if (incomingChar == 'w') {  // recieved 'w' command
        // send data request to mouse, get new data
        modeNumber = modeCounter % 3;
        updateLeds();
        sendData();     // send new data
      }
    }
}

void sendData(){
    // USED FOR DEBUGGING
//    unsigned long startTime = micros();
    
    int xPos = getData(X_CS_PIN, ANGLECOM_REG);
    int yPos = getData(Y_CS_PIN, ANGLECOM_REG);
    int zPos = getData(Z_CS_PIN, ANGLECOM_REG);

    int xRel, yRel, zRel;
    if(xPos == -1){
        getData(X_CS_PIN, ERRFL_REG);
        xRel = 0;
    }
    else{
        xRel = calcRelData(xPos, &xPrev);
    }
    if(yPos == -1){
        getData(Y_CS_PIN, ERRFL_REG);
        yRel = 0;
    }
    else{
        yRel = calcRelData(yPos, &yPrev);
    }
    if(zPos == -1){
        getData(Z_CS_PIN, ERRFL_REG);
        zRel = 0;
    }
    else{
        zRel = calcRelData(zPos, &zPrev);
    }

    // send mode\tx\ty\tz\n
    Serial.print(modeNumber, DEC);
    //Serial.print(2, DEC);
    Serial.print('\t');
    Serial.print(xRel, DEC);
    Serial.print('\t');
    Serial.print(yRel, DEC);
    Serial.print('\t');
    Serial.print(zRel, DEC);
    Serial.print('\n');

    // USED FOR DEBUGGING
//    unsigned long endTime = micros();
//    unsigned long elapsedTime = (endTime - startTime);
//    Serial.print("Elapsed time to read positions: ");
//    Serial.print(elapsedTime);
//    Serial.println(" microsecs");
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
  
    SPISettings spiSettings(SPI_CLK, MSBFIRST, SPI_MODE1);
    
    addrToRead = getAddrWParity(addrToRead);
    
    hspi->beginTransaction(spiSettings);
    digitalWrite(csPin, LOW);
    hspi->transfer16(addrToRead); // Set read address
    digitalWrite(csPin, HIGH);
    digitalWrite(csPin, LOW);
    int data = hspi->transfer16(0xC000); // Read data with no-op command
    digitalWrite(csPin, HIGH);
    hspi->endTransaction();

    // USED FOR DEBUGGING
    Serial.print("Raw Data: ");
    Serial.println(data, BIN);
    
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
    // Serial.println("Orbit LED");
    digitalWrite(LED_ORBIT_PIN, HIGH);
    digitalWrite(LED_PAN_PIN, LOW);
    digitalWrite(LED_ZOOM_PIN, LOW);
  }
  else if(modeNumber == 1){
    // Serial.println("Pan LED");
    digitalWrite(LED_ORBIT_PIN, LOW);
    digitalWrite(LED_PAN_PIN, HIGH);
    digitalWrite(LED_ZOOM_PIN, LOW);
  }
  else if(modeNumber == 2){
    // Serial.println("Zoom LED");
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
