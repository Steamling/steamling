import os
from pathlib import Path

# steamling-steam points MANGOHUD_CONFIGFILE at this file for the whole session; Steam writes
# its Performance Overlay level here and mangoapp re-reads the file whenever it changes.
HOME = Path("/home/deck")
FILE_NAME = "steamling-mangohud.conf"

# MangoHud's built-in presets, the same ones Steam's overlay levels pick.
LEVELS = {
    "off": "no_display",
    "fps": "preset=1",
    "compact": "preset=2",
    "detailed": "preset=3",
    "full": "preset=4",
}


def _path(home=HOME):
    try:
        uid = os.stat(home).st_uid
    except OSError:
        return None
    return Path(f"/run/user/{uid}/{FILE_NAME}")


def level_of(text):
    lines = [line.strip() for line in (text or "").splitlines() if line.strip() and not line.strip().startswith("#")]
    if not lines or "no_display" in lines or "no_display=1" in lines:
        return "off"
    for line in lines:
        key, _, value = line.partition("=")
        if key.strip() == "preset":
            preset = f"preset={value.strip().split(',')[0]}"
            for level, content in LEVELS.items():
                if content == preset:
                    return level
    # Something we didn't write (Steam's own settings, or a hand edit): it's showing.
    return "custom"


def overlay_status(path=None):
    path = path or _path()
    if path is None or not path.exists():
        return {"available": False, "level": "off"}
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return {"available": False, "level": "off"}
    return {"available": True, "level": level_of(text)}


def set_overlay(level, path=None):
    if level not in LEVELS:
        raise ValueError(f"unknown overlay level: {level!r}")
    path = path or _path()
    if path is None or not path.exists():
        raise RuntimeError("The performance overlay is only available in game mode")
    # Rewritten in place, never replaced: mangoapp watches this inode for changes.
    with path.open("w", encoding="utf-8") as f:
        f.write(LEVELS[level] + "\n")
    return overlay_status(path)
