"""Settings for this single-stop PTV timetable display."""

# Set this to a valid Interstate75 display constant for your HUB75 panel.
PANEL = "DISPLAY_INTERSTATE75_128X64"
# PTV route types: train=0, tram=1, bus=2, V/Line=3, Night Bus=4.
ROUTE_TYPES = (2,)
STOP_ID = 0
STOP_NAME = "Configure stop"
MAX_RESULTS_PER_TYPE = 4
REFRESH_SECONDS = 30
REQUEST_TIMEOUT_SECONDS = 12
# Australia/Melbourne: UTC+10 standard time; update to +11 during DST.
UTC_OFFSET_SECONDS = 10 * 60 * 60
