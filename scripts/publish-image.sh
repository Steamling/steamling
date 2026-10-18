#!/usr/bin/env bash
# publish-image.sh — compress, checksum, and upload the SD image for public download.
#
# The pacman repo ships updates (publish-repo.sh); the image is only for first
# installs, so publishing one is: zstd-compress it under a DATE-STAMPED name,
# write a sha256, and rclone the pair to the public bucket. Date-stamped because
# a public filename must never change bytes (CDN caches would mix chunks of two
# different disk images — a corrupted flash for the downloader).
#
# Config (config/steamling.conf or env):
#   STEAMLING_IMAGE_RCLONE_REMOTE  rclone destination, e.g. r2:steamling/images
#                                (optional: skip upload if empty)
#   STEAMLING_IMAGE_URL            public base URL for that destination, only used
#                                to print the final download link
#
# NB: build/ is root-owned after sudo builds; run with sudo -E if the compressed
# output can't be written next to the image.

source "$(dirname "$0")/lib.sh"

IMG="${IMAGE_DIR}/steamling-${SOC}-sd.img"
STAMP="$(date +%Y%m%d)"
OUT="${IMAGE_DIR}/steamling-${SOC}-${STAMP}-sd.img.zst"

[ -f "${IMG}" ] || die "no ${IMG} — run 'make sd-image' first"
need_tool zstd
need_tool sha256sum

if [ ! -f "${OUT}" ] || [ "${IMG}" -nt "${OUT}" ]; then
  log "compressing $(du -h "${IMG}" | cut -f1) image -> $(basename "${OUT}") (zstd -12, all cores)"
  zstd -T0 -12 --force "${IMG}" -o "${OUT}" || die "zstd failed (root-owned ${IMAGE_DIR}? use sudo -E)"
else
  log "$(basename "${OUT}") is up to date — skipping compression"
fi

log "writing sha256"
( cd "${IMAGE_DIR}" && sha256sum "$(basename "${OUT}")" > "${OUT}.sha256" )
ok "prepared: $(basename "${OUT}") ($(du -h "${OUT}" | cut -f1)) + .sha256"

if [ -n "${STEAMLING_IMAGE_RCLONE_REMOTE}" ]; then
  need_tool rclone
  log "uploading -> ${STEAMLING_IMAGE_RCLONE_REMOTE}"
  # image first, checksum last: a visible .sha256 implies the image is complete
  rclone copy --progress "${OUT}" "${STEAMLING_IMAGE_RCLONE_REMOTE}/"
  rclone copy "${OUT}.sha256" "${STEAMLING_IMAGE_RCLONE_REMOTE}/"
  ok "uploaded"
  if [ -n "${STEAMLING_IMAGE_URL}" ]; then
    log "download link: ${STEAMLING_IMAGE_URL}/$(basename "${OUT}")"
  fi
else
  warn "STEAMLING_IMAGE_RCLONE_REMOTE unset — nothing uploaded (artifacts left in ${IMAGE_DIR})"
fi
