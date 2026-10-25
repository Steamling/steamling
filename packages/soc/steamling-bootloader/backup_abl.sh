#!/bin/sh
# Saves the stock bootloader next to this script as abl_a.img and abl_b.img. Run it as root from
# Android BEFORE flash_abl.sh: those two files are your only way back to the factory bootloader.
# A backup that's already here is kept, so running this again after flashing can't replace the
# stock copy with OpenABL.

kit=$(dirname "$0")
for d in "$kit" /sdcard/openabl /sdcard/rocknix_abl; do
  [ -f "$d/flash_abl.sh" ] && { kit=$d; break; }
done

for slot in a b; do
  if [ -s "$kit/abl_$slot.img" ]; then
    echo "abl_$slot.img is already saved here, keeping it"
    continue
  fi
  dd if="/dev/block/by-name/abl_$slot" of="$kit/abl_$slot.img" bs=1M \
    || { echo "Backing up abl_$slot FAILED. Don't run flash_abl.sh until this works."; exit 1; }
done
sync
echo "Stock bootloader saved to $kit (abl_a.img, abl_b.img). Copy both to your PC now."
