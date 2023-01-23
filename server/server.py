import json
from enum import Enum
from json import JSONDecodeError

import paho.mqtt.client as mqttClient

from anchor import Anchor
from processdata import ProcessData
from storedata import StoreData
from tag import Tag
from turtlevisualizer import TurtleVisualizer


class VisualizerType(Enum):
    TURTLE = 1


class Server:
    class VisualizerType(Enum):
        TURTLE = 1

    MQTT_TOPIC = "UWB_TAG"

    def __init__(self, broker_host, port, anchors, tags):
        self.broker_host = broker_host
        self.port = port
        self.anchors = {}
        self.tags = {}
        for a in anchors:
            self.anchors[a.get_addr()] = a
        for t in tags:
            self.tags[t.get_addr()] = t
        self.visualizer = None
        self.sock = None
        self.client = mqttClient.Client("PythonServer", protocol=mqttClient.MQTTv31)

    def get_anchors(self):
        return self.anchors

    def get_tags(self):
        return self.tags

    def set_visualizer(self, v: VisualizerType):
        if v == VisualizerType.TURTLE:
            self.visualizer = TurtleVisualizer(self.anchors.values())

    def start(self):
        self.client.connect(self.broker_host, self.port)  # connect to broker
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_subscribe = self.on_subscribe

        t1 = ProcessData(self)
        t1.start()

        t2 = StoreData(self)
        t2.start()

        self.visualize()

    def on_connect(self, client, userdata, flags, rc):  # The callback for when
        print("Connected to the broker with result code " + str(rc))
        self.client.subscribe(Server.MQTT_TOPIC)

    def on_subscribe(self, client, userdata, mid, granted_qos):
        print("Successfully subscribed to '{topic}' topic".format(topic=Server.MQTT_TOPIC))

    def on_message(self, client, userdata, message):
        line = message.payload.decode("utf-8")
        try:
            uwb_data = json.loads(line)
            if uwb_data["T"] not in self.tags:
                print("Tag not recognized")
            else:
                tag = self.tags[uwb_data["T"]]
                if uwb_data["A"] not in self.anchors:
                    print("Anchor not recognized")
                    return

                position_changed = tag.add_measurement(self.anchors[uwb_data["A"]], float(uwb_data["R"]))
                if position_changed and self.visualizer is not None:
                    self.visualizer.update_tag(tag)
                elif position_changed:
                    print(tag.get_last_position())
        except JSONDecodeError as e:
            print(e)
            print("exception:" + line)

    def visualize(self):
        if self.visualizer is not None:
            self.visualizer.show()


def main():
    # configure network
    HOST = "192.168.1.53"
    PORT = 1883

    # set anchors
    A1_ADDR = "1781"
    A2_ADDR = "1783"

    """
     NB: For now, it works with two anchors only:
           - A1 in axis origin
           - A2 must have y coordinate set to 0    
    """

    A1 = Anchor(A1_ADDR, 0, 0)
    A2 = Anchor(A2_ADDR, 3, 0)

    TAG1_ADDR = "7D:00:22:EA:82:60:3B:9B"
    TAG2_ADDR = "8D:00:22:EA:82:60:3B:9B"
    T1 = Tag("T1", TAG1_ADDR)
    T2 = Tag("T2", TAG2_ADDR)

    server = Server(HOST, PORT, [A1, A2], [T1, T2])
    server.set_visualizer(VisualizerType.TURTLE)
    server.start()


if __name__ == '__main__':
    main()
