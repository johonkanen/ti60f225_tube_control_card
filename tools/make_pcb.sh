#!/usr/bin/env bash
# Phase 3: rebuild kicad/tube_control_card.kicad_pcb from the schematic and the Proteus gerbers
# (shared tools in tools/p2k, board values in p2k_config.py). Re-runnable; two runs give a
# byte-identical board (UUIDs seeded per step). As ~/dev/tube_hv_supplies_kicad/tools/make_pcb.sh,
# each step through tools/pcb_wrap.py (decision D1 split terminals, U10 BGAPad flashes, SMD test
# pads; STATUS.md "p2k candidates"):
#   1 build_pcb         footprints with nets at the Proteus positions, rules, outline, holes H1-H4,
#                       SMD test pads TP1-TP4
#   2 gerber_to_tracks  copper gerbers -> tracks and vias, pour outlines on User.1-4
#   3 assign_nets       nets of tracks/vias/pours by copper connectivity -> reports/pour_nets.json
#   4 pours_to_zones    pours -> zones, zone fill (ZONE_FILLER), saved
#   5 place_refdes      references clear of pads / silk / edge (else smaller, else Fab only;
#                       Phase 5 user decision; p2k.place_refdes directly, no wrapper needed)
# The copper check after the fill (assign_nets --check), check_board and the DRC run in
# tools/check_all.sh. Footprints and the fit come from tools/gen_footprints.py and
# p2k.check_footprints (reports/footprint_fit.csv): run those first after footprint changes.
#
#   tools/make_pcb.sh           rebuild the board in place
#   tools/make_pcb.sh --check   rebuild into build/tmp/make_pcb_check (with a copy of the
#                               .kicad_pro) and fail unless the board, reports/pour_nets.json and
#                               the stage A/B sections of reports/assign_nets.txt equal the
#                               committed ones byte for byte
set -eu
cd "$(dirname "$0")/.."
K=tools/p2k/bin/kipy
W=tools/pcb_wrap.py
PCB=kicad/tube_control_card.kicad_pcb
run() {   # chained with &&: `set -e` does not apply inside a function called in a `||` list
    $K $W build_pcb && $K $W gerber_to_tracks && $K $W assign_nets && $K $W pours_to_zones && $K -m p2k.place_refdes
}
if [ "${1:-}" = "--check" ]; then
    tmp="$PWD/build/tmp/make_pcb_check"
    rm -rf "$tmp"; mkdir -p "$tmp/reports"; trap 'rm -rf "$tmp"' EXIT
    cp reports/footprint_fit.csv "$tmp/reports/"
    cp kicad/tube_control_card.kicad_pro "$tmp/"   # pcbnew loads the project next to the board (affects the UUID sequence)
    export P2K_PCB="$tmp/tube_control_card.kicad_pcb" P2K_REPORTS="$tmp/reports"
    run >"$tmp/log" 2>&1 || { cat "$tmp/log"; echo "make_pcb: FAILED"; exit 1; }
    ok=1
    cmp -s "$P2K_PCB" "$PCB" || { echo "make_pcb: $PCB is not up to date (run tools/make_pcb.sh)"; ok=0; }
    # assign_nets --check (check_all.sh) appends its own section to the report: compare stages A/B only
    stages() { sed '/^== after zone fill/,$d' "$1"; }
    [ "$(stages "$tmp/reports/assign_nets.txt")" = "$(stages reports/assign_nets.txt)" ] || { echo "make_pcb: reports/assign_nets.txt is not up to date"; ok=0; }
    cmp -s "$tmp/reports/pour_nets.json" reports/pour_nets.json || { echo "make_pcb: reports/pour_nets.json is not up to date"; ok=0; }
    grep -E "^(build_pcb|gerber_to_tracks: [0-9]|assign_nets: stage|pours_to_zones|place_refdes)" "$tmp/log" | sed "/^build_pcb/s/ -> .*//"
    [ $ok -eq 1 ] && echo "make_pcb: board rebuilt from scratch, byte-identical" || exit 1
else
    run
fi
