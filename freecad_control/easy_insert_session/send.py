"""Send a Python script to the connected FreeCAD GUI."""
import argparse
import json
import os
from pathlib import Path
import time
import uuid


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("script", type=Path)
    parser.add_argument("--timeout", type=float, default=30)
    args = parser.parse_args()
    root = Path(__file__).resolve().parent
    try:
        status = json.loads((root / "status.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        parser.exit(1, "FreeCAD is not connected. Run Connect.FCMacro first.\n")
    if time.time() - status["time"] > 10:
        parser.exit(1, "FreeCAD heartbeat is stale. Run Connect.FCMacro again.\n")
    name = uuid.uuid4().hex
    target = root / "inbox" / (name + ".json")
    temporary = target.with_suffix(".tmp")
    temporary.write_text(json.dumps({"code": args.script.read_text(encoding="utf-8")}), encoding="utf-8")
    os.replace(temporary, target)
    response = root / "outbox" / target.name
    deadline = time.monotonic() + args.timeout
    while time.monotonic() < deadline:
        if response.exists():
            value = json.loads(response.read_text(encoding="utf-8"))
            print(json.dumps(value, ensure_ascii=False, indent=2))
            return 0 if value["ok"] else 1
        time.sleep(0.2)
    parser.exit(1, "Timed out; the command may still execute. Do not blindly resend it.\n")


if __name__ == "__main__":
    raise SystemExit(main())
