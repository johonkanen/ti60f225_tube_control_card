# Next prompt

Ready-to-paste prompt for the next agent session. Replaced at the end of every session.

```
Proteus board /home/jari/dev/ti60f225_tube_control_card converted to KiCad 10: the conversion is
COMPLETE (Phases 0-5 done, 2026-11-20). This Ti60F225 card is NOT installed in the amplifier (the Agilex 3
card is), so the amplifier master repo does not add it as a submodule; the conversion is a reference and a
starting point only. There is no scheduled next step - do nothing unless the user asks for something.

State: 12 sheets, 146 parts, PCB with 3373 tracks / 240 vias / 20 zones, rebuilt byte-identically by
tools/make_pcb.sh (last step p2k place_refdes, Phase 5). tools/check_all.sh prints "ALL CHECKS PASSED"
(compare 146/146; ERC 0 / 14; make_pcb byte-identical; copper 307 groups 0 / 0 / 0 + 5 D1; DRC 83
violations: 0 shorts, 32 accepted courtyards, 28 silk_over_copper, 11 silk_overlap, 11 track_dangling,
1 via_dangling, + 5 D1 unconnected; ipc356_diff OK with 5 accepted D1 merges; check_drill_smaller exactly
J8-1..3; gerber round trip OK, track draws 2152 / 72 / 221 / 928; PDF reading: no difference).

Open, report only (redesign items, not conversion work; STATUS.md "Findings"):
- finding 1: D1 split terminals (J2, ISO5V, ISO_G, RS485A, RS485B: second pad has no copper to the first)
- finding 9: ADC1 VA / VIN swapped on the board
- finding 24: FLASH1 land pattern (kept as built in rev A)
- finding 25: J11 mirrored numbering (together with tube_hv_supplies J1)
- finding 26: dangling Proteus copper (11 track / 1 via, kept as built), 0.07 mm gaps
- 32 courtyard overlaps (Proteus placement) and 39 footprint body silk warnings (AD2, RS1, J1 guess,
  PWR1-3, U3 / U4 / V4, R2, V4); no reference is involved
- whether rev A stops being generated: the user's call at the first manual KiCad layout change (then
  record it in STATUS.md Decisions; make_pcb --check would fail from then on and must leave check_all.sh)

If the user asks for work: read PLAN.md, STATUS.md (phase table, "Phase 5", Decisions). Rules (PLAN.md
section 5): don't change tools/p2k or its pin (c5682dd); don't touch other repos; generate, don't hand-edit
(until the user decides otherwise); never use the no_connect pin type; temporary files in build/tmp; never
run the KiCad AppImage with --version (use tools/p2k/bin/kipy and tools/p2k/bin/kicad-cli). Negative-test
anything new; at the end tools/check_all.sh passing, STATUS.md / README updated, commit and push.
```
