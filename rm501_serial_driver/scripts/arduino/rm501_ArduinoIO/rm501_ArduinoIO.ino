  bool D2 = 1;
  bool D2_prev = 1;

void setup() {

  // start serial port at 9600 bps and wait for port to open:
  Serial.begin(115200);
  while (!Serial) {
    ; // wait for serial port to connect. Needed for native USB port only
  }
  
  pinMode(2, INPUT_PULLUP);   // digital sensor is on digital pin 2
  
  getFirmwareVersion();       //Print version
}

void loop() {
  // We send the Digital Inputs Status when changes
  // Read Digital Pins
  
  D2 = digitalRead(2);

  // Send message if the Status changes
  if (D2 != D2_prev){
    if(D2 == 1){
      Serial.println("D2:OFF");
    }
    else{
      Serial.println("D2:ON");      
    }
    D2_prev = D2;
  }

  delay(10);
}

void getFirmwareVersion() {
  if (Serial.available() <= 0) {
    Serial.println("rm501_ArduinoIO v1.0");   // send an initial string
    delay(300);
    }
  }
