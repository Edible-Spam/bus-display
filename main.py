"""Run this as main.py on the Interstate 75 W."""
import time
from config import REFRESH_SECONDS, ROUTE_TYPES, STOP_ID
from display import TimetableDisplay, format_clock
from ptv import PTVClient


def iso_to_epoch(value):
    date, clock = value.replace("Z", "").split("T")
    year, month, day = (int(part) for part in date.split("-"))
    hour, minute, second = (int(part) for part in clock[:8].split(":"))
    return time.mktime((year, month, day, hour, minute, second, 0, 0))


def normalise(payload):
    routes, directions = payload.get("routes", {}), payload.get("directions", {})
    output = []
    for departure in payload.get("departures", []):
        route = routes.get(str(departure.get("route_id")), {})
        direction = directions.get(str(departure.get("direction_id")), {})
        timestamp = departure.get("estimated_departure_utc") or departure.get("scheduled_departure_utc")
        if timestamp:
            output.append({"route": route.get("route_number") or route.get("route_name") or "?",
                           "destination": direction.get("direction_name") or "Unknown",
                           "epoch": iso_to_epoch(timestamp)})
    return output


def departures(client):
    all_departures = []
    for route_type in ROUTE_TYPES:
        all_departures.extend(normalise(client.departures(route_type, STOP_ID)))
    all_departures.sort(key=lambda item: item["epoch"])
    now = time.time()
    for item in all_departures:
        minutes = max(0, int((item["epoch"] - now + 30) // 60))
        item["due"] = "NOW" if minutes == 0 else "%dm" % minutes
    return all_departures


def main():
    from secrets import PTV_API_KEY, PTV_DEVELOPER_ID
    from wifi import connect
    display = TimetableDisplay()
    connect()
    client, cached = PTVClient(PTV_DEVELOPER_ID, PTV_API_KEY), []
    while True:
        try:
            cached = departures(client)
            display.show_departures(cached, format_clock(time.time()))
        except Exception as error:
            if cached:
                display.show_departures(cached, "offline")
            else:
                display.show_error(str(error))
        time.sleep(REFRESH_SECONDS)


main()
