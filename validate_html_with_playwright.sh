#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <path-to-complete.html>" >&2
  exit 2
fi

PLAYWRIGHT_IMAGE="${PLAYWRIGHT_IMAGE:-mcr.microsoft.com/playwright:v1.56.1-noble}"
PLAYWRIGHT_VERSION="${PLAYWRIGHT_VERSION:-1.56.1}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

HTML_PATH_INPUT="$1"
if [[ "${HTML_PATH_INPUT}" != /* ]]; then
  HTML_PATH_INPUT="${PWD}/${HTML_PATH_INPUT}"
fi

HTML_PATH="$(realpath "${HTML_PATH_INPUT}")"
if [[ ! -f "${HTML_PATH}" ]]; then
  echo "HTML file not found: ${HTML_PATH}" >&2
  exit 2
fi

HTML_DIR="$(dirname "${HTML_PATH}")"
HTML_BASENAME="$(basename "${HTML_PATH}")"
SCREENSHOT_PATH_IN_CONTAINER="/artifacts/${HTML_BASENAME%.html}.playwright.png"

docker run --rm --init --ipc=host \
  -v "${SCRIPT_DIR}:/repo" \
  -v "${HTML_DIR}:/artifacts" \
  -w /tmp \
  "${PLAYWRIGHT_IMAGE}" \
  bash -lc "set -euo pipefail \
    && rm -rf /tmp/playwright-validate \
    && mkdir -p /tmp/playwright-validate \
    && cd /tmp/playwright-validate \
    && PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1 npm init -y >/dev/null 2>&1 \
    && PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1 npm install --no-fund --no-audit @playwright/test@${PLAYWRIGHT_VERSION} >/dev/null \
    && cp /repo/integration_tests/playwright_html.spec.js /tmp/playwright-validate/playwright_html.spec.js \
    && TARGET_HTML=/artifacts/${HTML_BASENAME} SCREENSHOT_PATH=${SCREENSHOT_PATH_IN_CONTAINER} /tmp/playwright-validate/node_modules/.bin/playwright test /tmp/playwright-validate/playwright_html.spec.js --reporter=line --workers=1 --output=/tmp/playwright-test-results"

echo "Playwright validation completed for ${HTML_PATH}"
echo "Screenshot: ${HTML_DIR}/${HTML_BASENAME%.html}.playwright.png"
