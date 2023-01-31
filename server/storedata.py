import threading
import time
from csv import writer
from enum import Enum
from threading import Thread


class DataType(Enum):
    UWB = 0
    IMU = 1


class StoreData(Thread):
    PERIOD = 10  # mn
    RATE = 1  # msg received/sec
    uwb_filename = 'uwb_data.csv'
    imu_filename = 'imu_data.csv'

    def __init__(self, server):
        threading.Thread.__init__(self, daemon=True)
        self.server = server

    def run(self):
        while (True):
            time.sleep(StoreData.PERIOD * 60)
            self.store(DataType.UWB)
            self.store(DataType.IMU)

    def store(self, data_type):
        file_name = StoreData.uwb_filename if data_type == DataType.UWB else StoreData.imu_filename
        with open(file_name, 'a', newline='') as f_object:
            writer_object = writer(f_object)
            n = StoreData.PERIOD * 60 * StoreData.RATE  # number of data to store
            for tag in self.server.tags.values():
                i = 0
                queue = tag.uwb_queue if data_type == DataType.UWB else tag.imu_queue
                while not queue.empty() and i < n:
                    data = queue.get()
                    writer_object.writerow(data)
                    i += 1
            f_object.close()
