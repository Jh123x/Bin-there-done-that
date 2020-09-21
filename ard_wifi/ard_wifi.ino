#include <WiFi.h>

char* ssid = "Bin there done that";
char* pass = "qwerty1234!";
int status = WL_IDLE_STATUS;
const char* host = "192.168.1.47";

WiFiClient client;

void setup() {
 
  Serial.begin(9600);
  WiFi.begin(ssid,pass);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Establishing connection to WiFi..");
  }
  Serial.println("Connected to the network");
  Serial.println("Connecting to host");
  
  client.connect(host,1234);

  Serial.println("Connected to host");
  
}

void loop() {
  // put your main code here, to run repeatedly:
  if(client.connected()){
    String line = client.readStringUntil('\n');
    Serial.println(line + "\n");
  }else{
    Serial.println("No data received");
  }


}
