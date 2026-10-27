from pathlib import Path

from .touch import touchscreens

# What this handheld actually has, so the panel only offers controls that do something here.
HWMON = Path("/sys/class/hwmon")
SCX_LAVD = Path("/usr/bin/scx_lavd")
SCHED_EXT = Path("/sys/kernel/sched_ext")
LAVD_MODE = Path("/usr/bin/steamling-lavd-mode")


def has_fan(hwmon=HWMON):
    # The same test steamling-fancontrol makes before it does anything.
    return any(hwmon.glob("hwmon*/pwm1"))


def has_scheduler(binary=SCX_LAVD, sched_ext=SCHED_EXT, helper=LAVD_MODE):
    # scx_lavd ships separately (scx-scheds) and needs a kernel with sched_ext.
    return binary.exists() and sched_ext.is_dir() and helper.exists()


def hardware():
    return {
        "fan": has_fan(),
        "scheduler": has_scheduler(),
        "touchscreen": bool(touchscreens()),
    }
