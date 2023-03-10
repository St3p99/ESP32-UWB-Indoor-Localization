from enum import Enum

from anchor import Anchor
from processdata import ProcessData
from storedata import StoreData
from synchtags import SynchTags
from tag import Tag
from turtlevisualizer import TurtleVisualizer


class VisualizerType(Enum):
    TURTLE = 1


class Server:
    class VisualizerType(Enum):
        TURTLE = 1

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

    def get_anchors(self):
        return self.anchors

    def get_tags(self):
        return self.tags

    def set_visualizer(self, v: VisualizerType):
        if v == VisualizerType.TURTLE:
            self.visualizer = TurtleVisualizer(self.anchors.values())

    def start(self):
        t1 = ProcessData(self)
        t1.start()

        t2 = SynchTags(self)
        t2.start()

        t3 = StoreData(self)
        t3.start()

        self.visualize()

    def visualize(self):
        if self.visualizer is not None:
            self.visualizer.show()


def main():
    # configure network
    HOST = "192.168.172.90"
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
    A2 = Anchor(A2_ADDR, 6, 0)

    TAG1_ADDR = "1D:00:22:EA:82:60:3B:9B"
    TAG2_ADDR = "2D:00:22:EA:82:60:3B:9B"
    T1 = Tag("T1", TAG1_ADDR)
    T2 = Tag("T2", TAG2_ADDR)

    server = Server(HOST, PORT, [A1, A2], [T1, T2])
    server.set_visualizer(VisualizerType.TURTLE)
    server.start()


if __name__ == '__main__':
    main()
