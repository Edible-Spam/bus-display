"""RGB timetable renderer for Interstate 75 W HUB75 panels."""
import time
from interstate75 import Interstate75
from config import PANEL, STOP_NAME, UTC_OFFSET_SECONDS


class TimetableDisplay:
    def __init__(self):
        self.board = Interstate75(display=getattr(Interstate75, PANEL))
        self.g = self.board.display
        self.g.set_font("bitmap8")
        self.compact = PANEL == "DISPLAY_INTERSTATE75_64X32"
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
        if self.compact:
            # bitmap8 remains readable on the small panel. Two route/due rows
            # fit without clipping; destination text needs a wider panel.
            self.text(STOP_NAME, 1, 0, self.cyan, 7)
            if not departures:
                self.text("NO BUS", 1, 14, self.amber, 7)
            for index, item in enumerate(departures[:2]):
                y = 11 + index * 11
                self.text(item["route"], 1, y, self.green, 4)
                self.text(item["due"], 39, y, self.amber, 3)
            self.board.update()
            return
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
        if self.compact:
            self.text(STOP_NAME, 1, 0, self.cyan, 7)
            self.text("ERROR", 1, 11, self.red, 7)
            self.text(message, 1, 22, self.amber, 7)
            self.board.update()
            return
        self.text(STOP_NAME, 1, 1, self.cyan)
        self.text("TIMETABLE UNAVAILABLE", 1, 21, self.red)
        self.text(message, 1, 37, self.amber, 20)
        self.board.update()


def format_clock(epoch):
    return "%02d:%02d" % time.localtime(epoch + UTC_OFFSET_SECONDS)[3:5]
