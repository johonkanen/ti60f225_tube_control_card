# Next prompt

Ready-to-paste prompt for the next agent session. Replaced at the end of every session.

```
Proteus board /home/jari/dev/ti60f225_tube_control_card converted to KiCad 10: Phases 0-4 are done
(12 sheets, 146 parts, PCB with 3373 tracks / 240 vias / 20 zones; Phase 4 independent verification
passed: ipc356_diff 1132 / 1132 records with only the five D1 merges, gerber round trip clean on all 4
copper layers incl. pours and drills, all 876 pins of the PDF read independently, no difference). What
is left is Phase 5, clean-up: ONLY what the user chooses. Note: this Ti60F225 card is NOT installed in
the amplifier (the Agilex 3 card is); the conversion is a reference and a starting point, so Phase 5 may
well be "nothing" - ask before doing any work.

Read, in this order: PLAN.md, STATUS.md (phase table, "Phase 4", "Remaining DRC items", findings 1, 9,
24, 25, 26, Decisions), tools/p2k/CONVERSION_PLAYBOOK.md (section 3 "Phase 5", section 5). Reference
(read only): ~/dev/tube_psu_kicad (Phase 5 done: REFDES_PLACEMENT, REMOVED_TRACKS, silk bodies).

Start with tools/check_all.sh; it must print "ALL CHECKS PASSED" (compare 146/146; ERC 0 / 14; make_pcb
byte-identical; copper 307 groups 0 / 0 / 0 + 5 D1; DRC 0 shorts, 32 accepted courtyards, 5 D1
unconnected; ipc356_diff OK with 5 accepted D1 merges; check_drill_smaller: exactly J8-1..3; gerber
round trip OK, only pad-shape clusters, track draws 2152 / 72 / 221 / 928; PDF reading: no difference).

Ask the user (through the coordinating session) which of these to do, then implement each in the
generators (never by hand), re-run tools/make_pcb.sh and tools/check_all.sh, and update the recorded
counts (DRC warnings, RT_DRAWS in tools/phase4_wrap.py if tracks are removed, EXPECT):
1. Reference positions (167 silk_overlap / 155 silk_over_copper / 4 silk_edge_clearance warnings):
   p2k place_refdes as the last make_pcb step (REFDES_PLACEMENT), or leave the KiCad defaults.
2. Dangling Proteus copper (finding 26: 11 track_dangling, 1 via_dangling): keep as built, or record
   REMOVED_TRACKS / REMOVED_VIAS (the checks accept recorded removals).
3. Footprint bodies: J1 (Phoenix MPT guess, causes 4 courtyard overlaps) vs a 1x05 pin-header body;
   FLASH1 land pattern (finding 24) stays as built in rev A.
4. Pad sizes / drills where DRC does not force a choice (KiCad pads on U10, passives, PWR1-3, FLASH1,
   RS1, OSC1, J1, J3, J6, J8, terminals; J8 drill 1.0 accepted): keep, or Proteus pads on more parts.
5. Whether rev A stays generated or the first manual KiCad layout change is made (record it in STATUS.md).
Redesign items are NOT Phase 5 (report only): findings 1 (D1 split terminals), 9 (ADC1 VA / VIN), 24,
25 (J11 mirrored numbering, together with tube_hv_supplies J1), 26.

Rules (PLAN.md section 5): don't change tools/p2k or its pin (c5682dd); board-local workarounds in
tools/, noted in STATUS.md "p2k candidates" (now 1-33); don't touch other repos; generate, don't
hand-edit; never use the no_connect pin type; temporary files in build/tmp; never run the KiCad AppImage
with --version (use tools/p2k/bin/kipy and tools/p2k/bin/kicad-cli). Negative-test anything new. At the
end: tools/check_all.sh passing, STATUS.md (phase table, Phase 5 section, decisions), README status,
next_prompt.md replaced, commit and push (git push origin main). When Phase 5 is closed (or declined),
STATUS.md says the conversion is complete so the amplifier master repo can add this repo as a submodule
(done from the master repo, not here).
```
