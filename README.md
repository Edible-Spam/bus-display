# PTV Bus Timetable Display

MicroPython project for a single PTV stop on a HUB75 RGB LED panel driven by a
Pimoroni Interstate 75 W. It polls PTV's v3 API every 30 seconds and shows
an unavailable message when Wi-Fi or the API fails. It retries every 30
seconds and attempts to reconnect Wi-Fi automatically, including after boot.

## Setup

1. Install Pimoroni's current Interstate 75 W MicroPython firmware.
2. Copy `secrets.example.py` to `secrets.py`; add Wi-Fi credentials plus the
   PTV developer ID and API key. `secrets.py` is ignored by Git.
3. In `config.py`, set the PTV `STOP_ID`, short `STOP_NAME`, route types and
   panel size. Bus is route type `2`.
4. Upload all `.py` files to the Pico W's root in Thonny; run `main.py`.

The default layout is for a 64×32 panel and shows the next two route/due pairs.
For a 128×64 panel, set `PANEL` to `DISPLAY_INTERSTATE75_128X64`; the wider
layout then shows three services with destinations.
Power the HUB75 panel from a separate, suitably rated 5 V supply; do not power
it through the Interstate 75 W USB connection.

Look up stop IDs and validate credentials in PTV's [v3 Swagger UI](https://timetableapi.ptv.vic.gov.au/swagger/ui/index). PTV requires every API call to include an HMAC-SHA1 signature.

## Local-network control and deployment

The display itself makes the PTV API calls. Once it is connected to Wi-Fi, it
also provides an authenticated HTTP control endpoint on port `8080` for status
and code deployment. It never serves, accepts, or replaces `secrets.py`.

1. Put a long random `CONTROL_TOKEN` in `secrets.py` (and keep it private).
2. Use a DHCP reservation in your router so the display has a stable IP address.
3. For the first install, upload all board-side `.py` files by USB/Thonny,
   including `control_server.py`. Do **not** upload `deploy.py`.
4. Copy `deploy.example.json` to `deploy.local.json`; enter the device IP and
   control token. This file is ignored by Git.
5. On a computer with Python 3, run `python deploy.py` to upload the allow-listed
   app files. The board confirms the upload, then restarts.

Use this only on a trusted private LAN: do not port-forward the control port,
do not expose it to the internet, and rotate the control token if it is ever
disclosed. Every control request requires `Authorization: Bearer <token>`.
