"""Upload an allow-listed code update to an Interstate 75 W control endpoint."""
import base64
import json
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).parent
CONFIG_PATH = ROOT / "deploy.local.json"
FILES = ("config.py", "control_server.py", "display.py", "main.py", "ptv.py", "wifi.py")


def main():
    if not CONFIG_PATH.exists():
        raise SystemExit("Copy deploy.example.json to deploy.local.json and fill it in.")
    config = json.loads(CONFIG_PATH.read_text())
    files = {
        name: base64.b64encode((ROOT / name).read_bytes()).decode("ascii")
        for name in FILES
    }
    address = "http://%s:%s/v1/deploy" % (config["host"], config.get("port", 8080))
    request = Request(
        address,
        data=json.dumps({"files": files}).encode(),
        headers={"Authorization": "Bearer " + config["token"], "Content-Type": "application/json"},
        method="POST",
    )
    with urlopen(request, timeout=15) as response:
        print(response.read().decode())


if __name__ == "__main__":
    main()
