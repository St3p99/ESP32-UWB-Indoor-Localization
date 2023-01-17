import cmath

from anchor import Anchor


class Tag:
    def __init__(self, name, addr):
        self.name = name
        self.addr = addr
        self.measurements = {}
        self.last_measurements = [None]*2
        self.x = -1
        self.y = -1

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
    
    def add_measurement(self, a: Anchor, range: float):
        if self.measurements.get(a.get_addr()) is not None:
            self.measurements[a.get_addr()].append(range)
        else:
            self.measurements[a.get_addr()] = [range]

        if ( self.last_measurements[0] == None ):
            self.last_measurements[0] = (a, range)
        else:
            # self.last_measurements[0] è l'ultima misurazione
            # self.last_measurements[1] è la penultima misurazione
            # last_measurements[0], last_measurements[1] fanno riferimento a misurazioni di anchor diversi
            if( self.last_measurements[0][0].get_addr() == a.get_addr()):
                # stesso anchor -> sovrascrivi misura più recente
                self.last_measurements[0] = (a, range)
            else: # shift e sovrascrivi più recente
                self.last_measurements[1] = self.last_measurements[0]
                self.last_measurements[0] = (a, range)

        if self.last_measurements[0] is not None and self.last_measurements[1] is not None:
            self.update_pos()
            return True
        return False

    def update_pos(self):
        # TODO : Calculate position with MULTIPLE ANCHORS
        a1 = self.last_measurements[0][0]
        a2 = self.last_measurements[1][0]
        a, b = -1.0, -1.0

        if a1.x == 0.0 and a1.y == 0.0:
            b = self.last_measurements[0][1]
            a = self.last_measurements[1][1]
            c = a2.x
        else:
            b = self.last_measurements[1][1]
            a = self.last_measurements[0][1]
            c = a1.x
        # p = (a + b + c) / 2.0
        # s = cmath.sqrt(p * (p - a) * (p - b) * (p - c))
        # y = 2.0 * s / c
        # x = cmath.sqrt(b * b - y * y)

        if b == 0:
            self.x, self.y = 0, 0
            return
        cos_a = (b * b + c * c - a * a) / (2 * b * c)
        x = b * cos_a
        y = b * cmath.sqrt(1 - cos_a * cos_a)

        self.x, self.y = round(x.real, 1), round(y.real, 1)

    def get_last_position(self):
        return (self.x, self.y)
    
    def set_last_position(self, x: float, y: float):
        self.x = x
        self.y = y

    def __str__(self):
        return f"Tag: addr={self.addr}, measurements={self.measurements}, x={self.x}, y={self.y}"
