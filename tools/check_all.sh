#!/usr/bin/env bash
# Run every verification step. Exit status is non-zero if any step fails.
# Each phase adds its steps here (playbook principle 5). The tools are the proteus2kicad
# submodule in tools/p2k; board values in p2k_config.py (decision D1 = SPLIT_PIN_MERGES, the SMD
# test pads = SMD_FREE_PADS, the U10 BGAPad flashes = BGA_REFDES; strict checks on by default).
# Generation stopped on 2026-11-20 (STATUS.md "Decisions"): the committed KiCad files are the
# source, so nothing here regenerates or byte-compares them (the frozen generators are in
# tools/generate/); every step checks the committed files against the Proteus sources and the
# KiCad rules. The hand edits made since (STATUS.md "Hand edits after generation stopped") are
# accepted exactly by tools/hand_edits.py (H): the listed pin-net changes, the copper inside the
# listed area and the listed track-count change; anything else still fails.
set -u
cd "$(dirname "$0")/.."
[ -x tools/p2k/bin/p2k ] || { echo "tools/p2k missing: git submodule update --init"; exit 1; }
P=tools/p2k/bin/p2k
K=tools/p2k/bin/kipy
H=tools/hand_edits.py
fail=0
mkdir -p build/tmp
log=build/tmp/check_all.log; : > "$log"
step() {
    echo "== $1" | tee -a "$log"; shift
    "$@" 2>&1 | tee -a "$log"
    [ "${PIPESTATUS[0]}" -eq 0 ] || { echo "!! FAILED: $*" | tee -a "$log"; fail=1; }
}

step "KiCad environment" $K -c "import pcbnew; v = pcbnew.GetBuildVersion(); print('pcbnew', v); assert v.startswith('10.0.7'), v"
# reference/* is the parsed Proteus netlist, not a design file: it never changes after the freeze, and this
# step keeps it equal to source/ (a hand edit must not be hidden by editing the reference)
step "IPC-D-356A parser self-check, reference/ = the Proteus IPC (split pins, SMD test pads)" $P ipc356 --check
step "Gerber X2 export vs IPC (BGAPad flashes = U10 balls, SMD test pads)" $P check_sources
# Phase 1
step "Symbol pin sets vs IPC" $P check_symbols
# fails on errors and on the fatal warning no_connect_connected (decision D2, ERC_FATAL_WARNINGS)
step "ERC" $P erc
# full comparison: all 146 parts, every IPC net complete (no --allow-missing); the five D1 merges
# accepted (SPLIT_PIN_MERGES); joined N/C pins fail (strict nc_joined); hand edits: PIN_NETS
step "Netlist comparison vs IPC (hand edits: PIN_NETS)" python3 $H compare_netlists

# Phase 2: footprints
step "Footprints vs IPC pad geometry (fit and pcbnew placement)" $K -m p2k.check_footprints --pcbnew
# unmoved KiCad base footprints with the renumbering of tools/generate/gen_footprints.py (RULES read
# through FOOTPRINT_SCRIPT, nothing written; a wrong renumbering passes
# check_footprints because p2k.footprints.derive moves the pads); U10 ball A1 orientation (180 deg)
step "Pin order vs unmoved KiCad base footprints (PIN_ORDER)" $P check_pin_order

# Phase 3: PCB
step "Board pads, holes, test pads, vias vs IPC (position, size, nets 1:1, D1 merges accepted; hand edits: PIN_NETS)" $K $H check_board
step "Board copper connectivity after zone fill (assign_nets --check; hand edits: PIN_NETS)" $K $H assign_nets --check
step "DRC with schematic parity" $P drc

# Phase 4: independent verification (kicad-cli IPC-D-356 export and gerber plot of the board vs Proteus).
# PHASE4_EXPECTED = the recorded summary; DRILL_SMALLER = exactly J8-1..3; strict roundtrip_counts =
# the KiCad track draws / flashes per layer (+ TRACK_DELTA of the hand edits); hand-edited copper only in AREAS
step "IPC-D-356 from the board vs Proteus (pads, vias, holes, test pads, nets; D1 merges accepted; hand edits: PIN_NETS)" python3 $H ipc356_diff
step "Gerber round trip vs Proteus (copper XOR incl. pours, coverage, counts, drills, Excellon; hand edits: AREAS, TRACK_DELTA)" python3 $H gerber_roundtrip --check
# the Phase 4 reader's own transcript of the PDF (every pin, by eye; own IPC parser, no p2k code) vs IPC and KiCad netlist;
# hand edits: PIN_LABELS of tools/hand_edits.py
step "Independent PDF reading vs IPC and KiCad netlist (tools/phase4_reading)" python3 tools/phase4_reading/reading.py
# decision D2 negative test (six scratch variants of PWR4 in build/tmp/nctest: the real p2k erc / compare_netlists
# must catch a wired N/C pin); ~30 s, added to the regular run when generation stopped
step "No-connect negative test (decision D2, tools/test_no_connect.py)" python3 tools/test_no_connect.py

echo
pending=$(grep -c "PENDING USER DECISION" "$log")
if [ $fail -ne 0 ]; then echo "SOME CHECKS FAILED"
elif [ "$pending" -ne 0 ]; then echo "ALL CHECKS PASSED, EXCEPT $pending PENDING USER DECISION(S):"; grep "PENDING USER DECISION" "$log" | sed 's/^/  /'
else echo "ALL CHECKS PASSED"; fi
exit $fail
