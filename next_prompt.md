# Next prompt

Ready-to-paste prompt for the next agent session. Replaced at the end of every session.

```
Convert the Proteus board in /home/jari/dev/ti60f225_tube_control_card to KiCad 10: Phase 1 transcription,
session T1 = sheets 1, 11, 10, 8, 3 (in this order).

Read, in this order: PLAN.md, STATUS.md (Phase 1 preparation, D1 implementation, Transcription rules,
findings, p2k candidates, decision D1), tools/p2k/CONVERSION_PLAYBOOK.md (sections 1, 3 "Phase 1" and 5),
tools/p2k/README.md (sheetkit, sch_builder), README.md. Run tools/check_all.sh first and compare with
STATUS.md "Last verification".
Reference conversions (read only, don't change them): ~/dev/tube_psu_kicad (tools/sheets/sheetNN.py,
_common.py, STATUS.md "Phase 1 transcription") and ~/dev/tube_power_amp_kicad (tools/sheets/, its
_common.py is the origin of term(), place_mirrored(), P() in our tools/sheets/_common.py).

Render the PDF pages first (pdftoppm -r 200 -png source/schematic_pdf/fpga_boardv2.5.PDF build/tmp/pdf/hi).

For each sheet write tools/sheets/sheetNN.py (NN = PDF page) that rebuilds kicad/NN_*.kicad_sch from
scratch with p2k.sheetkit / tools/sheets/_common.py, following STATUS.md "Transcription rules":
symbols and values from lib/part_map.csv; net names = IPC names (look up every pin in
reference/pin_nets_by_component.md, not the PDF label); power symbols for the 10 rails (flagged_power
where the rail enters or is generated); global labels for nets on several sheets, local labels
otherwise, plain wires for #00xxx nets; no-connect flags on the N/C pins; page-1 alias pairs and the
other PDF aliases as text notes; the D1 terminals (J2, ISO5V, ISO_G, RS485A, RS485B; also J4, J5, J9)
as one TERMINAL pin drawn as in the PDF (term()); grid 1.27 mm, layout close to the PDF (P()).
Sheet 1 has J2, J4, J5, J9, J8, R16 plus the alias notes; sheet 11 exercises decision D1 (RS485B node =
R68-2, RS1-7 and R67-1).

After each sheet: python3 tools/compare_netlists.py --allow-missing --sheet N (the board wrapper with the
D1 acceptance, not the bare p2k tool), tools/erc.sh, tools/p2k/bin/p2k render_sheet kicad/NN_*.kicad_sch
and compare the render with build/tmp/pdf/hi-NN.png; target 0 missing on that sheet, 0 compare errors,
0 ERC errors (explain the remaining warnings in STATUS.md). Add repeated blocks to _common.py.
Don't place any U10 unit in this session (U10 sheets 2, 5, 6 come last, in one session: compare
reports the balls of unplaced units as errors).

Rules (PLAN.md section 5): don't change tools/p2k or its pin (board-local workarounds, noted in
STATUS.md "p2k candidates"); don't touch other repos; report design findings, don't fix them;
generate, don't hand-edit; temporary files in build/tmp; never run the KiCad AppImage with --version
(use tools/p2k/bin/kipy and tools/p2k/bin/kicad-cli). At the end: tools/check_all.sh passing, STATUS.md
updated (per-sheet result table with the compare output, check output, findings, p2k candidates,
decisions), next_prompt.md replaced with the prompt for session T2 (sheets 7, 9, 12, 4), commit and push
(git push origin main). If something needs a user decision, stop, record it in STATUS.md, commit and
push, and report it.
```
