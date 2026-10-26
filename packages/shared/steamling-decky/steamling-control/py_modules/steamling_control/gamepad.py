import threading

from .system import run_cmd
from .tweaks import load_tweaks

# Which virtual pad InputPlumber shows the system while a game runs. Game mode itself uses the
# Steam Deck pad (steamling-steam); a game can ask for another one, which matters when Steam
# Input is turned off for it and the game reads the pad directly.
TARGET_TOOL = "/usr/bin/steamling-gamepad-target"
SESSION_DEFAULT = "deck-uhid"
GAME_TYPES = ("xb360", "xbox-series", "ds5")

_lock = threading.Lock()
# What this plugin last switched to; None = it hasn't touched the pad, so the session's own
# choice stands.
_applied = {"kind": None}


def gamepad_for(tweaks, appid):
    # Same merge as steamling-game-launch: per-game values only count while the game is enabled.
    if not appid:
        return ""
    settings = dict(tweaks.get("global") or {})
    game = (tweaks.get("games") or {}).get(str(appid))
    if isinstance(game, dict) and game.get("enabled") is True:
        settings.update(game)
    kind = str(settings.get("gamepadType") or "")
    return kind if kind in GAME_TYPES else ""


def _switch(kind):
    # Through PID 1 like the other helpers, so it runs in the host's namespace and environment.
    proc = run_cmd(["systemd-run", "--quiet", "--collect", "--wait", "--pipe", TARGET_TOOL, kind], timeout=30)
    return proc is not None and proc.returncode == 0


def sync_gamepad(running_appid, switch=_switch, tweaks=None):
    want = gamepad_for(tweaks if tweaks is not None else load_tweaks(), running_appid)
    with _lock:
        current = _applied["kind"]
        if not want and current is None:
            return None
        kind = want or SESSION_DEFAULT
        if kind == current:
            return kind
        if switch(kind):
            # Back on the session default means we no longer hold the pad.
            _applied["kind"] = None if kind == SESSION_DEFAULT else kind
        else:
            print(f"steamling-control: could not switch the controller to {kind}")
        return kind
