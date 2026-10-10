"""Wi-Fi and clock setup for MicroPython on Pico W."""
import network
import time
from secrets import WIFI_SSID, WIFI_PASSWORD


async def ensure_connected():
    import uasyncio as asyncio
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if wlan.isconnected():
        return wlan
    wlan.disconnect()
    wlan.connect(WIFI_SSID, WIFI_PASSWORD)
    deadline = time.ticks_add(time.ticks_ms(), 20000)
    while not wlan.isconnected():
        if time.ticks_diff(deadline, time.ticks_ms()) <= 0:
            wlan.disconnect()
            raise RuntimeError("Wi-Fi connection timed out")
        await asyncio.sleep_ms(200)
    try:
        import ntptime
        ntptime.timeout = 2
        ntptime.settime()
    except Exception:
        pass
    return wlan


def connect():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        wlan.connect(WIFI_SSID, WIFI_PASSWORD)
        deadline = time.ticks_add(time.ticks_ms(), 20000)
        while not wlan.isconnected():
            if time.ticks_diff(deadline, time.ticks_ms()) <= 0:
                raise RuntimeError("Wi-Fi connection timed out")
            time.sleep_ms(200)
    try:
        import ntptime
        ntptime.settime()  # PTV timestamps are UTC, so a valid RTC matters.
    except Exception:
        pass
    return wlan
