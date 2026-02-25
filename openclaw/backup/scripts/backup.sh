#!/usr/bin/env bash
# OpenClaw backup script — creates timestamped tar.gz of openclaw environments
set -euo pipefail

BACKUP_DIR="${1:-${HOME}}"
ACTION="${2:-backup}"
ENV_FILTER="${3:-all}"  # personal, work, or all

TIMESTAMP="$(date +%Y-%m-%d-%H%M)"

# Build list of environments to process
declare -a ENVS=()
case "${ENV_FILTER}" in
  personal) ENVS=("personal") ;;
  work)     ENVS=("work") ;;
  all)      ENVS=("personal" "work") ;;
  *)
    echo "ERROR: Unknown environment '${ENV_FILTER}'. Use: personal, work, or all" >&2
    exit 1
    ;;
esac

case "${ACTION}" in
  backup)
    for env in "${ENVS[@]}"; do
      SRC_DIR="${HOME}/.openclaw-${env}"
      BACKUP_FILE="${BACKUP_DIR}/openclaw-${env}-backup-${TIMESTAMP}.tar.gz"
      if [ ! -d "${SRC_DIR}" ]; then
        echo "SKIP: ${SRC_DIR} does not exist"
        continue
      fi
      tar -czf "${BACKUP_FILE}" -C "${HOME}" ".openclaw-${env}"
      SIZE=$(du -h "${BACKUP_FILE}" | cut -f1)
      echo "Backup created: ${BACKUP_FILE} (${SIZE})"
    done
    ;;
  list)
    for env in "${ENVS[@]}"; do
      echo "=== ${env} backups in ${BACKUP_DIR} ==="
      ls -lh "${BACKUP_DIR}"/openclaw-${env}-backup-*.tar.gz 2>/dev/null || echo "  (none)"
    done
    ;;
  clean)
    KEEP="${4:-5}"
    for env in "${ENVS[@]}"; do
      echo "=== ${env} ==="
      TOTAL=$(ls -1 "${BACKUP_DIR}"/openclaw-${env}-backup-*.tar.gz 2>/dev/null | wc -l | tr -d ' ')
      if [ "${TOTAL}" -le "${KEEP}" ]; then
        echo "Only ${TOTAL} backup(s) found, keeping all (threshold: ${KEEP})"
        continue
      fi
      TO_DELETE=$((TOTAL - KEEP))
      echo "Removing ${TO_DELETE} oldest backup(s), keeping newest ${KEEP}:"
      ls -1t "${BACKUP_DIR}"/openclaw-${env}-backup-*.tar.gz | tail -n "${TO_DELETE}" | while read -r f; do
        echo "  Deleting: $(basename "${f}")"
        rm "${f}"
      done
    done
    ;;
  upload)
    REMOTE="${4:-gdrive}"
    REMOTE_PATH="${5:-backups/openclaw}"
    for env in "${ENVS[@]}"; do
      LATEST=$(ls -1t "${BACKUP_DIR}"/openclaw-${env}-backup-*.tar.gz 2>/dev/null | head -1)
      if [ -z "${LATEST}" ]; then
        echo "SKIP: No ${env} backup files found in ${BACKUP_DIR}"
        continue
      fi
      echo "Uploading $(basename "${LATEST}") to ${REMOTE}:${REMOTE_PATH}/"
      rclone copy "${LATEST}" "${REMOTE}:${REMOTE_PATH}/" --progress
      echo "Upload complete: ${env}"
    done
    ;;
  *)
    echo "Usage: backup.sh [backup_dir] [backup|list|clean|upload] [personal|work|all] [keep_n|remote] [remote_path]"
    exit 1
    ;;
esac
