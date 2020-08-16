/* This sketch is to combine the radio operations of an RFM69HCW and the weather data from a BME280 plus the distance information from
   a Maxbotix MB7060 range sensor.


   -----------------------------Implemented---------------------------------------------
   Initialize radio
   Initialize BME280
   Periodically read from BME280
   Report BME280 results in a text string
   Send text string out on radio to base station
   Read from distance sensor
   Send distance report out on radio
   Power down and wake radio
   Power down and wake MCU

   -----------------------------In work--------------------------------------------------
   Power down and wake BME280
   Power down and wake range sensor


*/

//Required libraries
#include <SPI.h>
#include <RH_RF69.h>
#include <stdlib.h>
#include <Wire.h>
#include <BME280I2C.h>
#include <EnvironmentCalculations.h>
#include <QuickStats.h>
#include <Adafruit_SleepyDog.h>


//Set radio frequency
#define RF69_FREQ 915.0

//Define pins for RH_RF69 library
#define RFM69_INT     3
#define RFM69_CS      4
#define RFM69_RST     10

// Singleton instance of the radio driver
RH_RF69 rf69(RFM69_CS, RFM69_INT);

BME280I2C bme;    // Default : forced mode, standby time = 1000 ms
// Oversampling = pressure ×1, temperature ×1, humidity ×1, filter off,
bool metric = false;

// variables for BME280
float pres, temp, hum, dewPoint;

// variables for tide
float absMedianDist, absMaxDist, datumDist;
float lastAbsDist = 0;
float rawPWM[9];

QuickStats stats;

int counter = 0;

void setup() {
  delay(500);
  Serial.begin(115200);
  Wire.begin();

  // Set reset pin to low to enable radio
  pinMode(RFM69_RST, OUTPUT);

  // manual reset
  digitalWrite(RFM69_RST, HIGH);
  delay(10);
  digitalWrite(RFM69_RST, LOW);
  delay(10);

  if (!rf69.init()) {
    Serial.println("RFM69 radio init failed");
    while (1);
  }
  Serial.println("RFM69 radio init OK!");

  // Defaults after init are 434.0MHz, modulation GFSK_Rb250Fd250, +13dbM (for low power module)
  // No encryption
  if (!rf69.setFrequency(RF69_FREQ)) {
    Serial.println("setFrequency failed");
  }

  //Set radio output power. Option is -18 to +20) with ishighpowermodule=true
  rf69.setTxPower(15, true);
  rf69.sleep();

  Serial.print("RFM69 radio @");  Serial.print((int)RF69_FREQ);  Serial.println(" MHz");

  while (!bme.begin())
  {
    Serial.println("Could not find BME280 sensor!");
    delay(1000);
  }
  // ----------- Set RX pin to INPUT --------------------
  pinMode(6, INPUT);
  pinMode(5, OUTPUT);
  digitalWrite(5, LOW);

}

void loop() {
  int sleepMS = Watchdog.sleep(8000);

  counter = counter + sleepMS;

  if (counter >= 28000) {
    envUpdate();
    getDist();

    //Group the 'sends' in order to 'sleep' the radio
    sendWx();
    delay(250);
    sendDist();
    delay(250);

    counter = 0;

    Serial.println("Sleep the radio");
    rf69.sleep();
  }



  /*  //Wait for a reply
    uint8_t buf[RH_RF69_MAX_MESSAGE_LEN];
    uint8_t len = sizeof(buf);

    if (rf69.waitAvailableTimeout(500)) {
      //After 1/2 a second, there should be a message
      if (rf69.recv(buf, &len)) {
        Serial.print("Got a reply: ");
        Serial.println((char*)buf);
      }
      else {
        Serial.println("Receive failed");
      }
    } else {
      Serial.println("No reply, is another RFM69 listening?");
    }*/
}


// Function for retrieving temp/baro/humidity
// requires functional check for data
void envUpdate() {
  uint8_t pressureUnit(2);
  bme.read(pres, temp, hum, BME280::TempUnit_Fahrenheit, BME280::PresUnit_inHg );
  delay(200);
  bme.read(pres, temp, hum, BME280::TempUnit_Fahrenheit, BME280::PresUnit_inHg );
  dewPoint = EnvironmentCalculations::DewPoint(temp, hum, metric);
}

// Function for retrieving tide level
// tide array = 9 elements, 50 ms delay?
void getDist() {
  digitalWrite(5, HIGH);
  for (int x = 0; x < 9; x++) {
    //Serial.println("Waiting for input");
    rawPWM[x] = pulseIn(6, HIGH);
    delay(50);
  }
  float medianPWM = stats.median(rawPWM, 9);
  float maxPWM = stats.maximum(rawPWM, 9);
  absMedianDist = medianPWM / 147;
  absMaxDist = maxPWM / 147;
  //Serial.println("Input completed");
  digitalWrite(5, LOW);
}

void sendWx() {
  char wxreport[50];
  char tempbuf[6];
  char humbuf[6];
  char presbuf[5];
  char dpbuf[5];

  //Convert measurements to char arrays
  dtostrf(temp, 0, 1, tempbuf);
  dtostrf(hum, 0, 1, humbuf);
  dtostrf(pres, 0, 2, presbuf);
  dtostrf(dewPoint, 0, 1, dpbuf);

  Serial.println("Weather buffer's constructed");

  strcpy(wxreport, "{\"type\":\"wx\"");
  strcat(wxreport, ",\"t\":\"");
  strcat(wxreport, tempbuf);
  strcat(wxreport, "\",\"h\":\"");
  strcat(wxreport, humbuf);
  strcat(wxreport, "\",\"p\":\"");
  strcat(wxreport, presbuf);
  strcat(wxreport, "\",\"dp\":\"");
  strcat(wxreport, dpbuf);
  strcat(wxreport, "\"}");

  Serial.print("Sending"); Serial.println(wxreport);

  //Send the message
  rf69.send((uint8_t *)wxreport, strlen(wxreport));
  rf69.waitPacketSent();
}

void sendDist() {
  char distreport[20];
  char distbuf[5];

  dtostrf(absMedianDist, 0, 1, distbuf);

  Serial.println("Tide buffer's constructed");

  strcpy(distreport, "{\"type\":\"dist\"");
  strcat(distreport, ", \"d\":\"");
  strcat(distreport, distbuf);
  strcat(distreport, "\"}");

  Serial.print("Sending"); Serial.println(distreport);

  //Send the message
  rf69.send((uint8_t *)distreport, strlen(distreport));
  rf69.waitPacketSent();
}
