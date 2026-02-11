#!/usr/bin/env bash
set -euo pipefail

IMAGE_TAG="${IMAGE_TAG:-allure-integration-tests:local}"
ARTIFACTS_DIR="${ARTIFACTS_DIR:-./integration_tests/artifacts}"
RUN_PLAYWRIGHT_VALIDATION="${RUN_PLAYWRIGHT_VALIDATION:-1}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${SCRIPT_DIR}"

if [[ "${ARTIFACTS_DIR}" = /* ]]; then
  ARTIFACTS_PATH="${ARTIFACTS_DIR}"
else
  ARTIFACTS_PATH="${SCRIPT_DIR}/${ARTIFACTS_DIR#./}"
fi

mkdir -p "${ARTIFACTS_PATH}"
rm -rf "${ARTIFACTS_PATH:?}/"*

docker build -f integration_tests/Dockerfile -t "${IMAGE_TAG}" .
docker run --rm \
  -e SINGLE_DIR=/artifacts \
  -v "${ARTIFACTS_PATH}:/artifacts" \
  "${IMAGE_TAG}"

if [[ "${RUN_PLAYWRIGHT_VALIDATION}" == "1" ]]; then
  mapfile -t HTML_FILES < <(find "${ARTIFACTS_PATH}" -name 'complete.html' -type f | sort)
  if [[ "${#HTML_FILES[@]}" -eq 0 ]]; then
    echo "No complete.html files found under ${ARTIFACTS_PATH}" >&2
    exit 1
  fi

  echo "Running Playwright validation for ${#HTML_FILES[@]} HTML file(s)."
  for html_file in "${HTML_FILES[@]}"; do
    "${SCRIPT_DIR}/validate_html_with_playwright.sh" "${html_file}"
  done
fi
