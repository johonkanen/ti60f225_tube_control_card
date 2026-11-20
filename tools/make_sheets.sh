#!/usr/bin/env bash
# Rebuild every drawn schematic sheet from its script (tools/sheets/sheetNN.py).
#   tools/make_sheets.sh           rebuild kicad/NN_*.kicad_sch
#   tools/make_sheets.sh --check   rebuild and fail if a sheet file changed (the committed sheets
#                                  are what the scripts and the current library generate)
set -u
cd "$(dirname "$0")/.."
tmp=build/tmp/sheets_before
rm -rf "$tmp"; mkdir -p "$tmp"
cp kicad/[0-9][0-9]_*.kicad_sch "$tmp"/
n=0
for s in tools/sheets/sheet[0-9][0-9].py; do
    python3 "$s" >/dev/null || { echo "make_sheets: $s failed"; exit 1; }
    n=$((n + 1))
done
changed=0
for f in "$tmp"/*.kicad_sch; do
    cmp -s "$f" "kicad/$(basename "$f")" || { changed=$((changed + 1)); [ "${1:-}" = "--check" ] && echo "make_sheets: $(basename "$f") was not up to date"; }
done
if [ "${1:-}" = "--check" ]; then
    [ $changed -eq 0 ] && echo "make_sheets: $n sheet scripts, kicad/ up to date" || exit 1
else
    echo "make_sheets: $n sheet scripts run, $changed sheet files changed"
fi
