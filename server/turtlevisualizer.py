import threading
import time
import turtle
from datetime import datetime, timedelta

from visualizer import Visualizer


class TurtleVisualizer(Visualizer):
    TAG_LIFETIME = 10  # sec

    def __init__(self, anchors):
        self.turtle_screen = turtle.Screen()
        self.screen_init(self.turtle_screen)
        self.t_ui = None
        self.distance_a1_a2 = 2.0
        self.meter2pixel = 100
        self.range_offset = 0.9
        self.anchors = anchors

        self.turtle_anchors = []
        self.turtle_tags = {}  # dict{ tag_addr: (turtle_tag, timestamp_last_update)}
        self.showing = False

    def set_anchors(self, anchors):
        self.anchors = anchors
        if (self.showing):
            for t_a in self.turtle_anchors:
                t_a.clear()
            self.turtle_anchors = []
            self.draw_anchors()

    def show(self):
        self.showing = True
        t_ui = turtle.Turtle()
        self.turtle_init(t_ui)
        self.draw_ui(t_ui)
        self.draw_anchors()
        thread = threading.Thread(target=self.remove_inactive_tags)
        thread.start()
        turtle.mainloop()

    def update_tag(self, tag):
        if self.turtle_tags.get(tag.get_addr()) is not None:
            turtle_tag, last_update = self.turtle_tags[tag.get_addr()]
            if datetime.now() - last_update < timedelta(seconds=2):
                return
            turtle_tag.clear()
            self.turtle_tags[tag.get_addr()] = turtle_tag, datetime.now()
            self.draw_uwb_tag(tag.get_last_position()[0], tag.get_last_position()[1], tag.get_name(), turtle_tag)
        else:
            self.add_tag(tag)

    def add_tag(self, tag):
        t = turtle.Turtle()
        self.turtle_init(t)
        self.draw_uwb_tag(tag.get_last_position()[0], tag.get_last_position()[1], tag.get_name(), t)
        self.turtle_tags[tag.get_addr()] = (t, datetime.now())

    def remove_tag(self, tag):
        if self.turtle_tags.get(tag.get_addr()) is not None:
            t = self.turtle_tags[tag.get_addr()][0]
            t.clear()
            self.turtle_tags.pop(tag.get_addr())

    def remove_inactive_tags(self):
        while (True):
            time.sleep(TurtleVisualizer.TAG_LIFETIME)
            tags_addr = list(self.turtle_tags.keys())
            for tag_addr in tags_addr:
                t, timestamp = self.turtle_tags[tag_addr]
                if timestamp + timedelta(seconds=TurtleVisualizer.TAG_LIFETIME) < datetime.now():
                    # print("Inactive Tag "+ tag_addr)
                    t.clear()
                    self.turtle_tags.pop(tag_addr)

    def draw_anchors(self):
        for a in self.anchors:
            t = turtle.Turtle()
            self.turtle_init(t)
            pos = "({x}, {y})"
            self.draw_uwb_anchor(a.get_x(), a.get_y(),
                                 a.get_addr() + pos.format(x=a.get_x(), y=a.get_y()),
                                 t)
            self.turtle_anchors.append(t)

    def screen_init(self, width=1200, height=800, t=turtle):
        t.tracer(False)
        t.hideturtle()
        t.speed(0)

    # Turtle drawing utilities
    def turtle_init(self, t=turtle):
        t.hideturtle()
        t.speed(0)

    def draw_line(self, x0, y0, x1, y1, color="black", t=turtle):
        t.pencolor(color)
        t.up()
        t.goto(x0, y0)
        t.down()
        t.goto(x1, y1)
        t.up()

    def draw_fastU(self, x, y, length, color="black", t=turtle):
        self.draw_line(x, y, x, y + length, color, t)

    def draw_fastV(self, x, y, length, color="black", t=turtle):
        self.draw_line(x, y, x + length, y, color, t)

    def draw_cycle(self, x, y, r, color="black", t=turtle):
        t.pencolor(color)

        t.up()
        t.goto(x, y - r)
        t.setheading(0)
        t.down()
        t.circle(r)
        t.up()

    def fill_cycle(self, x, y, r, color="black", t=turtle):
        t.up()
        t.goto(x, y)
        t.down()
        t.dot(r, color)
        t.up()

    def write_txt(self, x, y, txt, color="black", t=turtle, f=('Arial', 12, 'normal')):
        t.pencolor(color)
        t.up()
        t.goto(x, y)
        t.down()
        t.write(txt, move=False, align='left', font=f)
        t.up()

    def draw_rect(self, x, y, w, h, color="black", t=turtle):
        t.pencolor(color)

        t.up()
        t.goto(x, y)
        t.down()
        t.goto(x + w, y)
        t.goto(x + w, y + h)
        t.goto(x, y + h)
        t.goto(x, y)
        t.up()

    def fill_rect(self, x, y, w, h, color=("black", "black"), t=turtle):
        t.begin_fill()
        self.draw_rect(x, y, w, h, color, t)
        t.end_fill()
        pass

    def clean(self, t=turtle):
        t.clear()

    def draw_ui(self, t):
        self.write_txt(-300, 250, "UWB Positon", "black", t, f=('Arial', 32, 'normal'))
        self.fill_rect(-400, 200, 800, 40, "black", t)
        self.write_txt(-50, 205, "WALL", "yellow", t, f=('Arial', 24, 'normal'))

    def draw_uwb_anchor(self, x, y, txt, t):
        x = -250 + x * self.meter2pixel
        y = 150 - y * self.meter2pixel
        r = 20
        self.fill_cycle(x, y, r, "green", t)
        self.write_txt(x + r, y, txt,
                       "black", t, f=('Arial', 16, 'normal'))

    def draw_uwb_tag(self, x, y, txt, t):
        pos_x = -250 + int(x * self.meter2pixel)
        pos_y = 150 - int(y * self.meter2pixel)
        r = 20
        self.fill_cycle(pos_x, pos_y, r, "blue", t)
        self.write_txt(pos_x, pos_y, txt + ": (" + str(x) + "," + str(y) + ")",
                       "black", t, f=('Arial', 16, 'normal'))
