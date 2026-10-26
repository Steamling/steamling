# Heroic Games Launcher

[Heroic](https://heroicgameslauncher.com) plays your **Epic**, **GOG** and **Amazon** games. It
comes with Steamling and shows up in your Steam library as **Heroic Games Launcher**, so you can
start it from game mode like any game. It's also in the app list in desktop mode.

> [!NOTE]
> Heroic on Steamling is new and hasn't been tried with many games yet. If a game won't start,
> the steps under [When a game won't start](#when-a-game-wont-start) are worth a go, and a bug
> report with the game's name helps.

## First run

1. In game mode, open **Heroic Games Launcher** from your library. Heroic works with the
   controller; the touch screen works too.
2. Choose **Log in** in the sidebar and sign in to the stores you use (Epic, GOG, Amazon). You
   can be signed in to all three at once.
3. Your games appear in Heroic's library. Pick one and press **Install**.

To install games to a microSD card, set the install folder in Heroic's **Settings → General**
first.

## Windows games

Most Epic and GOG games are Windows games. Heroic runs them through Proton, the same way Steam
does, and on an ARM handheld it needs an ARM build of Proton:

1. In Heroic, open **Wine Manager** (left side) and pick the **Proton-CachyOS** tab.
2. Install the newest version. On this handheld Heroic only lists the ARM builds, so any of them is
   the right kind.
3. In **Settings → Game Defaults**, set **Wine Version** to the Proton-CachyOS you installed.

Heroic also lists the Proton builds Steam already has, so those work too.

## Adding a Heroic game to Steam

On a game's page in Heroic, open the **⋮** menu and pick **Add to Steam**. After you go back to
game mode the game has its own tile in your Steam library, and Steamling Control's per-game
settings work for it like any non-Steam game.

## When a game won't start

- **Try another Proton version.** Install a second one in Wine Manager and switch the game to it
  in its own settings.
- **Turn off umu.** In the game's settings, tick **Disable umu** and try again.
- **Check the log.** The game's settings have a **Log** tab. Include it in a bug report.
