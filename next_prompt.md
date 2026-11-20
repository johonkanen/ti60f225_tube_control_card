# Next prompt

Ready-to-paste prompt for the next agent session. Replaced at the end of every session.

```
Convert the Proteus board in /home/jari/dev/ti60f225_tube_control_card to KiCad 10: finish Phase 3
(PCB) after the user's pad-size decision, then (if time allows, else in the next session) Phase 4.
Phases 0-2 are done; Phase 3 stopped on a user decision: the board is generated (tools/make_pcb.sh
through tools/pcb_wrap.py: build_pcb, gerber_to_tracks, assign_nets, pours_to_zones; 3373 tracks, 240
vias, 20 zones, 1.6 mm), the Proteus copper is clean (stage B 307 groups, 0 shorts / 0 orphans / 0
opens + 5 accepted D1 opens), check_board OK, make_pcb --check byte-identical, but the KiCad pads of
15 parts (U1 U2 U3 U5 U6 U7 U8 U9 U11 U14 ADC1 U4 U12 J7 J11) collide with Proteus copper (13 shorts,
85 clearance, 17 mask bridges, 2 hole clearance); tools/drc_check.py passes exactly those as PENDING.

Read, in this order: PLAN.md, STATUS.md (phase table, "Phase 3" - new files, steps, design rules,
"Phase 3 - pad sizes (OPEN USER DECISION)" with the per-refdes table and the tested options A / B,
remaining DRC items, negative tests -, findings 1, 4, 26, p2k candidates 1-3, 21, 24-28, Decisions),
tools/p2k/CONVERSION_PLAYBOOK.md (sections 1, 3 "Phase 3" / "Phase 4" and 5), tools/p2k/README.md
(ipc356_diff, gerber_roundtrip, DRILL_SMALLER, DRILL_EXCELLON). Reference (read only):
~/dev/tube_hv_supplies_kicad (commit 0186195: the applied pad decision, PROTEUS_PADS in
tools/gen_footprints.py, STATUS.md Phase 3) and ~/dev/tube_psu_kicad (Phase 4).

Start with tools/check_all.sh; it must print "ALL CHECKS PASSED, EXCEPT 2 PENDING USER DECISION(S)"
(compare 146/146, 0 wrong-net pins; ERC 0 / 14; check_footprints worst 0.030 mm; make_pcb
byte-identical; check_board OK; the two drc_check PENDING lines).

Then, with the user's answer to the pad question (record it in STATUS.md "Decisions" as a user
decision; if there is no answer in STATUS.md or in this prompt, ASK and stop):
- Apply it in tools/gen_footprints.py the way tools/pad_option_test.sh patches a scratch copy (a
  PROTEUS_PADS refdes set, refdes= rules before the general rule of each symbol, derived
  "<footprint>_ProteusPads" specs with ipc_sizes=True; drop a project spec no part uses any more),
  re-run gen_footprints, tools/make_sheets.sh (only Footprint fields may change: check git diff),
  ERC, the full compare, p2k.check_footprints --pcbnew, tools/check_pin_order.py (adapt its rule()
  lookups if a part moved to a _ProteusPads spec), tools/make_pcb.sh. Options A and B both gave DRC 0
  shorts / 0 clearance / 0 bridges / 0 hole clearance and copper 0 / 0 / 0 in the scratch test.
- Empty PENDING in tools/drc_check.py (keep its D1 acceptance: one unconnected item per D1 net) and
  remove tools/pad_option_test.sh (it patches the pre-decision gen_footprints.py; keep it in git
  history). Update the Phase 2 pad table / footprint notes.
- Negative-test the applied decision on a scratch copy (P2K_BOARD): one part back to the KiCad pads
  -> gen_footprints --check out of date, then DRC errors that drc_check rejects.
- STATUS.md: phase table (3 done), Phase 3 section (decision applied, results, DRC table without the
  pending rows), check output (ALL CHECKS PASSED), decisions; README status; commit and push.

Phase 4 (independent verification; preferably a different model/session): p2k ipc356_diff and
p2k gerber_roundtrip --check (with DRILL_EXCELLON, DRILL_SMALLER for J8) in tools/check_all.sh. Both will
need this board's acceptances board-locally (as tools/pcb_wrap.py does for Phase 3): the five D1
merges (pad nets compared by pad sets: the merged IPC nets join their kept nets, exactly
SPLIT_PIN_MERGES), the 4 SMD test pads (IPC free_pad records with is_tht False: SMD on top, no drill,
FREE_PAD_FOOTPRINT TP1-TP4), the U10 BGAPad,CuDef aperture function (gerber_roundtrip PAD_FUNCTIONS),
and KiCad's IPC-D-356 export of TP1-TP4 / the BGA. Negative-test every new check and record the results.

Still open and reported only (don't change without asking): findings 1 (D1), 9 (ADC1 VA / VIN), 19,
24 (FLASH1 land pattern), 25 (J11 mirrored numbering), 26 (sub-4-mil gaps, dangling copper).

Rules (PLAN.md section 5): don't change tools/p2k or its pin (c5682dd); board-local workarounds in
tools/, noted in STATUS.md "p2k candidates"; don't touch other repos; report design findings, don't
fix them; generate, don't hand-edit; never use the no_connect pin type; temporary files in build/tmp;
never run the KiCad AppImage with --version (use tools/p2k/bin/kipy and tools/p2k/bin/kicad-cli). At
the end: tools/check_all.sh passing, STATUS.md updated, next_prompt.md replaced with the prompt for
the next session, commit and push (git push origin main). If something needs a user decision, stop,
record it in STATUS.md, commit and push, and report it.
```
