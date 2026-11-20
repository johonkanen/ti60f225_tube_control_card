# Next prompt

Ready-to-paste prompt for the next agent session. Replaced at the end of every session.

```
Convert the Proteus board in /home/jari/dev/ti60f225_tube_control_card to KiCad 10: Phase 2, footprints.
Phases 0 and 1 are done: 12 sheets, 146 of 146 parts, full netlist comparison clean (0 wrong-net pins,
every IPC net complete), ERC 0 errors.

Read, in this order: PLAN.md, STATUS.md (Phase 0 "U10 facts", Phase 1 preparation, session T3, findings
1, 4, 9, 12, p2k candidates 1-4, decisions D1 and D2), tools/p2k/CONVERSION_PLAYBOOK.md (sections 1,
3 "Phase 2" and 5), tools/p2k/README.md (footprints, check_footprints, FOOTPRINT_PAD_SIZES), and as the
worked example ~/dev/tube_psu_kicad/tools/gen_footprints.py with its STATUS.md Phase 2 (read only). Run
tools/check_all.sh first and compare with STATUS.md "Last verification".

Write tools/gen_footprints.py (p2k.footprints.run(RULES, PROJECT)): a footprint for every one of the 146
IPC parts -> lib/footprint_map.csv and lib/tube_control_card.pretty, with --check; then
tools/p2k/bin/p2k check_footprints: every part fits its IPC pads within 0.05 mm, pads matched by number
(reports/footprint_fit.csv, footprint_pads.csv). Packages are in lib/part_map.csv (column package, from
ROOT.LYT). Board specifics:
- U10 (Ti60F225, BGA225C65P15X15): 225 balls A1..R15 at 0.65 mm pitch, 0.3 mm round SMD pads, top,
  centre (37.023, -13.710), A1 at (41.573, -18.26) = an A1-top-left footprint rotated 180 deg. Build the
  footprint from the IPC pads (or derive it from a KiCad BGA footprint if one fits within 0.05 mm);
  pad names = ball ids = symbol pin numbers.
- Two-pad terminals of decision D1 (J2, J4, J5, J9, ISO5V, ISO_G, RS485A, RS485B): two 1.4 mm holes
  5 mm apart, both pad number 1 (the symbol has one pin 1). On J2, ISO5V, ISO_G, RS485A, RS485B the two
  pads are on different IPC nets (SPLIT_PIN_MERGES): check_footprints must fit both pads; note what the
  shared tool needs (p2k candidate 1) and work around board-locally.
- The 4 SMD test pads without refdes (SMD_FREE_PADS: 0.711 mm, top, on JFET_6, JFET_5, GPIOL_10,
  GPIOL_11) and the 4 plated 3.0 mm mounting holes: board-only footprints for Phase 3 (the shared free
  pad footprint is THT: p2k candidate 2, board-local SMD variant).
- Finding 9 (ADC1, ADC121C027, pin ids A1 A2 COM1 COM2 K1 K2): map the ids to the SOT-23-6 pads from the
  IPC positions and report which physical pad gets 3V3 and which the filtered BIASFEEDBACK input,
  against the datasheet pinout (VA / VIN). Finding 12 (AP61202, SOT563): the same for pin 6 "VOUT" (the
  1V_ENABLE output of PWR2) against the datasheet pinout. Report, don't fix.
- Check every multi-pin package's pin order against the IPC pad positions (pin 1 position, rotation,
  mirrored bottom-side parts: 80 parts are on the bottom) and list the oddities in STATUS.md.
- Pad sizes: FOOTPRINT_PAD_SIZES as in the playbook; if the choice matters (DRC in Phase 3), record the
  question for the user instead of deciding silently.

Add gen_footprints --check and check_footprints to tools/check_all.sh; negative-test each new check
(a pad moved 0.06 mm, a swapped pad number, a wrong rotation) and record the results.

Rules (PLAN.md section 5): don't change tools/p2k or its pin (board-local workarounds, noted in
STATUS.md "p2k candidates"); don't touch other repos; report design findings, don't fix them;
generate, don't hand-edit; temporary files in build/tmp; never run the KiCad AppImage with --version
(use tools/p2k/bin/kipy and tools/p2k/bin/kicad-cli). The schematic must not change: after any change of
tools/gen_symbols.py or a sheet script run tools/make_sheets.sh, check_symbols, tools/test_no_connect.py
and the full compare. At the end: tools/check_all.sh passing, STATUS.md updated (Phase 2 state,
footprint table per package, fit residuals, pin-order oddities, findings 9 and 12 results, check output,
p2k candidates, decisions), README.md "Status" updated, next_prompt.md replaced with the prompt for
Phase 3 (PCB: build_pcb, gerber_to_tracks, assign_nets, pours_to_zones, the D1 acceptance in
check_board, the SMD test pads, PCB_RULES from the measured gaps of finding 4, the board thickness
question of finding 5), commit and push (git push origin main). If something needs a user decision,
stop, record it in STATUS.md, commit and push, and report it.
```
