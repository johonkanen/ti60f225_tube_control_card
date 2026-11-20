#!/usr/bin/env bash
# ERC of the project schematic (full report: reports/erc.rpt), judged by tools/erc_check.py:
# fails on ERC errors, on the fatal warning type no_connect_connected (decision D2) and on stale
# entries of tools/erc_pending.txt (errors expected until a later sheet is drawn).
#   tools/erc.sh [schematic.kicad_sch [report.rpt]]   (arguments only for tests on a scratch copy)
set -u
cd "$(dirname "$0")/.."
sch=${1:-kicad/tube_control_card.kicad_sch}
rpt=${2:-reports/erc.rpt}
mkdir -p "$(dirname "$rpt")"
tools/p2k/bin/kicad-cli sch erc --severity-all -o "$rpt" "$sch" >/dev/null || exit 1
if [ $# -eq 0 ]; then python3 tools/erc_check.py "$rpt"; else python3 tools/erc_check.py --no-pending "$rpt"; fi
