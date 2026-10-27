import json
import os
import threading
import time
from pathlib import Path

from .system import atomically_write

# steamling-steam points MANGOHUD_CONFIGFILE at this file for the whole session; Steam writes
# its Performance Overlay level here and mangoapp re-reads the file whenever it changes.
HOME = Path("/home/deck")
FILE_NAME = "steamling-mangohud.conf"
# The level picked here. Steam writes its own level into the file when a game starts and the
# session starts it at no_display, so the pick is kept here and put back at those moments.
SAVED = Path("/etc/steamling/overlay.json")
# Steam's write lands a moment after the start notification: check a few times, then leave the
# file alone so a change made with Steam's own slider mid-game stays.
REASSERT_AFTER_S = (1, 3, 6)
_lock = threading.Lock()

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


def _write(path, level):
    # Rewritten in place, never replaced: mangoapp watches this inode for changes.
    with path.open("w", encoding="utf-8") as f:
        f.write(LEVELS[level] + "\n")


def saved_level(saved=SAVED):
    try:
        level = json.loads(saved.read_text()).get("level")
    except (OSError, ValueError, AttributeError):
        return None
    return level if level in LEVELS else None


def set_overlay(level, path=None, saved=SAVED):
    if level not in LEVELS:
        raise ValueError(f"unknown overlay level: {level!r}")
    path = path or _path()
    if path is None or not path.exists():
        raise RuntimeError("The performance overlay is only available in game mode")
    with _lock:
        _write(path, level)
        atomically_write(saved, json.dumps({"level": level}) + "\n", 0o644)
    return overlay_status(path)


def reassert_overlay(path=None, saved=SAVED, delays=REASSERT_AFTER_S, sleep=time.sleep):
    """Put the saved level back if Steam overwrote it; nothing if no level was ever picked here."""
    level = saved_level(saved)
    if level is None:
        return
    for delay in delays:
        sleep(delay)
        target = path or _path()
        if target is None or not target.exists():
            continue
        with _lock:
            try:
                current = level_of(target.read_text(encoding="utf-8", errors="replace"))
            except OSError:
                continue
            if current != level:
                _write(target, level)


def reassert_in_background():
    threading.Thread(target=reassert_overlay, daemon=True).start()
