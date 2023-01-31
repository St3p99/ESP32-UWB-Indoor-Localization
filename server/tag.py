import json
import multiprocessing as mp
from datetime import datetime

import trilateration
from anchor import Anchor


class Tag:
    """
        Tag
    """

    def __init__(self, name, addr):
        self.name = name
        self.addr = addr
        self.measurements = {}
        self.uwb_queue = mp.Queue()
        self.imu_queue = mp.Queue()
        self.last_measurements = [None] * 2
        self.x = 0
        self.y = 0
        self.z = 0

    def get_name(self):
        return self.name

    def set_name(self, name):
        self.name = name

    def get_addr(self):
        return self.addr

    def set_addr(self, addr):
        self.addr = addr

    def get_measurements(self):
        return self.measurements

    def set_measurements(self, measurements: dict):
        self.measurements = measurements

    def add_imu_measurement(self, measurement: json):  # TYPE Json or json
        q = [measurement["T"], measurement["accelerometer"], measurement["gyroscope"], measurement["magnetometer"],
             str(datetime.now().strftime("%d-%m-%Y %H:%M:%S"))]
        self.imu_queue.put(q)

    def add_measurement(self, a: Anchor, range: float):
        if self.measurements.get(a.get_addr()) is not None:
            self.measurements[a.get_addr()].append(range)
        else:
            self.measurements[a.get_addr()] = [range]

        # TODO: discard expired last_measurements
        #  e.g.
        #    if new_measurements.timestamp - last_measurements[i].timestamp > expiring_time:
        #       discard last_measurement[i]

        # TODO: use 3 anchors to calculate tag positions
        #   needs 3 'last_measurements' from different anchors
        #   and trilateration.least_squares_trilateration_2D function to calculate tag position

        # Now, 2 anchors are used
        # last_measurements[0] is the latest measurement
        # last_measurements[1] is the second last measurement...
        # last_measurements refers to different anchors
        if (self.last_measurements[0] == None):
            self.last_measurements[0] = (a, range)
        else:
            if (self.last_measurements[0][0].get_addr() == a.get_addr()):
                # same anchor -> overwrite
                self.last_measurements[0] = (a, range)
            else:
                # new -> latest, latest -> second last, second last -> discarded
                self.last_measurements[1] = self.last_measurements[0]
                self.last_measurements[0] = (a, range)

        if self.last_measurements[0] is not None and self.last_measurements[1] is not None:
            self.update_pos()

            return True
        return False

    def update_pos(self):
        # TODO: use 3 anchors to calculate tag positions
        #   needs 3 'last_measurements' from different anchors
        #   and trilateration.least_squares_trilateration_2D function to calculate tag position

        a1 = self.last_measurements[0][0]
        a2 = self.last_measurements[1][0]

        # NOTE: trilateration_2D_2A_origin function assume that the first anchor is fixed in the axis origin
        # and second one is on the x-axis

        if a1.x == 0.0 and a1.y == 0.0:
            self.x, self.y = trilateration.trilateration_2D_2A_origin(
                a1, self.last_measurements[0][1],
                a2, self.last_measurements[1][1])
        else:
            self.x, self.y = trilateration.trilateration_2D_2A_origin(
                a2, self.last_measurements[1][1],
                a1, self.last_measurements[0][1])

        q = [self.name, self.x, self.y, str(datetime.now().strftime("%d-%m-%Y %H:%M:%S"))]
        self.uwb_queue.put(q)

    def get_last_position(self):
        return self.x, self.y, self.z

    def __str__(self):
        return f"Tag: addr={self.addr}, measurements={self.measurements}, x={self.x}, y={self.y}"
