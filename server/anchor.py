class Anchor:
    def __init__(self, addr: str, x: float, y: float):
        self.addr = addr
        self.x = x
        self.y = y

    def get_addr(self):
        return self.addr

    def set_addr(self, addr: str):
        self.addr = addr

    def get_x(self):
        return self.x

    def set_x(self, x: float):
        self.x = x

    def get_y(self):
        return self.y

    def set_y(self, y: float):
        self.y = y

    def __str__(self):
        return f"Anchor: addr={self.addr}, x={self.x}, y={self.y}"
