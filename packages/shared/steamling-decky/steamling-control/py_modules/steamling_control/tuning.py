from pathlib import Path

from . import calibration
from .system import atomically_write

# How the sticks respond, on top of the calibration: a bigger or smaller dead zone round the
# centre, and full tilt reached before the stick hits its edge. Stored as percentages of the
# calibrated values (or the driver's defaults when uncalibrated), so recalibrating keeps the
# preference. steamling-gamepad-calibration-restore applies the same maths at boot.
TUNING = Path("/etc/steamling/gamepad-tuning.conf")
STICKS = {"left": ("axis_leftx", "axis_lefty"), "right": ("axis_rightx", "axis_righty")}
DEADZONES = (50, 75, 100, 150, 200, 300)
OUTERS = (100, 95, 90, 85, 80)
DEFAULT = {"deadzone": 100, "outer": 100}


def load(path=TUNING):
    try:
        values = calibration._parse_kv(path.read_text())
    except OSError:
        values = {}
    out = {}
    for stick in STICKS:
        dz = values.get(f"{stick}_deadzone", 100)
        outer = values.get(f"{stick}_outer", 100)
        out[stick] = {"deadzone": dz if dz in DEADZONES else 100, "outer": outer if outer in OUTERS else 100}
    return out


def tuned(base, tuning):
    """Driver parameters for `tuning`, scaled from the untuned `base` values."""
    out = {}
    for stick, axes in STICKS.items():
        dz, outer = tuning[stick]["deadzone"], tuning[stick]["outer"]
        for axis in axes:
            for key, pct in (("deadzone", dz), ("antideadzone", dz), ("max", outer), ("min", outer)):
                name = f"{axis}_{key}"
                if name in base:
                    out[name] = int(base[name] * pct / 100)
    return out


def _base(params):
    try:
        values = calibration._parse_kv(calibration.CONF.read_text())
    except OSError:
        values = {}
    defaults = calibration._defaults(params)
    # Saved calibration first, the boot-time defaults for anything it lacks.
    return {**defaults, **{k: v for k, v in values.items() if k in defaults or (params / k).exists()}}


def apply(tuning=None):
    _name, _info, params = calibration._driver()
    if not params:
        return False
    values = tuned(_base(params), tuning or load())
    if values:
        calibration._write_params(params, values)
    return True


def tuning_status():
    _name, _info, params = calibration._driver()
    return {"available": bool(params), **load()}


def set_tuning(stick, deadzone, outer):
    if stick not in STICKS or deadzone not in DEADZONES or outer not in OUTERS:
        raise ValueError("unsupported stick setting")
    current = load()
    current[stick] = {"deadzone": deadzone, "outer": outer}
    lines = ["# Written by Governor: stick response, in percent of the calibrated values."]
    for name, values in current.items():
        lines += [f"{name}_deadzone={values['deadzone']}", f"{name}_outer={values['outer']}"]
    atomically_write(TUNING, "\n".join(lines) + "\n", 0o644)
    apply(current)
    return tuning_status()
