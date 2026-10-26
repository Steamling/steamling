import json
import struct
import threading
from pathlib import Path

from .system import atomically_write

# Rumble on these handhelds runs through the gamepad driver into a separate vibration motor
# driver. Two knobs exist, both lost at reboot, so the choice is kept here and re-applied when
# the plugin loads:
#  - rumble_enable, a parameter of the gamepad drivers (rsinput, retroid): on or off.
#  - the force-feedback gain of the motor's own input device: how strong.
CONFIG = Path("/etc/steamling/rumble.json")
MODULES = Path("/sys/module")
INPUT = Path("/sys/class/input")
DEV_INPUT = Path("/dev/input")

# Motor drivers whose gain we set, and the gain that means full strength for each. The Qualcomm
# haptics driver scales by gain/0x7fff (anything above counts as full); ff-memless ones by
# gain/0xffff.
MOTORS = {"qcom-hv-haptics": 0x7FFF, "pwm-vibrator": 0xFFFF, "gpio-vibrator": 0xFFFF}
STRENGTHS = (25, 50, 75, 100)
DEFAULTS = {"enabled": True, "strength": 100}

EV_FF = 0x15
FF_GAIN = 0x60
_lock = threading.Lock()


def _switches(modules=MODULES):
    return sorted(modules.glob("*/parameters/rumble_enable"))


def _motors(input_dir=INPUT):
    found = []
    for dev in sorted(input_dir.glob("event*")):
        try:
            name = (dev / "device/name").read_text().strip()
        except OSError:
            continue
        if name in MOTORS:
            found.append((dev.name, MOTORS[name]))
    return found


def gain_for(strength, full):
    return max(1, round(full * strength / 100))


def _event(code, value):
    # struct input_event on 64-bit: a timeval (two longs), then type, code, value.
    return struct.pack("llHHi", 0, 0, EV_FF, code, value)


def load():
    try:
        data = json.loads(CONFIG.read_text())
    except (OSError, ValueError):
        data = {}
    out = dict(DEFAULTS)
    if isinstance(data, dict):
        if isinstance(data.get("enabled"), bool):
            out["enabled"] = data["enabled"]
        if data.get("strength") in STRENGTHS:
            out["strength"] = data["strength"]
    return out


def apply(settings, modules=MODULES, input_dir=INPUT, dev_input=DEV_INPUT):
    for switch in _switches(modules):
        try:
            switch.write_text("1" if settings["enabled"] else "0")
        except OSError as exc:
            print(f"steamling-control: could not set {switch}: {exc}")
    for event, full in _motors(input_dir):
        try:
            with open(dev_input / event, "wb", buffering=0) as f:
                f.write(_event(FF_GAIN, gain_for(settings["strength"], full)))
        except OSError as exc:
            print(f"steamling-control: could not set rumble strength on {event}: {exc}")


def rumble_status(modules=MODULES, input_dir=INPUT):
    settings = load()
    return {
        "canSwitch": bool(_switches(modules)),
        "canScale": bool(_motors(input_dir)),
        "enabled": settings["enabled"],
        "strength": settings["strength"],
    }


def set_rumble(enabled, strength):
    if strength not in STRENGTHS:
        raise ValueError(f"strength must be one of {STRENGTHS}")
    settings = {"enabled": bool(enabled), "strength": strength}
    with _lock:
        atomically_write(CONFIG, json.dumps(settings) + "\n", 0o644)
        apply(settings)
    return rumble_status()


def restore_rumble():
    # Only once someone has chosen: a fresh install leaves the drivers as they boot.
    if CONFIG.exists():
        with _lock:
            apply(load())
