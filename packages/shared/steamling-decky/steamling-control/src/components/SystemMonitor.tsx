import { Field, PanelSection, PanelSectionRow, ToggleField } from "@decky/ui";
import { useEffect, useState } from "react";
import { systemStats } from "../backend";
import { useQamVisible } from "../hooks/useQamVisible";
import { t } from "../i18n";
import type { SystemStats } from "../types";

const REFRESH_MS = 2000;
const SHOW_KEY = "steamling-control.monitor";

function remembered(): boolean {
  try {
    return window.localStorage.getItem(SHOW_KEY) === "1";
  } catch (error) {
    return false;
  }
}

function remember(on: boolean) {
  try {
    window.localStorage.setItem(SHOW_KEY, on ? "1" : "0");
  } catch (error) {
  }
}

const dash = "–";

function cpuText(stats: SystemStats): string {
  const clocks = stats.cpu.clusters.map((c) => `${(c.mhz / 1000).toFixed(1)}`).join(" / ");
  const load = stats.cpu.load === null ? dash : `${stats.cpu.load}%`;
  return t("{load} busy · {clocks} GHz", { load, clocks: clocks || dash });
}

function tempText(stats: SystemStats): string {
  const parts: string[] = [];
  if (stats.temps.cpu !== undefined) parts.push(t("CPU {n}°C", { n: stats.temps.cpu }));
  if (stats.temps.gpu !== undefined) parts.push(t("GPU {n}°C", { n: stats.temps.gpu }));
  if (stats.battery?.tempC != null) parts.push(t("Battery {n}°C", { n: stats.battery.tempC }));
  return parts.join(" · ") || dash;
}

function batteryText(stats: SystemStats): string {
  const b = stats.battery;
  if (!b) return dash;
  const pct = b.percent === null ? dash : `${b.percent}%`;
  if (b.watts === null) return pct;
  const flow = b.status === "Charging" ? t("charging at {w} W", { w: b.watts }) : t("drawing {w} W", { w: b.watts });
  return `${pct} · ${flow}`;
}

export function SystemMonitor() {
  const [show, setShow] = useState(remembered);
  const [stats, setStats] = useState<SystemStats | null>(null);
  const visible = useQamVisible();

  // Only while it is switched on and the menu is open: nothing reads these numbers otherwise.
  useEffect(() => {
    if (!show || !visible) return;
    let cancelled = false;
    const tick = () =>
      systemStats()
        .then((next) => {
          if (!cancelled) setStats(next);
        })
        .catch(() => {});
    tick();
    const timer = window.setInterval(tick, REFRESH_MS);
    return () => {
      cancelled = true;
      window.clearInterval(timer);
    };
  }, [show, visible]);

  return (
    <PanelSection title={t("SYSTEM MONITOR")}>
      <PanelSectionRow>
        <ToggleField
          label={t("Show live readings")}
          description={t("Updates every 2 seconds while this menu is open")}
          checked={show}
          onChange={(on: boolean) => {
            setShow(on);
            remember(on);
          }}
        />
      </PanelSectionRow>
      {show && stats ? (
        <>
          <Field label={t("CPU")} description={cpuText(stats)} />
          <Field
            label={t("GPU")}
            description={stats.gpu ? t("{mhz} of {max} MHz", { mhz: stats.gpu.mhz, max: stats.gpu.maxMhz }) : dash}
          />
          <Field label={t("Temperature")} description={tempText(stats)} />
          <Field label={t("Battery")} description={batteryText(stats)} />
          <Field
            label={t("Memory")}
            description={
              stats.memory
                ? t("{used} of {total} GB", {
                    used: (stats.memory.usedMb / 1024).toFixed(1),
                    total: (stats.memory.totalMb / 1024).toFixed(1),
                  })
                : dash
            }
          />
          {stats.fan ? (
            <Field
              label={t("Fan")}
              description={
                stats.fan.rpm !== null ? t("{rpm} RPM", { rpm: stats.fan.rpm }) : t("{n}% speed", { n: stats.fan.percent ?? 0 })
              }
            />
          ) : null}
        </>
      ) : null}
    </PanelSection>
  );
}
