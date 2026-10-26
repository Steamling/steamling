import json
import threading
from pathlib import Path

from .system import atomically_write, run_cmd

# Back paddles are remapped with an InputPlumber device profile, so the change happens before
# any app sees the pad: in game mode, desktop mode and emulators outside Steam alike.
# steamling-gamepad-target --apply loads the same file again whenever InputPlumber restarts.
PROFILE = Path("/etc/steamling/gamepad-profile.json")
STOCK_PROFILE = "/usr/share/inputplumber/profiles/default.yaml"
SERVICE = "org.shadowblip.InputPlumber"
IFACE = "org.shadowblip.Input.CompositeDevice"

# "" keeps the paddle as the Steam Deck back button (L4/R4), what game mode expects by default.
TARGETS = ("", "South", "East", "West", "North", "LeftBumper", "RightBumper",
           "LeftStick", "RightStick", "Select", "Start")
PADDLES = {"left": "LeftPaddle1", "right": "RightPaddle1"}
# Some controllers report their back buttons as LeftTop/RightTop, which InputPlumber's stock
# profile turns into the paddles; a remap has to catch those too.
TOP_ALIASES = {"left": "LeftTop", "right": "RightTop"}

_lock = threading.Lock()


def _button(name):
    return {"gamepad": {"button": name}}


# InputPlumber's own default profile, which ours replaces, so it is carried over as is.
STOCK_MAPPINGS = [
    {"name": "LeftTop", "source_event": _button("LeftTop"), "target_events": [_button("LeftPaddle1")]},
    {"name": "RightTop", "source_event": _button("RightTop"), "target_events": [_button("RightPaddle1")]},
    {"name": "Keyboard", "source_event": _button("Keyboard"), "target_events": [_button("Guide"), _button("North")]},
    {"name": "QuickAccess2", "source_event": _button("QuickAccess2"), "target_events": [_button("Screenshot")]},
] + [
    {"name": f"{side} Dial {turn}",
     "source_event": {"gamepad": {"dial": {"name": f"{side}StickDial", "direction": turn}}},
     "target_events": [{"keyboard": key}]}
    for side, turn, key in (("Left", "counter-clockwise", "KeyVolumeDown"), ("Left", "clockwise", "KeyVolumeUp"),
                            ("Right", "counter-clockwise", "KeyBrightnessDown"), ("Right", "clockwise", "KeyBrightnessUp"))
]


def build_profile(left, right):
    remap = {"left": left, "right": right}
    mappings = []
    for mapping in STOCK_MAPPINGS:
        side = next((s for s, alias in TOP_ALIASES.items() if mapping["name"] == alias), None)
        if side and remap[side]:
            continue
        mappings.append(mapping)
    for side, target in remap.items():
        if not target:
            continue
        for source in (PADDLES[side], TOP_ALIASES[side]):
            mappings.append({"name": f"Steamling {source}", "source_event": _button(source),
                             "target_events": [_button(target)]})
    return {"version": 1, "kind": "DeviceProfile", "name": "Steamling", "mapping": mappings}


def load(path=PROFILE):
    try:
        data = json.loads(path.read_text())
    except (OSError, ValueError):
        return {"left": "", "right": ""}
    out = {"left": "", "right": ""}
    for mapping in data.get("mapping", []) if isinstance(data, dict) else []:
        for side, paddle in PADDLES.items():
            if mapping.get("name") == f"Steamling {paddle}":
                target = (mapping.get("target_events") or [{}])[0].get("gamepad", {}).get("button", "")
                out[side] = target if target in TARGETS else ""
    return out


def _host(args, timeout=10):
    return run_cmd(["systemd-run", "--quiet", "--collect", "--wait", "--pipe", *args], timeout=timeout)


def _composites():
    proc = _host(["busctl", "--list", "tree", SERVICE])
    if proc is None or proc.returncode != 0:
        return []
    return [p for p in proc.stdout.split() if p.rsplit("/", 1)[-1].startswith("CompositeDevice")]


def _has_paddles(path):
    proc = _host(["busctl", "--json=short", "get-property", SERVICE, path, IFACE, "Capabilities"])
    if proc is None or proc.returncode != 0:
        return False
    try:
        caps = json.loads(proc.stdout).get("data", [])
    except ValueError:
        return False
    return any(f"Gamepad:Button:{p}" in caps for p in PADDLES.values())


def _pads():
    return [p for p in _composites() if _has_paddles(p)]


def _load_profile(path, profile_path):
    proc = _host(["busctl", "call", SERVICE, path, IFACE, "LoadProfilePath", "s", profile_path])
    return proc is not None and proc.returncode == 0


def paddle_status():
    return {"available": bool(_pads()), **load()}


def set_paddles(left, right):
    if left not in TARGETS or right not in TARGETS:
        raise ValueError("unsupported paddle mapping")
    with _lock:
        if left or right:
            atomically_write(PROFILE, json.dumps(build_profile(left, right), indent=2) + "\n", 0o644)
            profile_path = str(PROFILE)
        else:
            PROFILE.unlink(missing_ok=True)
            profile_path = STOCK_PROFILE
        failed = [p for p in _pads() if not _load_profile(p, profile_path)]
    if failed:
        raise RuntimeError("InputPlumber did not take the new mapping; it applies after a restart")
    return paddle_status()
