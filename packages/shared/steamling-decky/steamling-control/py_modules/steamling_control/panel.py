"""Panel refresh calibration: trims the panel to its nominal refresh through the driver's
frame_len_<rate> attributes (RP6). steamling-panel-calibration (steamling-bsp-common) does the
measuring and owns the conf; its unit writes the saved values back at boot."""

import json
import threading
from pathlib import Path

from .system import run_cmd

TOOL = "/usr/lib/steamling/steamling-panel-calibration"
CONF = Path("/etc/steamling/panel-calibration.conf")
DSI = Path("/sys/bus/mipi-dsi/devices")

# A run holds the vblank loop for up to a minute; one at a time.
_lock = threading.Lock()


def _host(args, timeout):
    # The tool runs as the host python under PID 1 (see sharing.py).
    return run_cmd(["systemd-run", "--quiet", "--collect", "--wait", "--pipe", *args], timeout=timeout)


def status():
    # Read straight from sysfs and the conf: no transient unit for a status read.
    available = Path(TOOL).exists() and DSI.is_dir() and any(DSI.glob("*/frame_len_*"))
    return {"available": available, "saved": CONF.exists(), "running": _lock.locked()}


def _fail(proc, what):
    detail = ((proc.stderr if proc else "") or "").strip().splitlines()
    detail = detail[-1].removeprefix("steamling-panel-calibration: ") if detail else ""
    raise RuntimeError(f"{what}: {detail or 'timed out'}")


def run():
    if not _lock.acquire(blocking=False):
        raise RuntimeError("Calibration is already running")
    try:
        proc = _host([TOOL, "run"], timeout=90)
        if proc is None or proc.returncode != 0:
            _fail(proc, "Calibration failed")
        try:
            result = json.loads(proc.stdout.strip().splitlines()[-1])
        except (ValueError, IndexError):
            result = {}
    finally:
        _lock.release()
    return {**status(), "result": result}


def reset():
    if not _lock.acquire(blocking=False):
        raise RuntimeError("Calibration is running")
    try:
        proc = _host([TOOL, "reset"], timeout=15)
        if proc is None or proc.returncode != 0:
            _fail(proc, "Could not reset")
    finally:
        _lock.release()
    return status()
