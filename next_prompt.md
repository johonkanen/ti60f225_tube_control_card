# Next prompt

Ready-to-paste prompt for the next agent session. Replaced at the end of every session.

```
Proteus board /home/jari/dev/ti60f225_tube_control_card converted to KiCad 10: the conversion is
COMPLETE (Phases 0-5 done, 2026-11-20), and the user's design fixes of 2026-11-20 are done (STATUS.md
"Design fixes 2026-11-20"). This Ti60F225 card is NOT installed in the amplifier (the Agilex 3 card is), so
the amplifier master repo does not add it as a submodule; the conversion is a reference and a starting
point only. There is no scheduled next step - do nothing unless the user asks for something.

State: 12 sheets, 146 parts (AP61202 pin 6 = PG), PCB with 3347 tracks / 239 vias / 20 zones (26 dangling
Proteus draws and the GPIOL_N_10 via removed: REMOVED_TRACKS / REMOVED_VIAS in p2k_config.py), rebuilt
byte-identically by tools/make_pcb.sh. tools/check_all.sh prints "ALL CHECKS PASSED" (compare 146/146;
ERC 0 / 14; make_pcb byte-identical; copper 307 groups 0 / 0 / 0 + 5 D1; DRC 71 violations: 0 shorts,
32 accepted courtyards, 28 silk_over_copper, 11 silk_overlap, 0 dangling, + 5 D1 unconnected; ipc356_diff
OK, KiCad 1131 records / 239 vias, 1 via removed as recorded; check_drill_smaller exactly J8-1..3; gerber
round trip OK, track draws 2132 / 72 / 221 / 922; PDF reading: no difference).

Remaining (user decisions of 2026-11-20; STATUS.md "Decisions", "Design fixes"):
- finding 9 (ADC1 VA / VIN swapped on the board): a hand edit of the board, AFTER generation stops
- finding 25 (J11 mirrored numbering -> standard): waits for a new shared-tool pin-renumber key in
  tools/p2k (another session consolidates the shared tools); done together with tube_hv_supplies J1,
  never one end alone
- stopping generation of rev A: the user's call (then record it in STATUS.md Decisions; make_pcb --check
  leaves check_all.sh)
Kept as built (no change): findings 1 (split terminals), 13 (bias_feedback / biasfeedback separate), 23
(1V8 decoupling, redesign), 24 (FLASH1 land pattern), 10 (J8 value "1k": component values stay).
Report only: the 0.07 mm gaps (finding 26), 32 courtyard overlaps and 39 footprint body silk warnings;
p2k candidate 34 (removed_track direction; board-local patch 5 in tools/pcb_wrap.py).

If the user asks for work: read PLAN.md, STATUS.md (phase table, "Design fixes 2026-11-20", Decisions).
Rules (PLAN.md section 5): don't change tools/p2k or its pin (c5682dd) unless the user / coordinating
session says so; don't touch other repos; generate, don't hand-edit (until the user decides otherwise);
never use the no_connect pin type; temporary files in build/tmp; never run the KiCad AppImage with
--version (use tools/p2k/bin/kipy and tools/p2k/bin/kicad-cli). Negative-test anything new; at the end
tools/check_all.sh passing, STATUS.md / README updated, commit and push.
```
