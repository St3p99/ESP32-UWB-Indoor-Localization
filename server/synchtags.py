from datetime import datetime, timedelta
import threading
from threading import Thread
import paho.mqtt.client as mqttClient



class SynchTags(Thread):
    TOPIC_TAG_DISCOVERY = "TAG_DISCOVERY"
    TOPIC_START_RANGING = "START_RANGING"
    TOPIC_RANGING_TERMINATED = "RANGING_TERMINATED"
    DEBUG = True
    def __init__(self, server):
        threading.Thread.__init__(self, daemon=True)
        self.server = server
        self.client = mqttClient.Client("PythonServer-SynchTags", protocol=mqttClient.MQTTv31)
        self.active_tags = []


    def run(self):
        self.client.connect(self.server.broker_host, self.server.port)  # connect to broker
        self.client.on_connect = self.on_connect
        self.client.message_callback_add(SynchTags.TOPIC_TAG_DISCOVERY, self.on_tag_discovery)
        self.client.message_callback_add(SynchTags.TOPIC_RANGING_TERMINATED, self.on_ranging_terminated)

        self.client.loop_forever()

    def on_connect(self, client, userdata, flags, rc):  # The callback for when
        if SynchTags.DEBUG: print("Connected to the broker with result code " + str(rc))
        self.client.subscribe(SynchTags.TOPIC_TAG_DISCOVERY, 0)
        self.client.subscribe(SynchTags.TOPIC_RANGING_TERMINATED, 0)

    def on_subscribe(self, client, userdata, mid, granted_qos):
        if SynchTags.DEBUG: print("Successfully subscribed to '{topics}' topics".format(
            topics=SynchTags.TOPIC_TAG_DISCOVERY+", "+SynchTags.TOPIC_RANGING_TERMINATED))

    def on_tag_discovery(self, client, userdata, message):
        new_tag_addr = message.payload.decode("utf-8")
        new_time = datetime.now()
        if SynchTags.DEBUG: print("{tagaddr} HELLO!".format(tagaddr=new_tag_addr))

        if len(self.active_tags) == 0:
            self.active_tags.append((new_tag_addr, new_time))
            if SynchTags.DEBUG: print("SEND TOKEN TO: {tagaddr}".format(tagaddr=new_tag_addr))
            client.publish(SynchTags.TOPIC_START_RANGING, new_tag_addr)  # SEND TOKEN
            return

        n_removed = 0
        found = False
        head_removed = False
        for i in range(0, len(self.active_tags)):
            tag_addr, time = self.active_tags[i-n_removed]
            if i == 0 and time + timedelta(seconds=2) < datetime.now():
                if SynchTags.DEBUG: print("TIME EXPIRED for " + str(tag_addr))
                self.active_tags.pop(i - n_removed)  # remove tag died with token
                n_removed += 1
                head_removed = True
            if tag_addr != new_tag_addr and time + timedelta(seconds=35) < datetime.now():
                if SynchTags.DEBUG: print("DELETE INACTIVE TAG "+str(tag_addr))
                self.active_tags.pop(i-n_removed)  # remove inactive tag
                n_removed += 1
            elif i > 0 and tag_addr == new_tag_addr:
                self.active_tags[i-n_removed] = (tag_addr, new_time)
                found = True

        if not found:
            # append new tag
            self.active_tags.append((new_tag_addr, new_time))

        if head_removed and len(self.active_tags) > 0:
            # send token to the new head
            client.publish(SynchTags.TOPIC_START_RANGING, self.active_tags[0][0])  # SEND TOKEN TO NEW HEAD
            if SynchTags.DEBUG: print("SEND TOKEN TO THE NEW HEAD: {tagaddr}".format(tagaddr=self.active_tags[0][0]))

        if SynchTags.DEBUG: print(str(self.active_tags))

    def on_ranging_terminated(self, client, userdata, message):
        ta = message.payload.decode("utf-8")
        if SynchTags.DEBUG: print("{tagaddr} RANGING TERMINATED".format(tagaddr=ta))

        if ta == self.active_tags[0][0]:
            tag_addr, time = self.active_tags.pop(0)
            self.active_tags.append((tag_addr, time))
            next_tag_addr = self.active_tags[0][0]
            if SynchTags.DEBUG: print("SEND TOKEN TO THE NEXT: {tagaddr}".format(tagaddr=next_tag_addr))
            client.publish(SynchTags.TOPIC_START_RANGING, next_tag_addr)  # SEND TOKEN TO self.active_tags[0]
