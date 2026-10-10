"""Run this as main.py on the Interstate 75 W."""
import time
import uasyncio as asyncio
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
    raw_departures = 0
    for route_type in ROUTE_TYPES:
        payload = client.departures(route_type, STOP_ID)
        raw_departures += len(payload.get("departures", []))
        all_departures.extend(normalise(payload))
    all_departures.sort(key=lambda item: item["epoch"])
    now = time.time()
    for item in all_departures:
        minutes = max(0, int((item["epoch"] - now + 30) // 60))
        item["due"] = "NOW" if minutes == 0 else "%dm" % minutes
    return all_departures, raw_departures


async def refresh_loop(display, client, state):
    cached = []
    while True:
        try:
            cached, raw_departures = departures(client)
            refreshed = format_clock(time.time())
            display.show_departures(cached, refreshed)
            state["last_refresh"] = refreshed
            state["last_error"] = None
            state["departures"] = len(cached)
            state["raw_departures"] = raw_departures
        except Exception as error:
            state["last_error"] = str(error)[:80]
            if cached:
                display.show_departures(cached, "offline")
            else:
                display.show_error(str(error))
        await asyncio.sleep(REFRESH_SECONDS)


async def run():
    from secrets import PTV_API_KEY, PTV_DEVELOPER_ID
    from wifi import connect
    display = TimetableDisplay()
    connect()
    from control_server import serve
    state = {"last_refresh": None, "last_error": None, "departures": 0, "raw_departures": 0, "last_deploy": None}
    asyncio.create_task(refresh_loop(display, PTVClient(PTV_DEVELOPER_ID, PTV_API_KEY), state))
    await serve(state)


asyncio.run(run())
