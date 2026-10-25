#!/bin/sh
# Puts back the stock bootloader that backup_abl.sh saved (abl_a.img and abl_b.img, next to this
# script). Run it as root from Android.

kit=$(dirname "$0")
for d in "$kit" /sdcard/openabl /sdcard/rocknix_abl; do
  [ -s "$d/abl_a.img" ] && { kit=$d; break; }
done

for slot in a b; do
  [ -s "$kit/abl_$slot.img" ] || { echo "No abl_$slot.img in $kit. Nothing was written."; exit 1; }
done
for slot in a b; do
  dd if="$kit/abl_$slot.img" of="/dev/block/by-name/abl_$slot" bs=1M \
    || { echo "Restoring abl_$slot FAILED. Don't power off; run this again, or ask for help."; exit 1; }
done
sync
echo "Stock bootloader restored. The handheld boots Android again on its next start."
