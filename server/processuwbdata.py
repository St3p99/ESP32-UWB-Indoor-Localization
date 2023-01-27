import json
import threading
from json import JSONDecodeError
from threading import Thread
import paho.mqtt.client as mqttClient


class ProcessUWBData(Thread):

    TOPIC_UWB_DATA = "UWB_TAG"

    def __init__(self, server):
        threading.Thread.__init__(self, daemon=True)
        self.server = server
        self.client = mqttClient.Client("PythonServer-ProcessUWBData", protocol=mqttClient.MQTTv31)

    def run(self):
        self.client.connect(self.server.broker_host, self.server.port)  # connect to broker
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_subscribe = self.on_subscribe

        self.client.loop_forever()

    def on_connect(self, client, userdata, flags, rc):  # The callback for when
        print("Connected to the broker with result code " + str(rc))
        self.client.subscribe(ProcessUWBData.TOPIC_UWB_DATA)

    def on_subscribe(self, client, userdata, mid, granted_qos):
        print("Successfully subscribed to '{topic}' topic".format(topic=ProcessUWBData.TOPIC_UWB_DATA))

    def on_message(self, client, userdata, message):
        line = message.payload.decode("utf-8")
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