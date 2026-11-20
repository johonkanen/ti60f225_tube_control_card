# Next prompt

Ready-to-paste prompt for the next agent session. Replaced at the end of every session.

```
Convert the Proteus board in /home/jari/dev/ti60f225_tube_control_card to KiCad 10: Phase 1 transcription,
session T2 = sheets 7, 9, 12, 4 (in this order). Session T1 (sheets 1, 11, 10, 8, 3) is done.

Read, in this order: PLAN.md, STATUS.md (Phase 1 transcription session T1, Transcription rules,
findings, p2k candidates, decisions D1 and D2), tools/p2k/CONVERSION_PLAYBOOK.md (sections 1, 3
"Phase 1" and 5), tools/p2k/README.md (sheetkit, sch_builder), tools/sheets/_common.py and the five
finished scripts tools/sheets/sheet01.py, 11, 10, 08, 03 (the pattern to follow). Run
tools/check_all.sh first and compare with STATUS.md "Last verification".

Render the PDF pages first (pdftoppm -r 200 -png source/schematic_pdf/fpga_boardv2.5.PDF build/tmp/pdf/hi).

For each sheet write tools/sheets/sheetNN.py (NN = PDF page) that rebuilds kicad/NN_*.kicad_sch from
scratch, following STATUS.md "Transcription rules" and using the IPC-driven helpers of _common.py:
two() for R / C / L, place_pin() for ICs, pin_tie() / tie() for every label, power symbol and
no-connect flag (they take the net from the IPC netlist; type no net name from the PDF), header(),
note(), term(), place_mirrored(), P(). Plain wires for the #00xxx nets, alias pairs and hand notes as
text notes, grid 1.27 mm, layout close to the PDF. Compare the PDF label of every pin with its IPC net:
a difference that is not a known alias is a finding. Add the repeated blocks to _common.py: the JFET
driver cell of pages 9 and 12 (one helper for both sheets) and the SN74AXC8T245 level shifter of page 4.
Multi-unit parts: R_ARRAY4 (units A-D), TLV9304PWR / TL084HIDYYR (units A-D + power unit E) - place
every unit (sh.place(..., unit=k)); check the unit/pin assignment against reference/pin_nets_by_component.md.

Decision D2: no pin of type no_connect; every N/C pad gets a no-connect flag (pin_tie does it);
tools/erc.sh fails on no_connect_connected. ERC errors that need a sheet not drawn yet (an input
driven only by a U10 ball: sheets 2, 5, 6 come in T3) go into tools/erc_pending.txt with the reason;
remove entries that are resolved (stale entries fail). No other ERC error may remain.

After each sheet: python3 tools/compare_netlists.py --allow-missing --sheet N (the board wrapper),
tools/erc.sh, tools/p2k/bin/p2k render_sheet kicad/NN_*.kicad_sch and compare the render with
build/tmp/pdf/hi-NN.png; target 0 missing on that sheet, 0 compare errors, 0 ERC errors outside the
pending list (explain the warnings in STATUS.md). Commit after each finished sheet. Don't place any U10
unit in this session. After a change of tools/gen_symbols.py: tools/make_sheets.sh, check_symbols,
and tools/test_no_connect.py.

Rules (PLAN.md section 5): don't change tools/p2k or its pin (board-local workarounds, noted in
STATUS.md "p2k candidates"); don't touch other repos; report design findings, don't fix them;
generate, don't hand-edit; temporary files in build/tmp; never run the KiCad AppImage with --version
(use tools/p2k/bin/kipy and tools/p2k/bin/kicad-cli). At the end: tools/check_all.sh passing, STATUS.md
updated (per-sheet result table, check output, the isolated_pin_label warnings still open, findings,
p2k candidates, decisions), next_prompt.md replaced with the prompt for session T3 (sheets 2, 5, 6 =
all eight U10 units with the 62 no-connect flags, then the full compare without --allow-missing, an
empty tools/erc_pending.txt, and check_all.sh switched to the full compare), commit and push
(git push origin main). If something needs a user decision, stop, record it in STATUS.md, commit and
push, and report it.
```
