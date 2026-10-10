"""128x64 RGB timetable renderer for Interstate 75 W."""
import time
from interstate75 import Interstate75
from config import PANEL, STOP_NAME, UTC_OFFSET_SECONDS


class TimetableDisplay:
    def __init__(self):
        self.board = Interstate75(display=getattr(Interstate75, PANEL))
        self.g = self.board.display
        self.g.set_font("bitmap8")
        self.black = self.g.create_pen(0, 0, 0)
        self.white = self.g.create_pen(220, 220, 220)
        self.cyan = self.g.create_pen(0, 210, 230)
        self.green = self.g.create_pen(60, 255, 100)
        self.amber = self.g.create_pen(255, 170, 20)
        self.red = self.g.create_pen(255, 50, 40)

    def text(self, value, x, y, pen, limit=20):
        self.g.set_pen(pen)
        self.g.text(str(value)[:limit], x, y, scale=1)

    def clear(self):
        self.g.set_pen(self.black)
        self.g.clear()

    def show_departures(self, departures, refreshed_at):
        self.clear()
        self.text(STOP_NAME, 1, 0, self.cyan, 20)
        self.text("RT  DESTINATION       DUE", 1, 8, self.white, 21)
        if not departures:
            self.text("No upcoming services", 1, 26, self.amber)
        for index, item in enumerate(departures[:3]):
            y = 18 + index * 14
            self.text(item["route"], 1, y, self.green, 4)
            self.text(item["destination"], 25, y, self.white, 13)
            self.text(item["due"], 104, y, self.amber, 5)
        self.text("Updated " + refreshed_at, 1, 56, self.white, 20)
        self.board.update()

    def show_error(self, message):
        self.clear()
        self.text(STOP_NAME, 1, 1, self.cyan)
        self.text("TIMETABLE UNAVAILABLE", 1, 21, self.red)
        self.text(message, 1, 37, self.amber, 20)
        self.board.update()


def format_clock(epoch):
    return "%02d:%02d" % time.localtime(epoch + UTC_OFFSET_SECONDS)[3:5]
