<p align="center">
  <img src="docs/images/steamling-logo.svg" alt="Steamling: a little red dragon peeking over a handheld" width="300">
</p>

<h3 align="center">A SteamOS-style gaming system for Snapdragon handhelds, built on Arch Linux ARM</h3>

<p align="center">Turn it on, land in Steam, pick a game and play.</p>

<p align="center">
  <a href="LICENSE.md"><img alt="license: GPL-2.0-or-later" src="https://img.shields.io/badge/license-GPL--2.0--or--later-blue"></a>
</p>

<p align="center">
  <a href="docs/install.md"><b>Install</b></a> ·
  <a href="docs/building/README.md"><b>Build it yourself</b></a> ·
  <a href="docs/README.md"><b>Docs</b></a> ·
  <a href="docs/about.md"><b>About and thanks</b></a>
</p>

> [!WARNING]
> Steamling is new and experimental. It can break, and installing it means replacing your
> handheld's bootloader. Go in with that in mind.

## What it is

Steamling is my attempt at a SteamOS that feels at home on an ARM handheld. You boot straight into
Steam's gaming mode, Proton is picked for you, and Windows games run through FEX. Underneath it's
a normal Arch Linux ARM system, so you can drop into a desktop, install Flatpaks from Discover, or
open a terminal and do whatever you like.

- **Steam gaming mode** on the ARM Steam client, the same interface as a Steam Deck.
- **Tuned out of the box.** It ships its own kernel (based on ROCKNIX's), and the scheduler, fan
  curve and graphics drivers are set up for smooth frame times. Set a frame cap and play.
- **Steamling Control**, a Quick Access Menu plugin for per-game settings, fan and CPU modes,
  controller and screen calibration, stick lights, SD card formatting and file sharing.
- **Emulation** through ES-DE and a full set of emulators, if you want it.
- **A stable base.** Packages come from a frozen snapshot of Arch Linux ARM, so things don't shift
  under you. If you'd rather live on the edge, you can switch to rolling Arch.

## Supported devices

| Device | Chip | Status |
|---|---|---|
| Retroid Pocket 6 (and the TOP-DPAD model) | Snapdragon 8 Gen 2 (SM8550) | Being brought up |

The tree is laid out so more devices can be added later without reshuffling everything.

## Getting started

1. **Get an image.** Build one with the [build guide](docs/building/README.md). It's written so
   you can follow it even if you've never built anything on Linux. Ready-made images will go up
   on the [Releases](https://github.com/dvandenburgh/steamling/releases) page once there are some.
2. **Install it** by following the [install guide](docs/install.md).
3. **Play.** Launch a game, open the Quick Access Menu, go to **Performance** and set a
   **Framerate Limit**. If it still doesn't feel smooth, try the game's own vsync setting.

## Docs

- [Install guide](docs/install.md): flashing, the bootloader, first boot
- [Install to internal storage](docs/install-to-internal.md): faster loading, uninstalling, going back to stock
- [Steamling Control](docs/steamling-control.md): the Quick Access Menu plugin
- [Emulation](docs/emulation-setup.md): ES-DE, ROMs and BIOS files
- [Android apps](docs/waydroid.md): Waydroid
- [Snapshots and rollback](docs/snapshots.md): getting back from a bad update
- [Known issues](docs/known-issues.md)
- [Building Steamling](docs/building/README.md) and [contributing](CONTRIBUTING.md)
- [About Steamling](docs/about.md): where it came from, and the people it's built on

## Thanks

Steamling stands on a lot of other people's work. It started life as a fork of
[Pocknix](https://github.com/shuuri-labs/pocknix-os) by shuuri-labs, its kernel and device
support come from [ROCKNIX](https://github.com/ROCKNIX/distribution), and much of the handheld
polish comes from [armada](https://github.com/armada-os/armada). The full list, with my thanks,
is in [About Steamling](docs/about.md).

## License

[GPL-2.0-or-later](LICENSE.md). Third-party parts keep their own licenses; see
[docs/licensing.md](docs/licensing.md).
