#!/usr/bin/env bash
# Run every verification step. Exit status is non-zero if any step fails.
# Each phase adds its steps here (playbook principle 5). The tools are the proteus2kicad
# submodule in tools/p2k; board values in p2k_config.py.
set -u
cd "$(dirname "$0")/.."
[ -x tools/p2k/bin/p2k ] || { echo "tools/p2k missing: git submodule update --init"; exit 1; }
fail=0
mkdir -p build/tmp
log=build/tmp/check_all.log; : > "$log"
step() {
    echo "== $1" | tee -a "$log"; shift
    "$@" 2>&1 | tee -a "$log"
    [ "${PIPESTATUS[0]}" -eq 0 ] || { echo "!! FAILED: $*" | tee -a "$log"; fail=1; }
}

step "KiCad environment" tools/p2k/bin/kipy -c "import pcbnew; v = pcbnew.GetBuildVersion(); print('pcbnew', v); assert v.startswith('10.0.7'), v"
# p2k ipc356 --check / p2k check_sources plus the board-local acceptance of the split terminal
# nets, the SMD test pads and the BGAPad flashes (STATUS.md "p2k candidates")
step "IPC-D-356A parser self-check (p2k ipc356 --check + board exceptions)" python3 tools/ipc356_check.py
step "Gerber X2 export vs IPC (p2k check_sources + board exceptions)" python3 tools/check_sources.py
# Phase 1
step "Part map up to date" python3 tools/make_part_map.py --check
step "Symbol library up to date" python3 tools/gen_symbols.py --check
step "Symbol pin sets vs IPC" tools/p2k/bin/p2k check_symbols
step "Sheets up to date (tools/sheets/sheetNN.py)" tools/make_sheets.sh --check
# fails on errors (except tools/erc_pending.txt) and on no_connect_connected (decision D2)
step "ERC" tools/erc.sh
# p2k compare_netlists with the five split terminal nets of decision D1 accepted (board-local);
# full comparison: all 146 parts, every IPC net complete (no --allow-missing)
step "Netlist comparison vs IPC (D1 merges accepted)" python3 tools/compare_netlists.py

# Phase 2: footprints
step "Footprint library, map and fp-lib-table up to date" python3 tools/gen_footprints.py --check
step "Footprints vs IPC pad geometry (fit and pcbnew placement)" tools/p2k/bin/kipy -m p2k.check_footprints --pcbnew
# unmoved KiCad base footprints with the renumbering of gen_footprints (a wrong renumbering passes
# check_footprints because p2k.footprints.derive moves the pads); U10 ball A1 orientation (180 deg)
step "Pin order vs unmoved KiCad base footprints" python3 tools/check_pin_order.py

# Phase 3: PCB. Every step through the board-local wrappers (tools/pcb_wrap.py: D1 split terminals,
# U10 BGAPad flashes, SMD test pads, "/" in unconnected net names; tools/drc_check.py: D1
# unconnected items; the pad-size decision is applied, PENDING is empty)
step "PCB rebuilt from schematic + gerbers, up to date (make_pcb --check)" tools/make_pcb.sh --check
step "Board pads, holes, test pads, vias vs IPC (position, size, nets 1:1, D1 merges accepted)" tools/p2k/bin/kipy tools/pcb_wrap.py check_board
step "Board copper connectivity after zone fill (assign_nets --check)" python3 tools/drc_check.py copper
step "DRC with schematic parity" python3 tools/drc_check.py drc

# Phase 4: independent verification (kicad-cli IPC-D-356 export and gerber plot of the board vs Proteus).
# tools/phase4_wrap.py: the shared tools unchanged; ipc356_diff judged with exactly the five D1 merges
# accepted (+ test pads, U10 balls, one pad per unconnected-(...) net); gerber_roundtrip with BGAPad
# flashes counted as pads. DRILL_SMALLER (J8, 1.016 -> 1.0) is accepted by the shared tools by diameter
# pair; tools/check_drill_smaller.py requires it per pad (exactly J8-1..3).
step "IPC-D-356 from the board vs Proteus (pads, vias, holes, test pads, nets; D1 merges accepted)" python3 tools/phase4_wrap.py ipc356_diff
step "Smaller board drills are exactly the three decided J8 holes" tools/p2k/bin/kipy tools/check_drill_smaller.py
step "Gerber round trip vs Proteus (copper XOR incl. pours, coverage, drills, Excellon)" python3 tools/phase4_wrap.py gerber_roundtrip --check
# the Phase 4 reader's own transcript of the PDF (every pin, by eye; own IPC parser, no p2k code) vs IPC and KiCad netlist
step "Independent PDF reading vs IPC and KiCad netlist (tools/phase4_reading)" python3 tools/phase4_reading/reading.py

echo
pending=$(grep -c "PENDING USER DECISION" "$log")
if [ $fail -ne 0 ]; then echo "SOME CHECKS FAILED"
elif [ "$pending" -ne 0 ]; then echo "ALL CHECKS PASSED, EXCEPT $pending PENDING USER DECISION(S):"; grep "PENDING USER DECISION" "$log" | sed 's/^/  /'
else echo "ALL CHECKS PASSED"; fi
exit $fail
