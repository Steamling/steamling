import { PanelSection } from "@decky/ui";
import { useEffect, useState } from "react";
import { t } from "../i18n";
import { applyToSteamWindow, getMenuWidth, onMenuWidth, panelCss, setMenuWidth } from "../lib/menuWidth";
import type { MenuWidth as Width } from "../lib/menuWidth";
import { SelectEdit } from "./widgets";

/** Mounted once by Content, which stays rendered for the whole session. The panel rules render
 * here, in the menu's window; the placeholder rule goes into Steam's main window. */
export function MenuWidthStyle() {
  const [width, setWidth] = useState<Width>(getMenuWidth);
  useEffect(() => onMenuWidth(setWidth), []);
  useEffect(() => applyToSteamWindow(width), [width]);
  const css = panelCss(width);
  return css ? <style>{css}</style> : null;
}

export function MenuWidthSetting() {
  const [width, setWidth] = useState<Width>(getMenuWidth);
  useEffect(() => onMenuWidth(setWidth), []);
  const options = [
    { data: "standard", label: t("Standard (Steam's own)") },
    { data: "wide", label: t("Wide") },
    { data: "wider", label: t("Wider") },
  ];
  return (
    <PanelSection title={t("QUICK ACCESS MENU")}>
      <SelectEdit label={t("Width")} value={width} options={options} onChange={(value) => setMenuWidth(value as Width)} />
      <div className="steamling-note">{t("Widens this menu for every page in it, so text wraps less.")}</div>
    </PanelSection>
  );
}
