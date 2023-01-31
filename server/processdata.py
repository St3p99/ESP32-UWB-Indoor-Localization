import json
import threading
from json import JSONDecodeError
from threading import Thread

import paho.mqtt.client as mqttClient


class ProcessData(Thread):
    TOPIC_UWB_DATA = "UWB_TAG"
    TOPIC_IMU_DATA = "IMU_DATA"
    DEBUG = False

    def __init__(self, server):
        threading.Thread.__init__(self, daemon=True)
        self.server = server
        self.client = mqttClient.Client("PythonServer-ProcessData", protocol=mqttClient.MQTTv31)

    def run(self):
        self.client.connect(self.server.broker_host, self.server.port)  # connect to broker
        self.client.on_connect = self.on_connect

        self.client.message_callback_add(ProcessData.TOPIC_UWB_DATA, self.on_uwb_data)
        self.client.message_callback_add(ProcessData.TOPIC_IMU_DATA, self.on_imu_data)

        self.client.loop_forever()

    def on_connect(self, client, userdata, flags, rc):  # The callback for when
        print("Connected to the broker with result code " + str(rc))
        self.client.subscribe(ProcessData.TOPIC_UWB_DATA)
        self.client.subscribe(ProcessData.TOPIC_IMU_DATA)

    def on_uwb_data(self, client, userdata, message):
        line = message.payload.decode("utf-8")
        if ProcessData.DEBUG: print(line)
        try:
            uwb_data = json.loads(line)
            if uwb_data["T"] not in self.server.tags:
                print("Tag not recognized")
            else:
                tag = self.server.tags[uwb_data["T"]]
                if uwb_data["A"] not in self.server.anchors:
                    print("Anchor not recognized")
                    return

                position_changed = tag.add_measurement(self.server.anchors[uwb_data["A"]], float(uwb_data["R"]))
                if position_changed and self.server.visualizer is not None:
                    self.server.visualizer.update_tag(tag)
                elif position_changed:
                    print(tag.get_last_position())
        except JSONDecodeError as e:
            print(e)
            print("exception:" + line)

    def on_imu_data(self, client, userdata, message):
        line = message.payload.decode("utf-8")
        if ProcessData.DEBUG: print(line)
        try:
            imu_data = json.loads(line)
            if imu_data["T"] not in self.server.tags:
                print("Tag not recognized")
            else:
                tag = self.server.tags[imu_data["T"]]
                tag.add_imu_measurement(imu_data)
        except JSONDecodeError as e:
            print(e)
            print("exception:" + line)
