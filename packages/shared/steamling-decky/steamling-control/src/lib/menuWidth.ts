import { quickAccessMenuClasses } from "@decky/ui";

// Steam draws the quick access menu 348px wide: a 48px tab strip plus a 300px page. Its
// placeholder is 854px wide and shifted right by 506px, so making the placeholder wider (it is
// anchored to the right edge) shows more of it without touching the slide-in transform. The
// friends list's expanded view resizes itself and is left alone.
export const WIDTHS = { standard: 0, wide: 100, wider: 200 } as const;
export type MenuWidth = keyof typeof WIDTHS;

const KEY = "steamling-control.menu-width";
const DEFAULT: MenuWidth = "wide";
const listeners = new Set<(width: MenuWidth) => void>();

export function getMenuWidth(): MenuWidth {
  try {
    const saved = window.localStorage.getItem(KEY);
    if (saved && saved in WIDTHS) return saved as MenuWidth;
  } catch (error) {
  }
  return DEFAULT;
}

export function setMenuWidth(width: MenuWidth) {
  try {
    window.localStorage.setItem(KEY, width);
  } catch (error) {
  }
  for (const listener of listeners) listener(width);
}

export function onMenuWidth(listener: (width: MenuWidth) => void): () => void {
  listeners.add(listener);
  return () => listeners.delete(listener);
}

export function menuWidthCss(width: MenuWidth): string {
  const extra = WIDTHS[width];
  const c = quickAccessMenuClasses as Record<string, string | undefined>;
  const cls = (key: string) => (c?.[key] ? `.${c[key]!.split(" ")[0]}` : "");
  const placeholder = cls("ViewPlaceholder");
  if (!extra || !placeholder) return "";
  const expanded = cls("Expanded");
  const open = expanded ? `${placeholder}:not(${expanded})` : placeholder;
  const rules = [`${open} { width: ${854 + extra}px !important; }`];
  if (cls("TabGroupPanel")) rules.push(`${open} ${cls("TabGroupPanel")}:not(.tab_Friends) { max-width: ${300 + extra}px !important; }`);
  if (cls("HeaderContainer")) rules.push(`${open} ${cls("HeaderContainer")} { max-width: ${348 + extra}px !important; }`);
  if (cls("Footer")) rules.push(`${open} ${cls("Footer")} { width: ${348 + extra}px !important; }`);
  return rules.join("\n");
}
