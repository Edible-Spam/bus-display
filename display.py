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
        self.g.text(str(value)[:limit], x, y + 1, scale=1)

    def clear(self):
        self.g.set_pen(self.black)
        self.g.clear()

    def right_text(self, value, y, pen):
        value = str(value)
        x = 63 - self.g.measure_text(value, scale=1)
        self.text(value, x, y, pen, len(value))

    def ptv_icon(self):
        # Supplied five-dot logo, reduced to 15x8 pixels. Zero pixels are
        # unpainted so the logo has no background rectangle.
        bitmap = (
            "010010010010010",
            "000000000000000",
            "111111101111111",
            "000001101100000",
            "000001101100000",
            "000001101100000",
            "000001101100000",
            "000001101100000",
        )
        self.g.set_pen(self.cyan)
        for y, row in enumerate(bitmap):
            for x, pixel in enumerate(row):
                if pixel == "1":
                    self.g.pixel(x + 1, y + 1)

    def show_departures(self, departures, refreshed_at):
        self.clear()
        if self.compact:
            # Keep the full combined route label and right-align the countdown.
            self.ptv_icon()
            self.right_text(format_clock(time.time()), 0, self.red)
            if not departures:
                self.text("NO BUS", 1, 14, self.amber, 7)
            for index, item in enumerate(departures[:2]):
                y = 11 + index * 11
                self.text(item["route"], 1, y, self.amber, 7)
                self.right_text(item["due"], y, self.green)
            self.board.update()
            return
        self.text(STOP_NAME, 1, 0, self.cyan, 20)
        self.text("RT  DESTINATION       DUE", 1, 8, self.white, 21)
        if not departures:
            self.text("No upcoming services", 1, 26, self.amber)
        for index, item in enumerate(departures[:3]):
            y = 18 + index * 14
            self.text(item["route"], 1, y, self.amber, 4)
            self.text(item["destination"], 25, y, self.white, 13)
            self.text(item["due"], 104, y, self.green, 5)
        self.text("Updated " + refreshed_at, 1, 56, self.white, 20)
        self.board.update()

    def show_error(self, message):
        self.clear()
        if self.compact:
            self.ptv_icon()
            self.text("NO DATA", 1, 11, self.red, 7)
            self.text("RETRYING", 1, 22, self.amber, 8)
            self.board.update()
            return
        self.text(STOP_NAME, 1, 1, self.cyan)
        self.text("TIMETABLE UNAVAILABLE", 1, 21, self.red)
        self.text(message, 1, 37, self.amber, 20)
        self.board.update()


def melbourne_offset(epoch):
    # Work in standard time: both transitions occur at 02:00 AEST
    # (the April transition is 03:00 AEDT).
    local = time.localtime(epoch + UTC_OFFSET_SECONDS)
    month, day, hour, weekday = local[1], local[2], local[3], local[6]
    first_sunday = 1 + (6 - (weekday - (day - 1)) % 7) % 7
    daylight = month < 4 or month > 10
    if month == 4:
        daylight = (day, hour) < (first_sunday, 2)
    elif month == 10:
        daylight = (day, hour) >= (first_sunday, 2)
    return UTC_OFFSET_SECONDS + (3600 if daylight else 0)


def format_clock(epoch):
    hour, minute = time.localtime(epoch + melbourne_offset(epoch))[3:5]
    suffix = "am" if hour < 12 else "pm"
    return "%d:%02d%s" % (hour % 12 or 12, minute, suffix)
