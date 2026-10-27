import { ButtonItem, Field, PanelSection, PanelSectionRow } from "@decky/ui";
import { setCompatTool } from "../lib/compat";
import { t } from "../i18n";
import type { Config, GameSuggestion } from "../types";
import { audioLatencyOptions, fanOptions, hw, lavdOptions } from "./GameFields";

// A suggestion made on another handheld can name a fan or scheduler this one doesn't have.
function usable(config: Config, settings: Record<string, any>): Record<string, any> {
  const has = hw(config);
  const out = { ...settings };
  if (!has.fan) delete out.fanMode;
  if (!has.scheduler) delete out.lavdMode;
  if (!has.touchscreen) delete out.touchDisabled;
  if (!(config.mesaVersions || []).some((v) => v.data === out.mesaVersion)) delete out.mesaVersion;
  return out;
}

function describe(config: Config, suggestion: GameSuggestion): string[] {
  const lines: string[] = [];
  const s = usable(config, suggestion.settings);
  const pick = (options: { data: string; label: string }[], value: any) =>
    options.find((o) => o.data === String(value))?.label || String(value);
  if (suggestion.proton) lines.push(t("Proton: {tool}", { tool: suggestion.proton }));
  if (s.fexProfile) lines.push(t("FEX Preset: {value}", { value: config.fexProfiles?.[s.fexProfile]?.label || s.fexProfile }));
  if (s.audioLatency !== undefined) lines.push(t("Audio Buffer: {value}", { value: pick(audioLatencyOptions, s.audioLatency) }));
  if (s.mesaVersion) lines.push(t("Mesa Version: {value}", { value: s.mesaVersion }));
  if (s.fanMode) lines.push(t("Fan Curve: {value}", { value: pick(fanOptions, s.fanMode) }));
  if (s.lavdMode) lines.push(t("CPU Scheduler: {value}", { value: pick(lavdOptions, s.lavdMode) }));
  if (s.gamepadType) lines.push(t("Controller Type: {value}", { value: s.gamepadType }));
  if (s.disableXalia !== undefined) lines.push(s.disableXalia ? t("Xalia off") : t("Xalia on"));
  if (s.touchDisabled) lines.push(t("Touchscreen off while playing"));
  if (s.envVars) lines.push(t("Environment: {value}", { value: s.envVars }));
  return lines;
}

/** One-tap known-good settings for the selected game, when the list has an entry for it. */
export function Suggestion({ config, appid, apply }: {
  config: Config;
  appid: string;
  apply: (settings: Record<string, any>) => void;
}) {
  const suggestion = config.suggestions?.[appid];
  if (!suggestion) return null;
  const lines = describe(config, suggestion);
  return (
    <PanelSection title={t("SUGGESTED SETTINGS")}>
      {suggestion.note ? <div className="steamling-note">{suggestion.note}</div> : null}
      <Field label={t("Would set")} description={lines.join(" · ")} />
      {suggestion.tested ? <div className="steamling-note">{t("Tested on {where}", { where: suggestion.tested })}</div> : null}
      <PanelSectionRow>
        <ButtonItem
          layout="below"
          description={t("Turns on per-game settings for this game and fills them in. You can still change anything afterwards.")}
          onClick={() => {
            apply(usable(config, suggestion.settings));
            if (suggestion.proton) setCompatTool(appid, suggestion.proton);
          }}
        >
          {t("Use Suggested Settings")}
        </ButtonItem>
      </PanelSectionRow>
    </PanelSection>
  );
}
