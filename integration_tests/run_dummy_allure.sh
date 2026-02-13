#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="/workspace/integration_tests"
RESULTS_DIR="/tmp/allure-results"
REPORT_DIR="/tmp/allure-report"
SINGLE_DIR="${SINGLE_DIR:-/tmp/allure-single}"
VARIANTS_DIR="${SINGLE_DIR}/variants"
TMP_VARIANTS="/tmp/allure-variant-sources"

rm -rf "${RESULTS_DIR}" "${REPORT_DIR}" "${TMP_VARIANTS}"
mkdir -p "${RESULTS_DIR}" "${SINGLE_DIR}"
rm -rf "${SINGLE_DIR:?}/"*
mkdir -p "${VARIANTS_DIR}" "${TMP_VARIANTS}"

pytest -q "${ROOT_DIR}/dummy_tests" --alluredir "${RESULTS_DIR}"
allure generate "${RESULTS_DIR}" --clean -o "${REPORT_DIR}"
allure-combine "${REPORT_DIR}" --dest "${SINGLE_DIR}" --auto-create-folders

test -f "${SINGLE_DIR}/complete.html"

printf 'Single-file report created: %s\n' "${SINGLE_DIR}/complete.html"
ls -lah "${SINGLE_DIR}/complete.html"

copy_source_report() {
  local name="$1"
  local destination="${TMP_VARIANTS}/${name}"
  rm -rf "${destination}"
  cp -a "${REPORT_DIR}" "${destination}"
  echo "${destination}"
}

# default args (output in source dir)
default_src="$(copy_source_report default)"
allure-combine "${default_src}"
mkdir -p "${VARIANTS_DIR}/default"
cp "${default_src}/complete.html" "${VARIANTS_DIR}/default/complete.html"

# --dest to existing folder
dest_src="$(copy_source_report dest)"
mkdir -p "${VARIANTS_DIR}/dest-existing"
allure-combine "${dest_src}" --dest "${VARIANTS_DIR}/dest-existing"
test -f "${VARIANTS_DIR}/dest-existing/complete.html"

# --auto-create-folders for missing destination
auto_src="$(copy_source_report auto-create-folders)"
allure-combine "${auto_src}" --dest "${VARIANTS_DIR}/auto-create/nested" --auto-create-folders
test -f "${VARIANTS_DIR}/auto-create/nested/complete.html"

# --remove-temp-files
remove_src="$(copy_source_report remove-temp-files)"
allure-combine "${remove_src}" --remove-temp-files
test -f "${remove_src}/complete.html"
test ! -f "${remove_src}/server.js"
test ! -f "${remove_src}/sinon-9.2.4.js"
mkdir -p "${VARIANTS_DIR}/remove-temp-files"
cp "${remove_src}/complete.html" "${VARIANTS_DIR}/remove-temp-files/complete.html"

# --ignore-utf8-errors
ignore_src="$(copy_source_report ignore-utf8-errors)"
mkdir -p "${ignore_src}/extra_data"
printf '\xff\xfe\xfd' > "${ignore_src}/extra_data/broken.json"
allure-combine "${ignore_src}" --ignore-utf8-errors
mkdir -p "${VARIANTS_DIR}/ignore-utf8-errors"
cp "${ignore_src}/complete.html" "${VARIANTS_DIR}/ignore-utf8-errors/complete.html"

# --disable-tags-escaping
disable_tags_src="$(copy_source_report disable-tags-escaping)"
allure-combine "${disable_tags_src}" --disable-tags-escaping
mkdir -p "${VARIANTS_DIR}/disable-tags-escaping"
cp "${disable_tags_src}/complete.html" "${VARIANTS_DIR}/disable-tags-escaping/complete.html"
test -f "${VARIANTS_DIR}/disable-tags-escaping/complete.html"

echo "Generated variant HTML reports:"
find "${VARIANTS_DIR}" -name 'complete.html' -type f | sort
