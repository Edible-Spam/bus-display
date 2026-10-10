"""Settings for this single-stop PTV timetable display."""

# Set this to a valid Interstate75 display constant for your HUB75 panel.
PANEL = "DISPLAY_INTERSTATE75_64X32"
# PTV route types: train=0, tram=1, bus=2, V/Line=3, Night Bus=4.
ROUTE_TYPES = (2,)
# Pitt St/Rathdowne St, Carlton — southbound / city-bound side. This stop
# serves route 250 to City (Queen St) and 251 to Little Collins St.
STOP_ID = 659
# 659 is the public/GTFS stop ID printed for this bus stop. PTV's departure
# endpoint requires an explicit flag when using a GTFS stop ID.
STOP_ID_IS_GTFS = True
STOP_NAME = "PITT ST"
MAX_RESULTS_PER_TYPE = 4
REFRESH_SECONDS = 30
REQUEST_TIMEOUT_SECONDS = 12
# HTTP port for the authenticated, local-network status/deployment endpoint.
CONTROL_PORT = 8080
# Hard limit for a single deployment request; keeps a malformed request from
# exhausting the Pico W's memory.
CONTROL_MAX_BODY_BYTES = 24 * 1024
# Australia/Melbourne standard offset. The renderer adds daylight saving
# automatically using Victoria's April/October transition rules.
UTC_OFFSET_SECONDS = 10 * 60 * 60
