
// Include the WiFi library and esp_now in this sketch
#include <esp_now.h>
#include <WiFi.h>

uint8_t receiverAddress[] = {0x84, 0xCC, 0xA8, 0x47, 0xD4, 0x7C};

typedef struct broadcastToReceiver {
  int mode;
  int x;
  int y;
  int z;
} broadcastToReceiver;
typedef struct incomingReceiverMessage {
  char receiverChar;
} incomingReceiverMessage;

broadcastToReceiver EncoderData;
incomingReceiverMessage IncomingReceiverCommand;

// Callback when data is sent
void OnDataSent(const uint8_t *mac_addr, esp_now_send_status_t status) {
  Serial.print("\r\nLast Packet Send Status:\t");
  Serial.println(status == ESP_NOW_SEND_SUCCESS ? "Delivery Success" : "Delivery Fail");
}

// Callback when data is received
void OnDataRecv(const uint8_t * mac, const uint8_t *incomingData, int len) {
  memcpy(&IncomingReceiverCommand, incomingData, sizeof(IncomingReceiverCommand));
  Serial.print("Bytes received: ");
  Serial.println(len);
  char receiverChar = IncomingReceiverCommand.receiverChar;
  if (receiverChar == 'w') {
	sendData();
  }
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
    memcpy(peerInfo.peer_addr, receiverAddress, 6);
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

void sendData() {
	// update EncoderData varaible with current encoder values
	EncoderData.mode = 2;
    EncoderData.x = 111;
    EncoderData.y = 222;
    EncoderData.z = 333;
    // Send encoder data message via ESP-NOW
    esp_err_t result = esp_now_send(receiverAddress, (uint8_t *) &EncoderData, sizeof(EncoderData));
     
    if (result == ESP_OK) {
      Serial.println("Sent with success");
    }
    else {
      Serial.println("Error sending the data");
    }
}







