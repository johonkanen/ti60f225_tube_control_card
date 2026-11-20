#!/usr/bin/env bash
# ERC of the project schematic; fails on ERC errors and on the warning types in FATAL_WARNINGS
# (other warnings are listed only). Full report: reports/erc.rpt
#   tools/erc.sh [schematic.kicad_sch [report.rpt]]   (arguments only for tests on a scratch copy)
#
# no_connect_connected is fatal (decision D2): a no-connect flag on a pin that is wired to
# something is always a drawing mistake here, and with a pin of type no_connect the KiCad 10
# netlist would hide it from compare_netlists (the pin stays in its own unconnected-(...) net).
set -u
cd "$(dirname "$0")/.."
FATAL_WARNINGS="no_connect_connected"
sch=${1:-kicad/tube_control_card.kicad_sch}
rpt=${2:-reports/erc.rpt}
mkdir -p "$(dirname "$rpt")"
tools/p2k/bin/kicad-cli sch erc --severity-all -o "$rpt" "$sch" >/dev/null || exit 1
errs=$(grep -c '; error' "$rpt")
warns=$(grep -c '; warning' "$rpt")
fatal=0
for t in $FATAL_WARNINGS; do
    n=$(grep -c "^\[$t\]" "$rpt")
    [ "$n" -gt 0 ] && { echo "erc: $n x $t (fatal warning, decision D2):"; grep -A3 "^\[$t\]" "$rpt" | grep '@' ; fatal=1; }
done
echo "erc: $errs errors, $warns warnings ($rpt)"
[ "$errs" -eq 0 ] && [ "$fatal" -eq 0 ]
