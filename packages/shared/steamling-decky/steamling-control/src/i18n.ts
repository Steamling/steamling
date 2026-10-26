import { catalogs } from "./locales";

// Strings are written in English in the code and looked up by that English text, so code stays
// readable and an untranslated string simply shows in English. {name} placeholders are filled
// from `vars`. See locales/README.md for adding a language.
type Vars = Record<string, string | number>;

function language(): string {
  try {
    const steam = (window as any).LocalizationManager?.m_rgLocalesToUse?.[0];
    const raw = String(steam || navigator.language || "en").toLowerCase();
    return raw.split(/[-_]/)[0];
  } catch (error) {
    return "en";
  }
}

let cached: Record<string, string> | null | undefined;

function catalog(): Record<string, string> | null {
  if (cached === undefined) cached = catalogs[language()] || null;
  return cached;
}

export function t(text: string, vars?: Vars): string {
  let out = catalog()?.[text] ?? text;
  if (vars) {
    for (const [key, value] of Object.entries(vars)) out = out.split(`{${key}}`).join(String(value));
  }
  return out;
}
