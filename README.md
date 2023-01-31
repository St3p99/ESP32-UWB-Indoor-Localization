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
    
    You can download the [binary package](https://mosquitto.org/download/) or download the [Docker based installation](https://docs.cedalo.com/management-center/2.4/installation/) which include also the Management Center and Eclipse Streamsheets.

2. Mosquitto Configuration
   - 'allow_anonymous true': Allows users to connect without authentication.
   - acl file: Restrict access to clients

# MQTT Tag
ESP32 UWB configured as a MQTT Tag:
   - connects to WiFI, 
   - establishes a connection with MQTT Broker
   - loops publishing last measurement to the broker on the 'UWB_TAG' topic.

# Python Server
   - connects to MQTT Broker
   - it subscribe to UWB_TAG tag and wait for the data
   - runs 3 threads: the main one run the Visualizer (Turtle 2D Tags and Anchors Visualizer), ProcessData to handle and process incoming data, StoreData to store every X mn tag positions on a CSV file. 

# Using Multiple Tags
Initially, running the first tests using multiple tags, we found the measurements to be unreliable due to overlapping signals sent simultaneously by the tags.

We have figured out a simple solution to solve the signal overlap problem. 

Since the DW1000 Library allows an anchor to perform the ranging process only with one tag at a time, we thought that the best solution was to implement an algorithm to synchronize tags sequentially, assigning them a time slot in which performs the ranging process.

In addition, we had to take in account that tags are dynamic device and can appear/disappear at any time.

The solution is implemented as follows:
-	Each tag on startup, and periodically (30sec), send a “Hello message” to notify the server his presence.
-	The server appends tags to a queue and sequentially distributes the token to allow the head tag to start the ranging process.
-	The tag performs the ranging process until the token expires (1sec), then send a message to notify the server the end of the ranging process.
-	The server run a thread that periodically removes inactive tags and tag died with the token.

All the communications happen via MQTT.
-	The tags publish “Hello message” on “TAG_DISCOVERY” topic.
-	The tags notify the server of the end of ranging process, publishing on “RANGING_TERMINATED” topic.
- The server subscribes to “TAG_DISCOVERY” and “RANGING_TERMINATED” topics.

# TODO
1. Calculate tags positions using 3 anchors and change, accordingly, Turtle visualization.
2. Add a timestamp to tag measurement messages.
3. Discard 'last measurements' if expired.
   NB: 'last measurements' should be used to calculate new tag positions, and they refers to different anchors.
       If a 'last measurement' is too old must be discarded.
    
    ```Python
    if new_measurement.timestamp - last_measurements[i].timestamp > expiring_time:
      discard last_measurement[i]
