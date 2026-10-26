from pathlib import Path

STEAM_ROOT = Path("/home/deck/.local/share/Steam")
STEAM_APPS_DIR = STEAM_ROOT / "steamapps"


# Re-parsing every appmanifest costs real time, more so under FEX on an x86 loader, and the panel asks on
# every open. Steam writes manifests by rename, so a library change always moves the mtime of
# its steamapps dir, and an added or removed library moves libraryfolders.vdf: that is the key.
_cache = {"key": None, "games": []}


def _mtime(path):
    try:
        return path.stat().st_mtime_ns
    except OSError:
        return None


def installed_games():
    library_files = (STEAM_APPS_DIR / "libraryfolders.vdf", STEAM_ROOT / "config/libraryfolders.vdf")
    dirs = _steamapps_dirs(library_files)
    key = tuple((str(p), _mtime(p)) for p in (*library_files, *dirs))
    if key != _cache["key"]:
        _cache["games"] = _scan(dirs)
        _cache["key"] = key
    return [dict(game) for game in _cache["games"]]


def _steamapps_dirs(library_files):
    steamapps_dirs = {STEAM_APPS_DIR}
    for library_file in library_files:
        try:
            lines = library_file.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            continue
        for line in lines:
            parts = line.strip().split('"')
            if len(parts) >= 4 and parts[1] == "path":
                steamapps_dirs.add(Path(parts[3]) / "steamapps")
    return sorted(steamapps_dirs)


def _scan(steamapps_dirs):
    games = []
    seen = set()
    for steamapps_dir in steamapps_dirs:
        for manifest in sorted(steamapps_dir.glob("appmanifest_*.acf")):
            values = {}
            try:
                lines = manifest.read_text(encoding="utf-8", errors="replace").splitlines()
            except OSError:
                continue
            for line in lines:
                parts = line.strip().split('"')
                if len(parts) >= 4 and parts[1] in ("appid", "name"):
                    values[parts[1]] = parts[3]
            appid = values.get("appid")
            name = values.get("name")
            if appid and name and appid not in seen:
                games.append({"appid": str(appid), "name": name})
                seen.add(appid)
    return sorted(games, key=lambda game: game["name"].casefold())
