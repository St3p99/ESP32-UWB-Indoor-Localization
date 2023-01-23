import threading
import time
from csv import writer
from threading import Thread


class StoreData(Thread):
    PERIOD = 10  # mn
    RATE = 2  # msg/sec
    filename = 'data.csv'

    def __init__(self, server):
        threading.Thread.__init__(self, daemon=True)
        self.server = server

    def run(self):
        while (True):
            time.sleep(StoreData.PERIOD * 60)
            self.store()

    def store(self):
        with open(StoreData.filename, 'a', newline='') as f_object:
            writer_object = writer(f_object)
            for tag in self.server.tags.values():
                i = 0
                while not tag.queue.empty() and i < StoreData.PERIOD * 60 * StoreData.RATE:
                    data = tag.queue.get()
                    writer_object.writerow(data)
                    i += 1

            # Close the file object
            f_object.close()
