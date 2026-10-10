"""Minimal signed PTV Timetable API v3 client for MicroPython."""
try:
    import urequests as requests
    import uhashlib as hashlib
    import ubinascii as binascii
except ImportError:
    import requests
    import hashlib
    import binascii

from config import MAX_RESULTS_PER_TYPE, REQUEST_TIMEOUT_SECONDS, STOP_ID_IS_GTFS

BASE_URL = "https://timetableapi.ptv.vic.gov.au"


def hmac_sha1(key, message):
    """HMAC-SHA1 with MicroPython's small standard library."""
    key, message = key.encode(), message.encode()
    if len(key) > 64:
        key = hashlib.sha1(key).digest()
    key += b"\x00" * (64 - len(key))
    inner = bytes(bytearray(value ^ 0x36 for value in key))
    outer = bytes(bytearray(value ^ 0x5c for value in key))
    digest = hashlib.sha1(inner + message).digest()
    return binascii.hexlify(hashlib.sha1(outer + digest).digest()).decode()


class PTVClient:
    def __init__(self, developer_id, api_key):
        self.developer_id = str(developer_id)
        self.api_key = api_key

    def departures(self, route_type, stop_id):
        # PTV signs the path and query string, excluding the signature itself.
        path = "/v3/departures/route_type/%d/stop/%d?max_results=%d" % (
            route_type, stop_id, MAX_RESULTS_PER_TYPE)
        if STOP_ID_IS_GTFS:
            path += "&gtfs=true"
        # Route expansion supplies route_number for each departure's route_id.
        path += "&expand=2&devid=" + self.developer_id
        response = requests.get(
            BASE_URL + path + "&signature=" + hmac_sha1(self.api_key, path),
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
        try:
            if response.status_code != 200:
                raise RuntimeError("PTV HTTP %s" % response.status_code)
            return response.json()
        finally:
            response.close()
