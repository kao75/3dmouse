/*
 * 3DMouseDevice.ino
 * Created By: Dylan Butler
 * Last Modified: 11/29/2021
 */

// Include the SPI library in this sketch
#include "SPI.h"

// Define SPI Pin definitions
// Set chip select pin to pin 4 so built-in SPI doesn't interfere with X_CS_PIN
#define HSPI_MISO   12
#define HSPI_MOSI   13
#define HSPI_SCLK   14
#define HSPI_SS     4   // IO4 is not used in our circuit

// Define SPI Chip Select Pin definitions
#define X_CS_PIN 15
#define Y_CS_PIN 16
#define Z_CS_PIN 17

// Switch Circuit Pin definitions
#define SWITCH_RIGHT_PIN 26
#define SWITCH_LEFT_PIN 25
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

// Relative change calculation values
#define WRAP_VALUE 8192
#define MAX_VALUE 16384

// Uninitalized pointer to SPI object
SPIClass * hspi = NULL;

// Global variables for interrupt
volatile byte modeCounter = 0;

// Global variables
byte modeNumber = 0;
static const uint16_t SPI_CLK = 8000000; // 8 MHz
uint16_t xPrev = 0, yPrev = 0, zPrev = 0;
char incomingChar = '\0';


void setup() {
    Serial.begin(115200);

    disableCore0WDT();

    // Initialize instance of the SPIClass attached to HSPI
    hspi = new SPIClass(HSPI);
    hspi->begin(HSPI_SCLK, HSPI_MISO, HSPI_MOSI, HSPI_SS); //SCLK, MISO, MOSI, SS

    // Set SPI Chip Select pin directions
    pinMode(X_CS_PIN, OUTPUT);
    pinMode(Y_CS_PIN, OUTPUT);
    pinMode(Z_CS_PIN, OUTPUT);

    // Set SPI pin directions
    pinMode(HSPI_MISO, INPUT);
    pinMode(HSPI_MOSI, OUTPUT);
    pinMode(HSPI_SCLK, OUTPUT);

    // Pull Chip Select pins high
    digitalWrite(X_CS_PIN, HIGH);
    digitalWrite(Y_CS_PIN, HIGH);
    digitalWrite(Z_CS_PIN, HIGH);

    // Set Button directions and setup interrupts
    pinMode(SWITCH_RIGHT_PIN, INPUT);
    pinMode(SWITCH_LEFT_PIN, INPUT);
    attachInterrupt(SWITCH_RIGHT_PIN, updateSwitchRight, RISING);
    attachInterrupt(SWITCH_LEFT_PIN, updateSwitchLeft, RISING);

    // Set LED pin directions
    pinMode(LED_PAN_PIN, OUTPUT);
    pinMode(LED_ZOOM_PIN, OUTPUT);
    pinMode(LED_ORBIT_PIN, OUTPUT);

    // Blink all LEDs
    // Init LEDs to off
    ledsOn();
    delay(1000);
    ledsOff();
}

void loop() {

    // Recieved new command
    if (Serial.available() > 0) {
        incomingChar = Serial.read();

        // Recieved 'w' command
        if (incomingChar == 'w') {
            // Send data request to mouse, get new data
            modeNumber = modeCounter % 3;
            updateLeds();
            sendData();     // Send new data
        }
    }
}

