import { AddGameSection } from "../components/AddGame";
import { FileSharing } from "../components/FileSharing";
import { RemoteAccess } from "../components/RemoteAccess";
import { SdCard } from "../components/SdCard";
import { UsbTransfer } from "../components/UsbTransfer";

// SD card last: the only destructive action, kept away from the casual toggles
export function Library() {
  return (
    <>
      <AddGameSection />
      <FileSharing />
      <UsbTransfer />
      <RemoteAccess />
      <SdCard />
    </>
  );
}
