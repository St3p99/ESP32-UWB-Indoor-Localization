# ESP32-UWB-Indoor-Localization
 
# Setup ESP32 Board and Arduino libraries
1. Install ESP32 in Arduino 2.0 https://randomnerdtutorials.com/installing-esp32-arduino-ide-2-0/
2. Download DW1000 library for ESP32 from https://github.com/Makerfabs/Makerfabs-ESP32-UWB

Other useful libraries:
 - Adafruit_SSD1306 (to use the ESP32 board display)
 - PubSubClient (to establish MQTT connections)
 
 You can find all the libraries in Arduino/libraries
 
 # Mosquitto Broker
 1. Download Eclipse Mosquitto Broker 
 You can download the [binary package](https://mosquitto.org/download/) or download the Docker based installation which include also the Management Center and Eclipse Streamsheets.

2. Mosquitto Configuration
- 'allow_anonymous true': Allows users to connect without authentication.
- acl file: Restrict access to clients

# MQTT Tag
ESP32 UWB configured as a MQTT Tag:
- connects to WiFI, 
- establish a connection with MQTT Broker
- loop publishing last measurement to the broker on the 'UWB_TAG' topic.

# Python Server
- it connects to MQTT Broker
- it subscribe to UWB_TAG tag and wait for the data
- runs 3 threads, the main one run the Visualizer (Turtle 2D Tags and Anchors Visualizer), ProcessData to handle and process incoming data, StoreData to store every X mn tag positions on a CSV file. 

# TODO
1. Calculate tags positions using multiple anchors
2. Add a timestamp to tag measurement messages
3. Discard 'last measurements' if expired.
   NB: 'last measurements' should be used to calculate new tag positions, and they refers to different anchors.
       If a 'last measurement' is too old must be discarded.
    
    ```Python
    if new_measurements.timestamp - last_measurements[i].timestamp > expiring_time:
      discard last_measurement[i]
    ```