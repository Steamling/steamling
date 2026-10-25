import { ButtonItem, ConfirmModal, Field, PanelSection, PanelSectionRow, showModal } from "@decky/ui";
import { useEffect, useState } from "react";
import { deviceInfo, restartGameMode } from "../backend";
import { useQamVisible } from "../hooks/useQamVisible";
import type { DeviceInfo } from "../types";

export function About() {
  const [info, setInfo] = useState<DeviceInfo | null>(null);
  const [error, setError] = useState("");
  const visible = useQamVisible();

  // Once per open: the bootloader check reads both ABL slots, so it is not polled.
  useEffect(() => {
    if (!visible) return;
    let cancelled = false;
    deviceInfo()
      .then((next) => {
        if (!cancelled) setInfo(next);
      })
      .catch((err) => {
        if (!cancelled) setError(String(err));
      });
    return () => {
      cancelled = true;
    };
  }, [visible]);

  const confirmRestart = () =>
    showModal(
      <ConfirmModal
        strTitle="Restart Game Mode"
        strDescription="Closes Steam and any running game, then brings game mode back up. Unsaved progress in a running game is lost. Useful when Steam or the screen gets stuck."
        strOKButtonText="Restart"
        onOK={() => restartGameMode().catch((err) => setError(String(err)))}
      />
    );

  return (
    <PanelSection title="ABOUT">
      <Field label="Steamling OS" description={info?.osVersion ?? "…"} />
      <Field label="Kernel" description={info?.kernel ?? "…"} />
      {info?.bootloader ? <Field label="Bootloader" description={info.bootloader} /> : null}
      <PanelSectionRow>
        <ButtonItem layout="below" onClick={confirmRestart}>Restart Game Mode</ButtonItem>
      </PanelSectionRow>
      {error ? <Field label="Error" description={error} /> : null}
    </PanelSection>
  );
}
