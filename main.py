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
            route_number = route.get("route_number") or route.get("route_name") or "?"
            if route_number == "250-251 combined":
                route_number = "250-251"
            output.append({"route": route_number,
                           "destination": direction.get("direction_name") or "Unknown",
                           "run_ref": departure.get("run_ref"),
                           "stop_id": departure.get("stop_id"),
                           "scheduled": departure.get("scheduled_departure_utc"),
                           "estimated": bool(departure.get("estimated_departure_utc")),
                           "epoch": iso_to_epoch(timestamp)})
    return output


def unique_departures(items):
    unique = []
    for item in items:
        match = None
        for existing in unique:
            same_stop = item["stop_id"] == existing["stop_id"]
            same_schedule = bool(item["scheduled"]) and item["scheduled"] == existing["scheduled"]
            same_run = bool(item["run_ref"]) and item["run_ref"] == existing["run_ref"]
            # The combined timetable can use a different run reference. Only
            # merge it with an individual route at the exact scheduled time.
            combined_pair = (item["route"] == "250-251" and existing["route"] in ("250", "251")) or (existing["route"] == "250-251" and item["route"] in ("250", "251"))
            if same_stop and ((same_run and same_schedule) or (combined_pair and same_schedule)):
                match = existing
                break
        if match is None:
            unique.append(item.copy())
        else:
            if item["estimated"] and not match["estimated"]:
                match["epoch"] = item["epoch"]
                match["estimated"] = True
            if match["route"] == "250-251" and item["route"] in ("250", "251"):
                match["route"] = item["route"]
    return unique


def departures(client):
    all_departures = []
    raw_departures = 0
    for route_type in ROUTE_TYPES:
        payload = client.departures(route_type, STOP_ID)
        raw_departures += len(payload.get("departures", []))
        all_departures.extend(normalise(payload))
    all_departures = unique_departures(all_departures)
    all_departures.sort(key=lambda item: item["epoch"])
    now = time.time()
    for item in all_departures:
        minutes = max(0, int((item["epoch"] - now + 30) // 60))
        item["due"] = "NOW" if minutes == 0 else "%dm" % minutes
    return all_departures, raw_departures


async def refresh_loop(display, client, state):
    from wifi import ensure_connected
    while True:
        try:
            await ensure_connected()
            current, raw_departures = departures(client)
            refreshed = format_clock(time.time())
            display.show_departures(current, refreshed)
            state["last_refresh"] = refreshed
            state["last_error"] = None
            state["departures"] = len(current)
            state["raw_departures"] = raw_departures
            state["next_routes"] = [item["route"] for item in current[:2]]
            state["duplicates_removed"] = raw_departures - len(current)
            state["next_trips"] = [{"run_ref": item["run_ref"], "scheduled": item["scheduled"], "estimated": item["estimated"], "due": item["due"]} for item in current[:2]]
        except Exception as error:
            state["last_error"] = str(error)[:80]
            state["departures"] = 0
            state["raw_departures"] = 0
            state["next_routes"] = []
            state["next_trips"] = []
            state["duplicates_removed"] = 0
            display.show_error(str(error))
        await asyncio.sleep(REFRESH_SECONDS)


async def run():
    from secrets import PTV_API_KEY, PTV_DEVELOPER_ID
    display = TimetableDisplay()
    display.show_error("Connecting")
    from control_server import serve
    state = {"last_refresh": None, "last_error": None, "departures": 0, "raw_departures": 0, "last_deploy": None}
    asyncio.create_task(refresh_loop(display, PTVClient(PTV_DEVELOPER_ID, PTV_API_KEY), state))
    await serve(state)


asyncio.run(run())