void sendData(){
    // USED FOR DEBUGGING
    // unsigned long startTime = micros();

    // Get position data from encoders
    uint16_t xPos = getData(X_CS_PIN, ANGLECOM_REG);
    uint16_t yPos = getData(Y_CS_PIN, ANGLECOM_REG);
    uint16_t zPos = getData(Z_CS_PIN, ANGLECOM_REG);

    // Calculate relative position change from encoders
    int16_t xRel, yRel, zRel;
    if(xPos == 0xFFFF){
        getData(X_CS_PIN, ERRFL_REG);
        xRel = 0;
    }
    else{
        xRel = calcRelData(xPos, &xPrev);
    }
    if(yPos == 0xFFFF){
        getData(Y_CS_PIN, ERRFL_REG);
        yRel = 0;
    }
    else{
        yRel = calcRelData(yPos, &yPrev);
    }
    if(zPos == 0xFFFF){
        getData(Z_CS_PIN, ERRFL_REG);
        zRel = 0;
    }
    else{
        zRel = calcRelData(zPos, &zPrev);
    }

    // Send mode\tx\ty\tz\n
    Serial.print(modeNumber, DEC);
    Serial.print('\t');
    Serial.print(xRel, DEC);
    Serial.print('\t');
    Serial.print(yRel, DEC);
    Serial.print('\t');
    Serial.print(zRel, DEC);
    Serial.print('\n');

    // USED FOR DEBUGGING
    // unsigned long endTime = micros();
    // unsigned long elapsedTime = (endTime - startTime);
    // Serial.print("Elapsed time to read positions: ");
    // Serial.print(elapsedTime);
    // Serial.println(" microsecs");
}

// Calculate whether we wrapped over the absolute min/max threshold
int16_t isWrapAround(uint16_t val, uint16_t valPrev){
    int16_t valRel = val - valPrev;

    if(abs(valRel) < WRAP_VALUE){
        return 0;
    }
    
    return valRel;
}

// Calculate relative change in encoder position based on current and previous value
int16_t calcRelData(uint16_t val, uint16_t * valPrev){
    int16_t valRel = val - *valPrev;
    int16_t wrapAround = isWrapAround(val, *valPrev);
    
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

// Use SPI library to get data from encoders
uint16_t getData(uint16_t csPin, uint16_t addrToRead){

    // Get address with correct parity
    addrToRead = getAddrWParity(addrToRead);

    // Use SPI transfers to get data
    hspi->beginTransaction(SPISettings(SPI_CLK, MSBFIRST, SPI_MODE1));
    digitalWrite(csPin, LOW);
    hspi->transfer16(addrToRead); // Set read address
    digitalWrite(csPin, HIGH);
    delayMicroseconds(1);
    digitalWrite(csPin, LOW);
    uint16_t data = hspi->transfer16(0xC000); // Read data with no-op command
    digitalWrite(csPin, HIGH);
    hspi->endTransaction();

    // USED FOR DEBUGGING
    // Serial.print("Raw Data: ");
    // Serial.println(data, BIN);
    
    // Check for parity errors
    return ((data >> AS5147_REG_SIZE) & 0x1 ? 0xFFFF : data & 0x3FFF);
}

// Take in address and calculate address to read with correct parity bit setting
uint16_t getAddrWParity(uint16_t addrToRead){
    uint16_t bitCount = 0;
    addrToRead |= 0x4000; // Set Read bit in command frame
    uint16_t bitsToCount = addrToRead;
    for(int16_t i = AS5147_REG_SIZE; i > 0; i--){
        bitCount += (addrToRead & 1 ? 1 : 0);
        bitsToCount >>= 1;
    }

    return (bitCount % 2 ? addrToRead : addrToRead | 0x8000);
}

// ISR for "right" switch
void updateSwitchRight(){
  if(++modeCounter == 255){
    modeCounter = 0;
  }
}

// ISR for "left" switch
void updateSwitchLeft(){
  if(--modeCounter == 255){
    modeCounter = 254;
  }
}

// Update LEDs according to current mode
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

// Turn all LEDs off
void ledsOff(){
  digitalWrite(LED_PAN_PIN, LOW);
  digitalWrite(LED_ZOOM_PIN, LOW);
  digitalWrite(LED_ORBIT_PIN, LOW);
}

// Turn all LEDs on
void ledsOn(){
  digitalWrite(LED_PAN_PIN, HIGH);
  digitalWrite(LED_ZOOM_PIN, HIGH);
  digitalWrite(LED_ORBIT_PIN, HIGH);
}
