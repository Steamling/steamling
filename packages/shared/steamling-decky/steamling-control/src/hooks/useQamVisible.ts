import { createContext, useContext } from "react";

// The panel is alwaysRender: it stays mounted while the menu is closed and a game runs, so
// anything that polls asks this first. Content provides it from @decky/api's
// useQuickAccessVisible; outside the panel (library modals) the default is visible.
export const QamVisible = createContext(true);

export const useQamVisible = () => useContext(QamVisible);
