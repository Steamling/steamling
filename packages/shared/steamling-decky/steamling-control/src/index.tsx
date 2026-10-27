import { definePlugin } from "@decky/api";
import { Content } from "./Content";
import { getConfig } from "./backend";
import { installedSteamGames, isGame, nonSteamShortcuts } from "./lib/games";
import { registerDownloadWrapper, wrapAllGames, wrapShortcuts } from "./lib/launchOptions";
import { patchLibraryContextMenu } from "./lib/contextMenu";
import { registerTouchLifetime } from "./lib/touch";
import { applyToSteamWindow, getMenuWidth } from "./lib/menuWidth";

export default definePlugin(() => {
  const unpatchContextMenu = patchLibraryContextMenu();
  const unregisterTouch = registerTouchLifetime();
  const unregisterDownloads = registerDownloadWrapper((appid) => isGame(appid));
  // Wider from the first time the menu opens, not only once this plugin's page has been shown.
  applyToSteamWindow(getMenuWidth());
  getConfig()
    .then((config) => wrapAllGames(installedSteamGames(config)))
    .then(() => wrapShortcuts(nonSteamShortcuts().map((shortcut) => shortcut.appid)))
    .catch(() => {});
  return {
    name: "Steamling Control",
    content: <Content />,
    icon: <div style={{ fontWeight: 700 }}>P</div>,
    alwaysRender: true,
    onDismount() {
      unpatchContextMenu();
      unregisterTouch();
      unregisterDownloads();
      applyToSteamWindow(null);
    },
  };
});
