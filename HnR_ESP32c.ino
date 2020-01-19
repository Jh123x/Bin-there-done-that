#include <WiFi.h>
char* ssid = "Bin there done that";
char* pass = "qwerty1234!";
int status = WL_IDLE_STATUS;
const char* host = "192.168.1.47";

WiFiClient client;

//For Ultrasonic
// defines pins numbers
const int trigPin = 22;
const int echoPin = 23;

// defines variables
long duration;
int distance;
int new_dist;

//For Zone division
int zone_div[6] = {143, 120, 93, 68, 40, 15};
int new_zone_ar[12] = {3,5,2,4,2,5,6,4,3,1,4,5,};
int new_zone;
int nz = 0;
int recv_zone = -1;

// Motor
int motor1Pin1 = 27;
int motor1Pin2 = 26;
int enable1Pin = 14;
int motor2Pin3 = 25;
int motor2Pin4 = 33;
int enable2Pin = 32;

// Setting PWM properties
const int freq = 30000;
const int pwmChannel = 0;
const int resolution = 8;

const int default_dutyCycle = 255;

int dutyCycle = default_dutyCycle;

int forward=-1;

void setup() {
  
  
  Serial.begin(115200);
    //WIFI STUFF
  WiFi.begin(ssid,pass);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Establishing connection to WiFi..");
  }
  Serial.println("Connected to the network");

  while (!client.connect(host,1234));
  Serial.println("Connecting to host");
  Serial.println("Connected to host");

  
  //For ultrasonic
  pinMode(trigPin, OUTPUT); // Sets the trigPin as an Output
  pinMode(echoPin, INPUT); // Sets the echoPin as an Input

  
  // sets the pins as outputs:
  pinMode(motor1Pin1, OUTPUT);
  pinMode(motor1Pin2, OUTPUT);
  pinMode(enable1Pin, OUTPUT);

  pinMode(motor2Pin3, OUTPUT);
  pinMode(motor2Pin4, OUTPUT);
  pinMode(enable2Pin, OUTPUT);

  // configure LED PWM functionalitites
  ledcSetup(pwmChannel, freq, resolution);

  // attach the channel to the GPIO to be controlled
  ledcAttachPin(enable1Pin, pwmChannel);
  ledcAttachPin(enable2Pin, pwmChannel);
  // testing
  Serial.print("Testing DC Motor...");
}

void loop() {
  
  while (!(client.connected())){
    client.connect(host,1234);
  }
  
  Serial.println("Client Connected");
  if (recv_zone < 1){     
    String line = client.readStringUntil('\n');
    Serial.print("Received: ");
    Serial.println(line + "\n");
    recv_zone = line.toInt();
  }

  Serial.println("recv_zone ");
  Serial.print(recv_zone);
  if (recv_zone>=1){  
  //For ultrasonic
  // Clears the trigPin
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  
  // Sets the trigPin on HIGH state for 10 micro seconds
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);
  
  // Reads the echoPin, returns the sound wave travel time in microseconds
  duration = pulseIn(echoPin, HIGH);
  
  // Calculating the distance
  distance= duration*0.034/2;
  
  // Prints the distance on the Serial Monitor
  Serial.print("Distance: ");
  Serial.println(distance);

  //WAIT FOR WHERE THE HELL THE BALLOON IS LANDING
  //new_zone = new_zone_ar[nz];
  new_zone = recv_zone;
  new_dist = zone_div[new_zone-1];
  
  Serial.print("New Dist: ");
  Serial.println(new_dist);
  Serial.print("New Zone: ");
  Serial.println(new_zone);  
  
  if (new_dist < distance){
      if (forward != 1){
        moveForward();  
        forward = 1;
      }
  }
  else if ((distance < new_dist+2)&&(distance > new_dist-2)){
      moveStop();
      //delay(500);
      forward = -1;
      //nz++;
      recv_zone = -1;
  }

  else if (new_dist > distance){
    if (forward != 0){
      moveBackward();
      forward = 0;  
    }
  }
  //delay(100);

  dutyCycle = default_dutyCycle;
  }
}


void moveForward(){
  
  ledcWrite(pwmChannel, dutyCycle);
  Serial.println("Moving Forward");
  digitalWrite(motor1Pin1, HIGH);
  digitalWrite(motor1Pin2, LOW);
  digitalWrite(motor2Pin3, HIGH);
  digitalWrite(motor2Pin4, LOW);
  // delay(4750);
}

void moveBackward(){
   ledcWrite(pwmChannel, dutyCycle);  
   Serial.println("Moving Backward");
   digitalWrite(motor1Pin1, LOW);
   digitalWrite(motor1Pin2, HIGH);
   digitalWrite(motor2Pin3, LOW);
   digitalWrite(motor2Pin4, HIGH);
   // delay(4750);
}
  
void moveStop(){
  ledcWrite(pwmChannel, dutyCycle);
  Serial.println("Motor stopped");
  digitalWrite(motor1Pin1, LOW);
  digitalWrite(motor1Pin2, LOW);
  digitalWrite(motor2Pin3, LOW);
  digitalWrite(motor2Pin4, LOW);
}
