#!/usr/bin/env bash
#
# download_data.sh
#
# Downloads the IEEE-CIS Fraud Detection dataset from Kaggle via the Kaggle
# API and places the raw CSVs into data/raw/.
#
# First-time setup (only needs to be done once per machine):
#   1. Create a Kaggle account if you don't have one: https://www.kaggle.com
#   2. Go to https://www.kaggle.com/settings/api -> "API Tokens" section ->
#      click "Generate New Token".
#   3. Put the API Token in an .env file in the project root.
#   4. Join the competition on the Kaggle website (required even though it's
#      free) by visiting the competition page and clicking "Join Competition" /
#      accepting the rules:
#         https://www.kaggle.com/c/ieee-fraud-detection/rules
#      The API download will fail with a 403 until you've done this.
#   5. Install the Kaggle CLI if not already installed.
#   6. Make the script executable: chmod +x download_data.sh
#
# Usage:
#   chmod +x download_data.sh
#   ./download_data.sh
#
# Idempotent: if the CSVs already exist in data/raw/, the script skips the
# download unless --force is passed.

set -euo pipefail

# --- Configuration -----------------------------------------------------

COMPETITION="ieee-fraud-detection"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="${SCRIPT_DIR}"
RAW_DIR="${PROJECT_ROOT}/data/raw"
ZIP_PATH="${RAW_DIR}/${COMPETITION}.zip"
SAMPLE_SUBMISSION_PATH="${RAW_DIR}/sample_submission.csv"

EXPECTED_FILES=(
  "train_transaction.csv"
  "train_identity.csv"
  "test_transaction.csv"
  "test_identity.csv"
)

FORCE=0
if [[ "${1:-}" == "--force" ]]; then
  FORCE=1
fi

# --- Helpers -------------------------------------------------------------

log()  { echo -e "[download_data] $*"; }
fail() { echo -e "[download_data] ERROR: $*" >&2; exit 1; }

check_kaggle_cli() {
  if ! command -v kaggle >/dev/null 2>&1; then
    fail "kaggle CLI not found. Install it with:
    pip install kaggle --break-system-packages
  See the header of this script for full setup steps."
  fi
}

load_dotenv() {
  local env_file="${PROJECT_ROOT}/.env"
  if [[ -f "${env_file}" ]]; then
    log "Loading environment variables from ${env_file}..."
    while IFS= read -r line || [[ -n "$line" ]]; do
      # Skip comments and empty lines
      if [[ ! "$line" =~ ^[[:space:]]*# ]] && [[ "$line" =~ = ]]; then
        local key="${line%%=*}"
        local val="${line#*=}"
        # Strip surrounding quotes
        val="${val#\"}"
        val="${val%\"}"
        val="${val#\'}"
        val="${val%\'}"
        export "${key}=${val}"
      fi
    done < "${env_file}"
  fi
}

check_kaggle_credentials() {
  if [[ -n "${KAGGLE_API_TOKEN:-}" ]]; then
    log "Kaggle credentials found in environment variables."
    return 0
  fi

  fail "Kaggle credentials not found.
  Please define either KAGGLE_API_TOKEN in ${PROJECT_ROOT}/.env."
}

all_files_present() {
  local f
  for f in "${EXPECTED_FILES[@]}"; do
    [[ -f "${RAW_DIR}/${f}" ]] || return 1
  done
  return 0
}

# --- Main ------------------------------------------------------------

main() {
  load_dotenv
  mkdir -p "${RAW_DIR}"

  if [[ "${FORCE}" -eq 0 ]] && all_files_present; then
    log "All expected CSVs already present in ${RAW_DIR} — skipping download."
    log "(re-run with --force to re-download)"
    exit 0
  fi

  check_kaggle_cli
  check_kaggle_credentials

  log "Downloading '${COMPETITION}' competition data from Kaggle..."
  log "(If this fails with a 403, make sure you've joined the competition"
  log " at https://www.kaggle.com/c/${COMPETITION}/rules)"

  kaggle competitions download \
    -c "${COMPETITION}" \
    -p "${RAW_DIR}"

  if [[ ! -f "${ZIP_PATH}" ]]; then
    fail "Expected zip not found at ${ZIP_PATH} after download. Kaggle CLI output above may explain why."
  fi

  log "Unzipping..."
  unzip -o "${ZIP_PATH}" -d "${RAW_DIR}" > /dev/null

  log "Cleaning up zip file..."
  rm -f "${ZIP_PATH}"

  log "Cleaning up sample_submission.csv file..."
  rm -f "${SAMPLE_SUBMISSION_PATH}"

  if ! all_files_present; then
    fail "Download/unzip completed but some expected files are missing from ${RAW_DIR}.
  Expected: ${EXPECTED_FILES[*]}
  Found:    $(ls "${RAW_DIR}")"
  fi

  log "Done. Files in ${RAW_DIR}:"
  for f in "${EXPECTED_FILES[@]}"; do
    local size
    size=$(du -h "${RAW_DIR}/${f}" | cut -f1)
    log "  ${f} (${size})"
  done
}

main "$@"
