/*
For ESP32 UWB or ESP32 UWB Pro
*/

#include <SPI.h>

#include <DW1000Ranging.h>
#include <WiFi.h>
#include <WiFiUdp.h>

// MQTT Library
#include <PubSubClient.h>

#define SPI_SCK 18
#define SPI_MISO 19
#define SPI_MOSI 23

#define PIN_RST 27 // reset pin
#define PIN_IRQ 34 // irq pin
#define PIN_SS 21  // spi select pin - UWB STANDARD: 4 - UWB PRO: 21

#define TAG_ADDR "8D:00:22:EA:82:60:3B:9B"

#define DEBUG false

const char *ssid = "TIM-23220228";
const char *password = "***";
const char *mqtt_broker_host = "192.168.1.53";
const int mqtt_broker_port = 1883;

WiFiClient espClient;
PubSubClient client(espClient);

//declare topic for publish_uwb_data message
const char* topic_uwb_data = "UWB_TAG";
const char* topic_tag_discovery = "TAG_DISCOVERY";
const char* topic_start_ranging = "START_RANGING";
const char* topic_ranging_terminated = "RANGING_TERMINATED";

long time_token_received = 0;
long token_period = 1*1000;
bool have_token = false;

long last_hello = 0;
long hello_period = 30*1000;  // 30sc

String json = "";
String old_json = "";

void setup()
{
    Serial.begin(115200);

    WiFi.mode(WIFI_STA);
    WiFi.setSleep(false);
    WiFi.begin(ssid, password);
    
    delay(1000);  // wait for serial monitor

    connect_to_wifi();
    client.setServer(mqtt_broker_host, mqtt_broker_port);
    client.setCallback(mqtt_callback);

    //init the configuration
    SPI.begin(SPI_SCK, SPI_MISO, SPI_MOSI);
    DW1000Ranging.initCommunication(PIN_RST, PIN_SS, PIN_IRQ);
    DW1000Ranging.attachNewRange(newRange);
    DW1000Ranging.attachNewDevice(newDevice);
    DW1000Ranging.attachInactiveDevice(inactiveDevice);

    //we start the module as a tag
    DW1000Ranging.startAsTag(TAG_ADDR, DW1000.MODE_LONGDATA_RANGE_LOWPOWER);
    client.publish(topic_tag_discovery, TAG_ADDR, true);
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

void reconnect() {
  // Loop until we're reconnected
  while (!client.connected())
  {
    Serial.print("Attempting MQTT connection...");
    // Create a random client ID
    String clientId = "ESP8266Client-";
    clientId += String(random(0xffff), HEX);
    // Attempt to connect
    //if you MQTT broker has clientID,username and password
    //please change following line to    if (client.connect(clientId,userName,passWord))
    if (client.connect(clientId.c_str()))
    {
      Serial.println("connected");
      //once connected to MQTT broker, subscribe command if any
      client.subscribe(topic_start_ranging);
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      // Wait 5 seconds before retrying
      delay(5000);
    }
  }
}

void loop()
{
    if (!client.connected()) {
      reconnect();
    }
    client.loop();

    if ( have_token && (millis() - time_token_received) < token_period)
    {
        if(DEBUG) Serial.println("loop...");
        DW1000Ranging.loop();
    }
    else if( have_token )
    { // ranging token_period expired
      have_token = false;
      if(DEBUG) Serial.println("RANGING TERMINATED");
      client.publish(topic_ranging_terminated, TAG_ADDR, true);
    }
    
    else if( (millis() - last_hello) > hello_period)
    { 
      if(DEBUG) Serial.println("HELLO!");
      client.publish(topic_tag_discovery, TAG_ADDR, true);
      last_hello = millis();
    }
    if( !json.equals("") ) 
      publish_uwb_data();

}

void mqtt_callback(char* topic, byte* payload, unsigned int length) {
  if( strcmp(topic, topic_start_ranging) == 0 && strncmp((char*) payload, TAG_ADDR, length) == 0){
        time_token_received = millis();
        have_token = true;
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
    
    strcpy(&old_json[0], &json[0]);
    make_json(&json,DW1000Ranging.getDistantDevice()->getShortAddress(), DW1000Ranging.getDistantDevice()->getRange(), DW1000Ranging.getDistantDevice()->getRXPower());
}

void make_json(String* s, uint16_t addr, float range, float dbm)
{
#ifdef SERIAL_DEBUG
    Serial.println("make_json");
#endif

    char buf[100];
    sprintf(buf, "{\"T\":\"%s\",\"A\":\"%X\",\"R\":\"%.1f\"}", TAG_ADDR, addr, range);
    *s = buf;
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


void publish_uwb_data()
{
  Serial.print("Publishing: ");
  Serial.println(json);
  bool sended = client.publish(topic_uwb_data, json.c_str(), true);
  if( sended ) Serial.println("Published");
}
