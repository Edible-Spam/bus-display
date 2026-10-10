"""Authenticated local-network status and deployment server for Pico W."""
try:
    import uasyncio as asyncio
    import ujson as json
    import ubinascii as binascii
except ImportError:  # Useful for limited desktop inspection.
    import asyncio
    import json
    import binascii

import os
from config import CONTROL_MAX_BODY_BYTES, CONTROL_PORT
from secrets import CONTROL_TOKEN

# Explicit allow-list: credentials can never be read or overwritten remotely.
DEPLOYABLE_FILES = (
    "config.py", "control_server.py", "display.py", "main.py", "ptv.py", "wifi.py",
)


def _same_token(provided, expected):
    """Compare without returning early for matching prefixes."""
    if len(provided) != len(expected):
        return False
    difference = 0
    for index in range(len(provided)):
        difference |= ord(provided[index]) ^ ord(expected[index])
    return difference == 0


async def _reply(writer, status, body):
    encoded = json.dumps(body).encode()
    writer.write(("HTTP/1.1 %s\r\nContent-Type: application/json\r\n"
                  "Content-Length: %d\r\nConnection: close\r\n\r\n") %
                 (status, len(encoded)))
    writer.write(encoded)
    await writer.drain()


async def _restart():
    await asyncio.sleep(1)
    import machine
    machine.reset()


def _install(files):
    if not isinstance(files, dict) or not files:
        raise ValueError("files must be a non-empty object")
    if any(name not in DEPLOYABLE_FILES for name in files):
        raise ValueError("deployment includes a forbidden filename")
    if sum(len(value) for value in files.values() if isinstance(value, str)) > CONTROL_MAX_BODY_BYTES:
        raise ValueError("deployment is too large")
    for name, encoded in files.items():
        if not isinstance(encoded, str):
            raise ValueError("file payload must be base64 text")
        try:
            content = binascii.a2b_base64(encoded)
        except Exception:
            raise ValueError("invalid base64 payload")
        temporary = name + ".new"
        with open(temporary, "wb") as handle:
            handle.write(content)
        try:
            os.remove(name + ".bak")
        except OSError:
            pass
        try:
            os.rename(name, name + ".bak")
        except OSError:
            pass
        os.rename(temporary, name)


async def _handle(reader, writer, state):
    try:
        request = (await reader.readline()).decode().strip().split()
        if len(request) != 3:
            await _reply(writer, "400 Bad Request", {"error": "invalid request"})
            return
        method, path, _ = request
        headers = {}
        while True:
            line = await reader.readline()
            if line in (b"\r\n", b"\n", b""):
                break
            name, value = line.decode().split(":", 1)
            headers[name.lower()] = value.strip()
        authorization = headers.get("authorization", "")
        if not authorization.startswith("Bearer ") or not _same_token(authorization[7:], CONTROL_TOKEN):
            await _reply(writer, "401 Unauthorized", {"error": "unauthorized"})
            return
        if method == "GET" and path == "/v1/status":
            await _reply(writer, "200 OK", state)
            return
        if method == "POST" and path == "/v1/deploy":
            length = int(headers.get("content-length", "0"))
            if length <= 0 or length > CONTROL_MAX_BODY_BYTES:
                await _reply(writer, "413 Payload Too Large", {"error": "invalid payload size"})
                return
            payload = json.loads((await reader.readexactly(length)).decode())
            _install(payload.get("files"))
            state["last_deploy"] = "installed; restarting"
            await _reply(writer, "200 OK", {"ok": True, "restarting": True})
            asyncio.create_task(_restart())
            return
        await _reply(writer, "404 Not Found", {"error": "not found"})
    except Exception as error:
        await _reply(writer, "400 Bad Request", {"error": str(error)[:80]})
    finally:
        try:
            writer.close()
            await writer.wait_closed()
        except Exception:
            pass


async def serve(state):
    async def handler(reader, writer):
        await _handle(reader, writer, state)
    server = await asyncio.start_server(handler, "0.0.0.0", CONTROL_PORT)
    await server.wait_closed()
