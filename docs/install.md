# Install Steamling

These steps are written for the Retroid Pocket 6. On the other handhelds (all untested ports,
see [Supported devices](devices.md)) the idea is the same, but the Android menus and the
bootloader's device model differ; that page points to model-specific help.

Steamling runs from a microSD card. Once it is up you can [move it to internal
storage](install-to-internal.md) for faster loading.

**You need** a microSD card: 64 GB works but fills up fast once games are installed, so 128 GB or
larger is recommended.

## 1. Flash the SD card

Build the image yourself with the [build guide](building/README.md), or grab one from the
[Releases](https://github.com/dvandenburgh/steamling/releases) page once there are some (those are
compressed, but balenaEtcher opens them as they are). Flash it to the microSD card with
[balenaEtcher](https://etcher.balena.io/), Rufus or `dd`.

## 2. Install the bootloader (OpenABL)

OpenABL replaces the stock bootloader with one that can boot Linux from the SD card or internal
storage. It is **required** on every device. (It used to be called the ROCKNIX ABL. If you already
flashed that one, it still works, and you can move to OpenABL later from Steamling Tools.)

The flashed SD card carries the install kit in its `rocknix_abl` folder, visible from Android when
the card is inserted. The folder kept the old name so older backups still line up.

1. Copy the `rocknix_abl` folder from the SD card to the root of Android's internal storage.
2. Open **Settings → Handheld Settings → Advanced → Run Script as Root** (that's where it is on
   Retroid handhelds; AYN, AYANEO and the others put it elsewhere), go into the `rocknix_abl`
   folder you just copied, and run `backup_abl.sh` (saves your stock bootloader next to the
   scripts), then `flash_abl.sh`.
3. **(Recommended)** copy the `abl_a.img` / `abl_b.img` backups from that folder to somewhere off
   the device. Installing Steamling to internal storage later wipes Android's data, backups
   included, and they are the only way back to the factory bootloader (see
   [restoring the stock bootloader](install-to-internal.md#restoring-the-stock-bootloader)).

## 3. Boot Steamling

1. Hold **Volume −** while powering on to open the ABL menu. Volume keys move through the entries,
   the power key selects.
2. Set **Boot mode** to **Linux** and **Boot source** to **SD card**, and **set Device model
   to Retroid Pocket 6** (a wrong model gives a black screen). Then pick **Start**.
3. Insert the flashed microSD and boot.

The first boot into game mode can take a long while, especially from an SD card. Leave it be; it
will come up.

> [!IMPORTANT]
> **Then change the default password.** It is `root` and publicly known: run `passwd` (and
> `sudo passwd root`) in a terminal. SSH is off by default.

## Updating

Steamling doesn't have its own update server yet, so for now a new version of Steamling means
flashing a newer image (your games and saves live on the card, so back up anything you care about
first). Once the update server is up, updates will arrive without reflashing, through any of:

- **Steamling Control**: Quick Access Menu → **Steamling Control** → **Updater** →
  **Check for Updates** → **Install Updates**, without leaving game mode.
- **Steamling Updater**: in desktop mode, launch the **Steamling Updater** app.
- **Terminal**: `sudo pacman -Syu`, like any Arch system.

The Steam client updates itself separately and tells you when one is available. If an update goes
wrong, see [snapshots and rollback](snapshots.md).
