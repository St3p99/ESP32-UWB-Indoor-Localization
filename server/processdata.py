import json
import threading
from json import JSONDecodeError
from threading import Thread


class ProcessData(Thread):
    def __init__(self, server):
        threading.Thread.__init__(self, daemon=True)
        self.server = server

    def run(self):
        self.server.client.loop_forever()

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
