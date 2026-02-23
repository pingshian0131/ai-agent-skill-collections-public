#!/usr/bin/env bash
# OpenClaw backup script — creates timestamped tar.gz of {baseDir}
set -euo pipefail

# TODO: Replace {baseDir} with your actual OpenClaw directory (e.g. ~/.openclaw-personal)
OPENCLAW_DIR="{baseDir}"
OPENCLAW_DIRNAME="$(basename "${OPENCLAW_DIR}")"
BACKUP_DIR="${1:-${HOME}}"
TIMESTAMP="$(date +%Y-%m-%d-%H%M)"
BACKUP_FILE="${BACKUP_DIR}/${OPENCLAW_DIRNAME}-backup-${TIMESTAMP}.tar.gz"

if [ ! -d "${OPENCLAW_DIR}" ]; then
  echo "ERROR: ${OPENCLAW_DIR} does not exist" >&2
  exit 1
fi

case "${2:-backup}" in
  backup)
    tar -czf "${BACKUP_FILE}" -C "${HOME}" "${OPENCLAW_DIRNAME}"
    SIZE=$(du -h "${BACKUP_FILE}" | cut -f1)
    echo "Backup created: ${BACKUP_FILE} (${SIZE})"
    ;;
  list)
    echo "Existing backups in ${BACKUP_DIR}:"
    ls -lh "${BACKUP_DIR}"/${OPENCLAW_DIRNAME}-backup-*.tar.gz 2>/dev/null || echo "  (none)"
    ;;
  clean)
    KEEP="${3:-5}"
    TOTAL=$(ls -1 "${BACKUP_DIR}"/${OPENCLAW_DIRNAME}-backup-*.tar.gz 2>/dev/null | wc -l | tr -d ' ')
    if [ "${TOTAL}" -le "${KEEP}" ]; then
      echo "Only ${TOTAL} backup(s) found, keeping all (threshold: ${KEEP})"
      exit 0
    fi
    TO_DELETE=$((TOTAL - KEEP))
    echo "Removing ${TO_DELETE} oldest backup(s), keeping newest ${KEEP}:"
    ls -1t "${BACKUP_DIR}"/${OPENCLAW_DIRNAME}-backup-*.tar.gz | tail -n "${TO_DELETE}" | while read -r f; do
      echo "  Deleting: $(basename "${f}")"
      rm "${f}"
    done
    ;;
  upload)
    REMOTE="${3:-gdrive}"
    REMOTE_PATH="${4:-backups/openclaw}"
    LATEST=$(ls -1t "${BACKUP_DIR}"/${OPENCLAW_DIRNAME}-backup-*.tar.gz 2>/dev/null | head -1)
    if [ -z "${LATEST}" ]; then
      echo "ERROR: No backup files found in ${BACKUP_DIR}" >&2
      exit 1
    fi
    echo "Uploading $(basename "${LATEST}") to ${REMOTE}:${REMOTE_PATH}/"
    rclone copy "${LATEST}" "${REMOTE}:${REMOTE_PATH}/" --progress
    echo "Upload complete."
    ;;
  *)
    echo "Usage: backup.sh [backup_dir] [backup|list|clean|upload] [remote] [remote_path]"
    exit 1
    ;;
esac
