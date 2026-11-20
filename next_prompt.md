# Next prompt

Ready-to-paste prompt for the next agent session. Replaced at the end of every session.

```
Convert the Proteus board in /home/jari/dev/ti60f225_tube_control_card to KiCad 10: Phase 1 preparation
(part map, symbols, schematic skeleton, netlist comparison; no sheet transcription yet).

Read, in this order: PLAN.md, STATUS.md (Phase 0 result, findings, p2k candidates, open decision D1),
tools/p2k/CONVERSION_PLAYBOOK.md (sections 1, 3 "Phase 1" and 5), tools/p2k/README.md (tools and
p2k_config.py keys), README.md. Run tools/check_all.sh first and compare with STATUS.md "Last verification".
The finished reference conversion is ~/dev/tube_psu_kicad (same tools): read its tools/make_part_map.py,
tools/gen_symbols.py, tools/erc.sh, tools/check_all.sh and STATUS.md "Phase 1" for how it was done.
Read it only; don't change it.

Render the PDF pages first (pdftoppm -r 200 -png source/schematic_pdf/fpga_boardv2.5.PDF build/tmp/pdf/hi).

Do the Phase 1 preparation as the playbook describes:
- tools/make_part_map.py -> lib/part_map.csv (refdes, sheet, lib_id, value; --check): values from
  p2k.pdsprj.dsn_values (all 146 found); p2k.pdsprj.lyt_parts finds nothing in this ROOT.LYT (STATUS.md
  p2k candidate 4): write a board-local reader for device/package if you need them, or use the DSN
  pinouts. Pages from p2k.pdftext; many refdes-like words are FPGA ball names or net labels (R3, R10,
  L1, N14, J10 ... on pages 1, 5, 6; X0-X7 on page 7): resolve each part's page on the renders.
- tools/gen_symbols.py -> lib/tube_control_card.kicad_sym (--check). U10 (Ti60F225, 225 balls,
  ids A1..R15 = IPC pin ids) as a multi-unit symbol following the PDF units A-H (A config/JTAG, B-F IO
  banks, G power, H GND; every ball, the 62 N/C ones included, must be on some unit). Check the U10
  pin names against the Efinix Ti60F225 pinout where you can (STATUS.md finding 3: only 12 GND balls).
  Quad op-amps / resistor arrays (U5, U6, U11, U14; R14, R15, R17, R18, R22-R25) as units like the PDF.
  Terminals (J2, J4, J5, J9, ISO5V, ISO_G, RS485A, RS485B): one pin 1 (two pads in the footprint).
- run p2k check_symbols; tools/erc.sh; p2k make_skeleton (SHEETS are in p2k_config.py);
  p2k compare_netlists --allow-missing working on the empty skeleton; add these steps to
  tools/check_all.sh.
- write the transcription rules into STATUS.md (power nets -> power symbols: GND, 1V, 1V8, 3V3, 5V,
  12V, AD_3V3, ISO5V, RS485_GND, OPAMP_-15V; other named nets -> labels in IPC spelling; auto-named
  nets -> wires; N/C pins; single-pin nets (finding 2); the page 1 alias pairs; grid 1.27 mm) and the
  sheet order for the transcription sessions.
- decision D1 (split terminal nets) is the user's: if it is still open, keep the netlist comparison
  of those five terminals as a recorded exception and ask; don't decide it yourself.

Rules (PLAN.md section 5): don't change tools/p2k or its pin (board-local workarounds, noted in
STATUS.md "p2k candidates"); don't touch other repos; report design findings, don't fix them;
generate, don't hand-edit; temporary files in build/tmp; never run the KiCad AppImage with --version
(use tools/p2k/bin/kipy and tools/p2k/bin/kicad-cli). At the end: tools/check_all.sh passing, STATUS.md
updated (result, check output, findings, p2k candidates, decisions), next_prompt.md replaced with the
prompt for the first transcription session, commit and push (git push origin main).
```
