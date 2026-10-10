# PTV Bus Timetable Display

MicroPython project for a single PTV stop on a HUB75 RGB LED panel driven by a
Pimoroni Interstate 75 W. It polls PTV's v3 API every 30 seconds and retains
the last departures when Wi-Fi or the API briefly fails.

## Setup

1. Install Pimoroni's current Interstate 75 W MicroPython firmware.
2. Copy `secrets.example.py` to `secrets.py`; add Wi-Fi credentials plus the
   PTV developer ID and API key. `secrets.py` is ignored by Git.
3. In `config.py`, set the PTV `STOP_ID`, short `STOP_NAME`, route types and
   panel size. Bus is route type `2`.
4. Upload all `.py` files to the Pico W's root in Thonny; run `main.py`.

The default layout is for a 128×64 panel and shows the next three services.
Power the HUB75 panel from a separate, suitably rated 5 V supply; do not power
it through the Interstate 75 W USB connection.

Look up stop IDs and validate credentials in PTV's [v3 Swagger UI](https://timetableapi.ptv.vic.gov.au/swagger/ui/index). PTV requires every API call to include an HMAC-SHA1 signature.
