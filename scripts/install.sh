#!/usr/bin/env bash
# install.sh — pointer to the ON-DEVICE internal installer.
#
# Installing to internal storage repartitions the device's internal UFS and clones the
# *running* system onto it, so it cannot run on the build host. It ships in the rootfs
# (via steamling-tools) as /usr/bin/steamling-install-internal — see its header for details.

source "$(dirname "$0")/lib.sh"
die "Run the installer ON THE DEVICE, not the build host:
    steamling-install-internal --dry-run     # review the plan
    steamling-install-internal               # install
See packages/shared/steamling-tools/steamling-install-internal."
