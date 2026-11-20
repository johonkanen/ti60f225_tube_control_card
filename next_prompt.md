# Next prompt

Ready-to-paste prompt for the next agent session. Replaced at the end of every session.

```
Proteus board /home/jari/dev/ti60f225_tube_control_card converted to KiCad 10: the conversion is
COMPLETE (Phases 0-5 done, 2026-11-20), the user's design fixes of 2026-11-20 are done, the shared-tool
migration is done (tools/p2k a9a286c: every check on the shared proteus2kicad tools and p2k_config.py keys,
no board-local wrappers then - since H1 one, tools/hand_edits.py, p2k candidate 36 - and no strict-check opt-outs) and J11 has the standard 2x20 numbering (finding 25,
IPC_PIN_IDS, copper unchanged; tube_hv_supplies J1 renumbered the same way in its own repo). See STATUS.md
"Shared-tool migration 2026-11-20". This Ti60F225 card is NOT installed in the amplifier (the Agilex 3 card
is), so the amplifier master repo does not add it as a submodule; the conversion is a reference and a
starting point only. Finding 9 fixed (H1).

State: 12 sheets, 146 parts, PCB with 3350 tracks / 239 vias / 20 zones (generated up to 827b0b7, then H1). tools/check_all.sh prints "ALL CHECKS PASSED" (compare 146/146; ERC 0 /
14; check_pin_order 19 checks; copper 307 groups 0 / 0 / 0 + 5 SPLIT_PIN_MERGES opens;
DRC 71 violations: 0 shorts, 32 accepted courtyards, 28 silk_over_copper, 11 silk_overlap (DRC_EXPECTED_WARNINGS),
+ 5 D1 unconnected;
ipc356_diff OK (PHASE4_EXPECTED); gerber round trip OK (roundtrip_counts, F.Cu +3 TRACK_DELTA); PDF reading: no difference; test_no_connect OK).
Regression: ~/dev/proteus2kicad/tools/regress.sh fails here at its regenerate step by design since the
freeze (p2k candidate 35); run tools/check_all.sh on a clean clone instead.

Generation STOPPED (user decision 2026-11-20; last generated commit 827b0b7, freeze commit 1b33b3e; STATUS.md
"Generation stopped 2026-11-20"): the committed lib/ and kicad/ files are the source, generators frozen in
tools/generate/ (do not run; make_pcb.sh refuses), check_all.sh has no regenerate / byte-compare steps.
Hand edits since (STATUS.md "Hand edits after generation stopped", deviation list): H1 = finding 9 FIXED (ADC1 3V3 on
VA = pad A1, the R34 / C68 node Net-(ADC1-VIN) on VIN = pad COM2; 3350 tracks). The checks accept exactly the
recorded hand edits through tools/hand_edits.py (PIN_NETS / PIN_LABELS / AREAS / TRACK_DELTA); a new hand edit
adds its entries there (and to the deviation list) and negative-tests them. There is no scheduled next step -
do nothing unless the user asks for something.
Kept as built (no change): findings 1 (split terminals), 13, 23, 24, 10 (J8 value "1k").
Report only: the 0.07 mm gaps (finding 26), 32 courtyard overlaps and 39 footprint body silk warnings.

If the user asks for work: read PLAN.md, STATUS.md (phase table, "Hand edits after generation stopped",
"Generation stopped 2026-11-20", Decisions). Rules (PLAN.md section 5): don't change tools/p2k or its pin (a9a286c) unless the user /
coordinating session says so; don't touch other repos; generation has stopped: edit the committed files with
scripts in build/tmp and record every hand edit; never use the no_connect pin type; temporary files in build/tmp; never run the KiCad AppImage
with --version (use tools/p2k/bin/kipy and tools/p2k/bin/kicad-cli). Negative-test anything new; at the end
tools/check_all.sh passing,
STATUS.md / README updated, commit and push.
```
