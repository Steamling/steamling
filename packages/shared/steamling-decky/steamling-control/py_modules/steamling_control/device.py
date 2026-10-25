import os
from pathlib import Path

from .system import run_cmd

# The same helpers the Steamling Tools menu uses, so both UIs agree on what "on" means.
SSH = "/usr/bin/steamling-ssh"
UPDATE_ABL = "/usr/bin/steamling-update-abl"
SESSION_SELECT = "/usr/bin/steamos-session-select"
OS_RELEASE = Path("/usr/lib/os-release")
KERNEL_RELEASE = Path("/proc/sys/kernel/osrelease")
HOME = Path("/home/deck")
SSHD = Path("/usr/bin/sshd")


def _host(args, timeout):
    # This python is an x86_64 FEX guest whose rootfs shadows bash and systemctl; systemd-run
    # hands the aarch64 command to PID 1 instead (sharing.py, updates.py).
    return run_cmd(
        ["systemd-run", "--quiet", "--collect", "--wait", "--pipe", *args],
        timeout=timeout,
    )


def _pairs(text):
    out = {}
    for line in (text or "").splitlines():
        key, sep, value = line.partition("=")
        if sep:
            out[key.strip()] = value.strip().strip('"')
    return out


def _read(path):
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def _abl():
    proc = _host([UPDATE_ABL, "--status"], timeout=30)
    info = _pairs(proc.stdout if proc and proc.returncode == 0 else "")
    state = info.get("state", "")
    shipped = info.get("shipped_version", "")
    if state == "uptodate":
        return f"OpenABL {shipped}, up to date"
    if state == "differs":
        return f"Not the bundled OpenABL {shipped}. Update it from Steamling Tools in desktop mode."
    if state == "mixed":
        return "The two bootloader slots differ. Update from Steamling Tools to make them match."
    if state == "nopart":
        return "Running from the SD card"
    return ""


def device_info():
    release = _pairs(_read(OS_RELEASE))
    return {
        "osVersion": release.get("VERSION") or release.get("VERSION_ID") or "unknown",
        "kernel": _read(KERNEL_RELEASE).strip() or "unknown",
        "bootloader": _abl(),
    }


def _addresses():
    proc = _host(["/usr/bin/ip", "-4", "-o", "addr", "show", "scope", "global"], timeout=10)
    found = []
    for line in (proc.stdout if proc and proc.returncode == 0 else "").splitlines():
        fields = line.split()
        if "inet" in fields:
            addr = fields[fields.index("inet") + 1].split("/")[0]
            if addr not in found:
                found.append(addr)
    return found


def ssh_status():
    # No openssh, no toggle: steamling-ssh would report "off" and then fail to turn it on.
    proc = _host([SSH, "status"], timeout=15) if SSHD.exists() else None
    if proc is None or proc.returncode != 0:
        return {"available": False, "on": False, "addresses": []}
    on = _pairs(proc.stdout).get("state") == "on"
    return {"available": True, "on": on, "addresses": _addresses() if on else []}


def set_ssh(on):
    proc = _host([SSH, "on" if on else "off"], timeout=60)
    if proc is None or proc.returncode != 0:
        detail = ((proc.stderr if proc else "") or "").strip()[-200:]
        raise RuntimeError(f"Could not turn SSH {'on' if on else 'off'}: {detail or 'no detail'}")
    return ssh_status()


def restart_game_mode():
    # Same path as Steam's own session switch: the supervisor relaunches game mode once
    # gamescope exits. Runs as the session user so the choice lands in their state file.
    uid = os.stat(HOME).st_uid
    proc = _host(
        [f"--uid={uid}", f"--setenv=XDG_RUNTIME_DIR=/run/user/{uid}", f"--setenv=HOME={HOME}",
         SESSION_SELECT, "gamescope"],
        timeout=30,
    )
    if proc is None or proc.returncode != 0:
        detail = ((proc.stderr if proc else "") or "").strip()[-200:]
        raise RuntimeError(f"Could not restart game mode: {detail or 'no detail'}")
    return True
