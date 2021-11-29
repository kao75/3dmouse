

// Include the WiFi library and esp_now in this sketch
#include <esp_now.h>
#include <WiFi.h>
uint8_t transmitterAddress[] = {0x1C, 0x9D, 0xC2, 0x87, 0xDA, 0x8C};

typedef struct broadcastToTransmitter {
  char receiverChar;
} broadcastToTransmitter;
typedef struct incomingTransmitterMessage {
  int mode;
  int x;
  int y;
  int z;
} incomingTransmitterMessage;

broadcastToTransmitter WriteCommand;
incomingTransmitterMessage IncomingEncoderData;

// Callback when data is sent
void OnDataSent(const uint8_t *mac_addr, esp_now_send_status_t status) {
  Serial.print("\r\nLast Packet Send Status:\t");
  Serial.println(status == ESP_NOW_SEND_SUCCESS ? "Delivery Success" : "Delivery Fail");
}

// Callback when data is received
void OnDataRecv(const uint8_t * mac, const uint8_t *incomingData, int len) {
  memcpy(&IncomingEncoderData, incomingData, sizeof(IncomingEncoderData));
  Serial.print("Bytes received: ");
  Serial.println(len);
  int mode = IncomingEncoderData.mode;
  int x = IncomingEncoderData.x;
  int y = IncomingEncoderData.y;
  int z = IncomingEncoderData.z;
  sendDataSerial(mode, x, y, z);
}


void setup() {
    Serial.begin(115200);

    // Set WiFi mode and initialize ESP-NOW
    WiFi.mode(WIFI_MODE_STA);
    if (esp_now_init() != ESP_OK) {
      Serial.println("Error initializing ESP-NOW");
      return;
    }
    // Once ESPNow is successfully Init, we will register for Send CB to get the status of Trasnmitted packet
    esp_now_register_send_cb(OnDataSent);
    // Register peer
    esp_now_peer_info_t peerInfo;
    memcpy(peerInfo.peer_addr, transmitterAddress, 6);
    peerInfo.channel = 0;  
    peerInfo.encrypt = false;
    // Add peer        
    if (esp_now_add_peer(&peerInfo) != ESP_OK){
      Serial.println("Failed to add peer");
      return;
    }
    // Register for a callback function that will be called when data is received
    esp_now_register_recv_cb(OnDataRecv);

}

void loop() {
    // recieved new command
    if (Serial.available() > 0) {
      incomingChar = Serial.read();

      if (incomingChar == 'w') {  // recieved 'w' command		
		// Send message to transmitter requesting new data via ESP-NOW
		WriteCommand.receiverChar = 'w';
		esp_err_t result = esp_now_send(receiverAddress, (uint8_t *) &WriteCommand, sizeof(WriteCommand));
      }
    }
    delay(100);
}

void sendDataSerial(int mode, int x, int y, int z) {
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







