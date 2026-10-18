import re
import threading
from pathlib import Path

from .system import run_cmd

# The microSD slot is mmcblk0, the internal OS disk sda. This constant is UI convenience only:
# the formatter is the safety boundary (mmcblk-only, refuses the disk backing /).
SD_DISK = "/dev/mmcblk0"
SD_PART = "/dev/mmcblk0p1"
FORMATTER = "/usr/lib/hwsupport/format-device.sh"

LABEL_RE = re.compile(r"^[A-Za-z0-9_-]{1,16}$")  # ext4 volume labels cap at 16 bytes

_format_lock = threading.Lock()  # one format at a time; a second RPC fails fast


# The panel polls this while it is open, from a Python that runs emulated under FEX, so it reads
# the kernel and udev directly rather than spawning lsblk and findmnt. /proc/1/mountinfo is PID
# 1's table, what `findmnt -N 1` reads: the loader runs in its own mount namespace
# (steamling-decky-run), and the host's table is the authoritative one for the UI.
SYS_BLOCK = Path("/sys/class/block")
UDEV_DATA = Path("/run/udev/data")
MOUNTINFO = Path("/proc/1/mountinfo")


def _unescape(text):
    # mountinfo octal-escapes space, tab, newline and backslash; udev's *_ENC values use \xNN
    text = re.sub(r"\\([0-7]{3})", lambda m: chr(int(m.group(1), 8)), text)
    return re.sub(r"\\x([0-9a-fA-F]{2})", lambda m: chr(int(m.group(1), 16)), text)


def _devno(name):
    try:
        return (SYS_BLOCK / name / "dev").read_text().strip()
    except OSError:
        return ""


def _udev_props(name):
    devno = _devno(name)
    props = {}
    try:
        lines = (UDEV_DATA / f"b{devno}").read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return props
    for line in lines:
        if line.startswith("E:") and "=" in line:
            key, _, value = line[2:].partition("=")
            props[key] = value
    return props


def _mounts():
    # (mount point, source device name) per line, from the source field after " - "
    out = []
    try:
        lines = MOUNTINFO.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return out
    for line in lines:
        head, sep, tail = line.partition(" - ")
        fields, rest = head.split(), tail.split()
        if sep and len(fields) >= 5 and len(rest) >= 2 and rest[1].startswith("/dev/"):
            out.append((_unescape(fields[4]), Path(_unescape(rest[1])).name))
    return out


# Which disk the system boots from cannot change without a reboot, so the answer is kept once
# findmnt has given one. findmnt resolves what mountinfo cannot: a kernel-mounted root reads
# /dev/root there, and btrfs SOURCE carries a [/subvol] suffix. /flash counts: a card can hold
# boot without hosting /.
_boot_cache = {}


def _boots_from(disk):
    if disk in _boot_cache:
        return _boot_cache[disk]
    answered = False
    for target in ("/", "/flash"):
        proc = run_cmd(["findmnt", "-N", "1", "-fno", "SOURCE", target], timeout=10)
        if proc is None or proc.returncode != 0:
            continue
        answered = answered or target == "/"
        src = (proc.stdout or "").strip().split("[")[0]
        if not src.startswith("/dev/"):
            continue
        parent = run_cmd(["lsblk", "-no", "PKNAME", src], timeout=10)
        name = (parent.stdout or "").strip().splitlines() if parent and parent.returncode == 0 else []
        node = f"/dev/{name[0].strip()}" if name and name[0].strip() else src
        if node == disk:
            _boot_cache[disk] = True
            return True
    if answered:
        _boot_cache[disk] = False
    return False


def detect_sdcard():
    absent = {"present": False}
    disk = Path(SD_DISK).name
    if not Path(SD_DISK).exists() or not (SYS_BLOCK / disk).exists():
        return absent
    try:
        size = int((SYS_BLOCK / disk / "size").read_text().strip()) * 512
    except (OSError, ValueError):
        size = 0
    # A partitioned card carries fs info on p1; a superfloppy carries it on the disk node.
    parts = sorted(p.name for p in (SYS_BLOCK / disk).iterdir() if p.name.startswith(disk + "p"))
    fs_name = parts[0] if parts else disk
    props = _udev_props(fs_name)
    label = props.get("ID_FS_LABEL_ENC")
    label = _unescape(label) if label is not None else props.get("ID_FS_LABEL", "")
    mounts = _mounts()
    mountpoint = next((target for target, source in mounts if source == fs_name), "")
    return {
        "present": True,
        "device": SD_DISK,
        "sizeBytes": size,
        "fstype": props.get("ID_FS_TYPE", ""),
        "label": label,
        "mountpoint": mountpoint,
        "bootDisk": _boots_from(SD_DISK),
    }


def format_sdcard(label):
    label = (label or "").strip() or "SDCARD"
    if not LABEL_RE.match(label):
        raise ValueError("Label must be 1-16 characters: letters, digits, - or _")
    if not Path(SD_DISK).exists():
        raise RuntimeError("No microSD card detected")
    if _boots_from(SD_DISK):
        raise RuntimeError("This device booted from the SD card; it cannot be formatted")
    if not _format_lock.acquire(blocking=False):
        raise RuntimeError("A format is already in progress")
    try:
        # systemd-run, not a direct call: run in our private mount namespace the formatter's
        # umount detaches the card only locally, leaving the init-ns mount live under mkfs.
        # PID 1 also gives it a clean env, free of the PyInstaller LD_LIBRARY_PATH poisoning.
        proc = run_cmd(
            ["systemd-run", "--quiet", "--collect", "--wait", "--pipe",
             FORMATTER, "--device", SD_DISK, "--label", label, "--force"],
            timeout=600,
        )
    finally:
        _format_lock.release()
    if proc is None:
        raise RuntimeError("Formatter failed to spawn")
    if proc.returncode != 0:
        detail = ((proc.stderr or "") + (proc.stdout or "")).strip()[-300:]
        raise RuntimeError(f"Format failed (rc={proc.returncode}): {detail}")
    return detect_sdcard()
