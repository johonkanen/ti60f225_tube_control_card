# Next prompt

Ready-to-paste prompt for the next agent session. Replaced at the end of every session.

```
Convert the Proteus board in /home/jari/dev/ti60f225_tube_control_card to KiCad 10: Phase 1 transcription,
session T3 = sheets 2, 5, 6 (the last three: all eight units of U10, Ti60F225). Sessions T1 (sheets
1, 11, 10, 8, 3) and T2 (7, 9, 12, 4) are done: 109 of 146 parts.

Read, in this order: PLAN.md, STATUS.md (Phase 1 preparation "U10 = TI60F225", sessions T1 and T2,
Transcription rules, findings, p2k candidates, decisions D1 and D2), tools/p2k/CONVERSION_PLAYBOOK.md
(sections 1, 3 "Phase 1" and 5), tools/p2k/README.md (sheetkit, sch_builder), tools/sheets/_common.py
and the finished scripts tools/sheets/sheet03.py, 04, 07, 09, 10, 11 (the pattern to follow). Run
tools/check_all.sh first and compare with STATUS.md "Last verification".

Render the PDF pages first (pdftoppm -r 200 -png source/schematic_pdf/fpga_boardv2.5.PDF build/tmp/pdf/hi).

Write tools/sheets/sheet02.py (FPGA configuration and clock: 19 parts + U10 units A and C),
sheet05.py (U10 units B, D, E, F; no other part) and sheet06.py (FPGA power: 18 parts + U10 units
G and H), each rebuilding kicad/NN_*.kicad_sch from scratch, following STATUS.md "Transcription
rules" and using the IPC-driven helpers of _common.py: two(), place_pin(), pin_tie() / tie() for
every label, power symbol and no-connect flag (they take the net from the IPC netlist; type no net
name from the PDF), note(), P(). U10: sh.place("TI60F225", "U10", x, y, unit=k) with k = 1..8 for
A..H and ref_at / value_at per unit; add a helper to _common.py that places one unit and runs
pin_tie() over all its balls (side from the pin position), so the 62 N/C balls get their no-connect
flags (decision D2) and every connected ball its label or power symbol. Plain wires for the #00xxx
nets, alias pairs (page 2: TXD = GPIOL_N_09, RXD = GPIOL_P_10 ...) and hand notes ("1v8 oscillator
voltage!!!", "1v8 flash voltage!!!") as text notes, grid 1.27 mm, layout close to the PDF. Compare
the PDF label of every ball / pin with its IPC net: a difference that is not a known alias is a
finding. Compare reports the connected balls of unplaced U10 units as errors and ERC an unplaced
power unit as an error, so judge the three sheets together: draw all eight units before expecting a
clean result (keep --allow-missing while the other parts of sheets 2 and 6 are missing).

Then: python3 tools/compare_netlists.py (the board wrapper, without --allow-missing): 146/146 parts,
0 missing, 0 wrong-net pins, every IPC net complete; tools/erc.sh: 0 errors with an EMPTY
tools/erc_pending.txt (the three entries RS1-2, AD2-1, AD2-3 are resolved by the U10 balls; stale
entries fail) and only the expected isolated_pin_label warnings: the 6 single-pin nets of U1 / U9
and the 8 single-ball nets of U10 (transcription rules) - list and explain every warning in
STATUS.md; the 80 warnings open after T2 must be gone. Switch tools/check_all.sh to the full compare
(drop --allow-missing). tools/p2k/bin/p2k render_sheet for each sheet and compare with
build/tmp/pdf/hi-NN.png. Commit after each finished sheet (or after the three U10 sheets together if
the checks cannot pass before). After a change of tools/gen_symbols.py: tools/make_sheets.sh,
check_symbols, and tools/test_no_connect.py.

Rules (PLAN.md section 5): don't change tools/p2k or its pin (board-local workarounds, noted in
STATUS.md "p2k candidates"); don't touch other repos; report design findings, don't fix them;
generate, don't hand-edit; temporary files in build/tmp; never run the KiCad AppImage with --version
(use tools/p2k/bin/kipy and tools/p2k/bin/kicad-cli). At the end: tools/check_all.sh passing with the
full compare, STATUS.md updated (Phase 1 done or what is left, per-sheet result table, check output,
the remaining warnings, findings, p2k candidates, decisions), README.md "Status" updated,
next_prompt.md replaced with the prompt for Phase 2 (footprints: tools/gen_footprints.py,
check_footprints, the U10 BGA footprint fitted to the IPC balls, the two-pad terminals of decision
D1, the 4 SMD test pads, findings 9 and 12 pinout checks), commit and push (git push origin main).
If something needs a user decision, stop, record it in STATUS.md, commit and push, and report it.
```
