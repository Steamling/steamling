import { PanelSection } from "@decky/ui";
import { useEffect, useState } from "react";
import { t } from "../i18n";
import { getMenuWidth, menuWidthCss, onMenuWidth, setMenuWidth } from "../lib/menuWidth";
import type { MenuWidth as Width } from "../lib/menuWidth";
import { SelectEdit } from "./widgets";

/** The stylesheet itself: mounted once by Content, which stays rendered for the whole session. */
export function MenuWidthStyle() {
  const [width, setWidth] = useState<Width>(getMenuWidth);
  useEffect(() => onMenuWidth(setWidth), []);
  const css = menuWidthCss(width);
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
