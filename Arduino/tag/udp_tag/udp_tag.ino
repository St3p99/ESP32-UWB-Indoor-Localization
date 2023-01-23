/*
For ESP32 UWB or ESP32 UWB Pro
*/

#include <SPI.h>
#include <DW1000Ranging.h>
#include <WiFi.h>
#include <WiFiUdp.h>
// #include "link.h"

#define SPI_SCK 18
#define SPI_MISO 19
#define SPI_MOSI 23

#define PIN_RST 27 // reset pin
#define PIN_IRQ 34 // irq pin
#define PIN_SS 21  // spi select pin - UWB STANDARD: 4 - UWB PRO: 21

#define TAG_ADDR "8D:00:22:EA:82:60:3B:9B"

const char *ssid = "TIM-23220228";
const char *password = "XZJXPHtAZndkkazkGhdzg9GM";
const char *host = "192.168.1.53";
const int udpPort = 5001;

//The udp library class
WiFiUDP udp;

long runtime = 0;
long period = 1000;
String all_json = "";

void setup()
{
    Serial.begin(115200);

    WiFi.mode(WIFI_STA);
    WiFi.setSleep(false);
    WiFi.begin(ssid, password);
    
    delay(1000);  // wait for serial monitor

    connect_to_wifi();
    
    //This initializes udp and transfer buffer
    udp.begin(udpPort);

    //init the configuration
    SPI.begin(SPI_SCK, SPI_MISO, SPI_MOSI);
    DW1000Ranging.initCommunication(PIN_RST, PIN_SS, PIN_IRQ);
    DW1000Ranging.attachNewRange(newRange);
    DW1000Ranging.attachNewDevice(newDevice);
    DW1000Ranging.attachInactiveDevice(inactiveDevice);

    //we start the module as a tag
    DW1000Ranging.startAsTag(TAG_ADDR, DW1000.MODE_LONGDATA_RANGE_LOWPOWER);
}

void connect_to_wifi()
{
 while (WiFi.status() != WL_CONNECTED)
    {
        delay(500);
        Serial.print(".");
    }
    Serial.println("Connected to WiFi");
    Serial.print("IP Address:");
    Serial.println(WiFi.localIP());  
}

void loop()
{
    DW1000Ranging.loop();
    if ((millis() - runtime) > period)
    {
        if(all_json != "") send_udp(&all_json);
        runtime = millis();
    }
}

void newRange()
{
    Serial.print("from: ");
    Serial.print(DW1000Ranging.getDistantDevice()->getShortAddress(), HEX);
    Serial.print("\t Range: ");
    Serial.print(DW1000Ranging.getDistantDevice()->getRange());
    Serial.print(" m");
    Serial.print("\t RX power: ");
    Serial.print(DW1000Ranging.getDistantDevice()->getRXPower());
    Serial.println(" dBm");
    
    make_json(&all_json, DW1000Ranging.getDistantDevice()->getShortAddress(), DW1000Ranging.getDistantDevice()->getRange(), DW1000Ranging.getDistantDevice()->getRXPower());
}

void make_json(String* s, uint16_t addr, float range, float dbm)
{
#ifdef SERIAL_DEBUG
    Serial.println("make_json");
#endif

    char json[100];
    sprintf(json, "{\"T\":\"%s\",\"A\":\"%X\",\"R\":\"%.1f\"}", TAG_ADDR, addr, range);
    *s = json;
    Serial.println(*s);

}

void newDevice(DW1000Device *device)
{
    Serial.print("ranging init; 1 device added ! -> ");
    Serial.print(" short:");
    Serial.println(device->getShortAddress(), HEX);
}

void inactiveDevice(DW1000Device *device)
{
    Serial.print("delete inactive device: ");
    Serial.println(device->getShortAddress(), HEX);
}


void send_udp(String *msg_json)
{
  udp.beginPacket(host, udpPort);
  udp.print(*msg_json);
  udp.endPacket();
  Serial.println("UDP send");
}
