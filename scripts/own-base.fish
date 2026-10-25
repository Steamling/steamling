#!/usr/bin/env fish
# own-base.fish - cut Steamling's own frozen Arch Linux ARM base on an Arch or CachyOS x86_64 host,
# so builds and devices stop borrowing Pocknix's. docs/building/own-base.md explains each step;
# this runs them.
#
#   scripts/own-base.fish --remote <rclone destination> --url <public url> [--id <label>] [--yes]
#   e.g. scripts/own-base.fish --remote r2:steamling/repo/base --url https://repo.example.com/base
#
# It points config/steamling.conf at your base and unpins it, builds everything against live Arch
# Linux ARM, freezes exactly what that build installed with `make snapshot` (which uploads it and
# pins the config again), checks the URL serves it, then builds once more against the frozen base.
# Afterwards, commit config/steamling.conf and the new steamling-base.lock.

set -l root (path resolve (status dirname)/..)
cd $root; or exit 1

function step
    set_color --bold cyan; echo "==> $argv"; set_color normal
end
function fail
    set_color red; echo "error: $argv" >&2; set_color normal; exit 1
end

argparse 'remote=' 'url=' 'id=' y/yes h/help -- $argv; or exit 2
if set -q _flag_help; or not set -q _flag_remote; or not set -q _flag_url
    sed -n '4,7p' (status filename)
    exit 2
end
set -l remote $_flag_remote
set -l url (string trim --right --chars / -- $_flag_url)
set -l id (date -u +%Y%m%d)
set -q _flag_id; and set id $_flag_id
set -l conf config/steamling.conf

step "checking the host"
for t in git make rclone repo-add curl sudo
    command -q $t; or fail "$t is missing: sudo pacman -S --needed git make rclone pacman curl sudo"
end
switch (uname -m)
    case x86_64
        test -e /proc/sys/fs/binfmt_misc/qemu-aarch64
        or fail "aarch64 programs can't run here yet: sudo pacman -S --needed qemu-user-static qemu-user-static-binfmt, then reboot (docs/building/linux-host.md)"
    case aarch64
    case '*'
        fail "this needs an x86_64 or aarch64 host, not "(uname -m)
end
command -q ccache; or echo "note: no ccache on this host, so kernel rebuilds start from scratch (sudo pacman -S ccache)"
git diff --quiet -- $conf packages/shared/steamling-base-lock
or fail "$conf or the base lock has uncommitted changes; commit or stash them first"
rclone lsf --max-depth 1 $remote >/dev/null 2>&1; or rclone mkdir $remote
or fail "rclone can't reach $remote (set the remote up with: rclone config)"

echo
echo "  base label:   $id"
echo "  uploads to:   $remote"
echo "  served from:  $url"
echo "  This builds everything twice. Under qemu that takes hours, mostly the first time."
if not set -q _flag_yes
    read -l -P "  Go on? [y/N] " answer
    string match -qi y -- $answer; or exit 1
end

step "pointing $conf at your base, unpinned"
sed -i \
    -e "s|^: \"\${STEAMLING_BASE_URL:=.*}\"|: \"\${STEAMLING_BASE_URL:=$url}\"|" \
    -e "s|^: \"\${STEAMLING_BASE_RCLONE_REMOTE:=.*}\"|: \"\${STEAMLING_BASE_RCLONE_REMOTE:=$remote}\"|" \
    -e "s|^: \"\${STEAMLING_BASE_SNAPSHOT:=.*}\"|: \"\${STEAMLING_BASE_SNAPSHOT:=}\"|" \
    -e "s|^: \"\${ALARM_TARBALL:=.*}\"|: \"\${ALARM_TARBALL:=ArchLinuxARM-aarch64-latest.tar.gz}\"|" \
    -e "s|^: \"\${STEAMLING_ALARM_SHA256:=.*}\"|: \"\${STEAMLING_ALARM_SHA256:=}\"|" \
    -e "s|^: \"\${STEAMLING_ALARM_TARBALL_URL:=.*}\"|: \"\${STEAMLING_ALARM_TARBALL_URL:=\${ALARM_MIRROR}/\${ALARM_TARBALL}}\"|" \
    $conf
grep -q "STEAMLING_BASE_SNAPSHOT:=}" $conf; or fail "couldn't unpin $conf"

step "building against live Arch Linux ARM (make image)"
make image; or fail "the live build failed; fix it and run this again (it picks up where it stopped)"

step "freezing that build as base $id (make snapshot)"
env STEAMLING_SNAPSHOT_ID=$id make snapshot; or fail "make snapshot failed"

step "checking $url serves the new base"
curl -fsI $url/pocknix-base.db >/dev/null
or fail "$url/pocknix-base.db isn't reachable. Make the bucket public (or put a domain in front of it), then run: make image"

step "building against the frozen base (make image)"
make image; or fail "the build against the frozen base failed"

echo
step "done: base $id is live at $url"
echo "  Next: git add $conf packages/shared/steamling-base-lock/steamling-base.lock"
echo "        git commit -m \"base: our own snapshot $id\""
echo "  Devices move onto it with their next update once you publish packages too (docs/building/own-base.md)."
