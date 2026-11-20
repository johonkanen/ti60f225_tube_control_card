# Next prompt

Ready-to-paste prompt for the next agent session. Replaced at the end of every session.

```
Convert the Proteus board in /home/jari/dev/ti60f225_tube_control_card to KiCad 10: Phase 3, PCB.
Phases 0-2 are done: 12 sheets, 146/146 parts, full netlist comparison clean, ERC 0 errors; every
footprint fits its IPC pads (worst 0.030 mm, reports/footprint_fit.csv = the placement), pin order
checked (tools/check_pin_order.py).

Read, in this order: PLAN.md, STATUS.md (Phase 2 incl. "Pad sizes and drills" and "Open questions",
Phase 0 inventory and "U10 facts", findings 1, 4, 5, 24, 25, p2k candidates 1-3 and 19-23, decisions D1
and D2), tools/p2k/CONVERSION_PLAYBOOK.md (sections 1, 3 "Phase 3" and 5), tools/p2k/README.md (build_pcb,
gerber_to_tracks, assign_nets, pours_to_zones, check_board, drc, PCB_RULES, HOLE_/FREE_PAD_FOOTPRINT,
DRC_ACCEPTED), and as the worked example ~/dev/tube_psu_kicad/tools/make_pcb.sh with its STATUS.md
Phase 3 (read only; ~/dev/tube_hv_supplies_kicad and ~/dev/tube_power_amp_kicad may be further on, read
only). Run tools/check_all.sh first and compare with STATUS.md "Phase 2 verification".

Write tools/make_pcb.sh [--check] (build_pcb, gerber_to_tracks, assign_nets, pours_to_zones, zone fill,
assign_nets --check; --check rebuilds into a temporary directory with a copy of the .kicad_pro and
compares byte for byte) -> kicad/tube_control_card.kicad_pcb. Board specifics:
- PCB_RULES from the measured Proteus gaps (finding 4: different-net via-pad to BGA ball gaps down to
  0.075 mm, 0.088, 0.090; same-net vias overlap balls; vias 0.419 / 0.2 mm): measure the smallest
  track/track, track/pad, via/pad gaps and track widths on every copper layer with a script first and
  record them; clearance etc. follow the measurements (not KiCad defaults).
- PCB_THICKNESS (finding 5): the Proteus READ-ME stack gives 2.34 mm, probably the Proteus default.
  Ask the user (record in STATUS.md, stop if needed) unless an answer is in STATUS.md by then.
- The 4 plated mounting holes (HOLE_FOOTPRINT, set in p2k_config.py) and the 4 SMD test pads
  (FREE_PAD_FOOTPRINT = tube_control_card:TestPad_SMD_D0.711mm, an SMD footprint: p2k candidates 2 / 21).
  Check that build_pcb places the SMD pad on F.Cu with the IPC net; if a shared tool assumes THT free
  pads (build_pcb, gerber_to_tracks pad landing, check_board), write a board-local wrapper.
- p2k candidate 3: gerber_to_tracks raises on the BGAPad,CuDef aperture function (225 U10 balls):
  board-local wrapper (e.g. rename the function as tools/check_sources.py does), no change in tools/p2k.
- Decision D1 acceptance in check_board / assign_nets / DRC parity: the five split terminals (J2,
  ISO5V, ISO_G, RS485A, RS485B) have both pads on one KiCad net, while the IPC has two nets per pin
  (SPLIT_PIN_MERGES): accept exactly these five merges board-locally (as tools/compare_netlists.py does);
  any other difference must still fail. The copper of the "second" pads (5V.00301 ...) gets the kept net.
- Placement: footprint_fit.csv (J3 is a THT part on the bottom side; U10 at 180 deg; J11 is the
  rows-swapped header on top, finding 25).
- First DRC with the KiCad pads (FOOTPRINT_PAD_SIZES = "kicad"): list per refdes every short /
  clearance / mask-bridge / hole-clearance problem caused by KiCad pads larger than Proteus (likely:
  TSSOP 1.475 vs 1.1 mm pads, SOT-23-5/6, SC-70-6, the 1.0 mm pads of the 1.27 mm headers; BGA pads are
  smaller). Then STOP and ask the user which parts get the Proteus pads (record the question and the
  per-refdes table in STATUS.md, commit, push), unless STATUS.md already holds the answer; also the open
  J8 drill question (KiCad 1.0 < Proteus 1.016).
- Courtyard overlaps and silk warnings of a Proteus placement are expected: accept them in DRC_ACCEPTED
  with reasons.

Add make_pcb.sh --check, assign_nets --check, check_board (with the D1 wrapper) and drc to
tools/check_all.sh; negative-test each new check (a track moved, a via removed, a wrong net on a pad, a
D1 merge removed from the table) and record the results.

Rules (PLAN.md section 5): don't change tools/p2k or its pin (board-local workarounds, noted in
STATUS.md "p2k candidates"); don't touch other repos; report design findings, don't fix them;
generate, don't hand-edit; temporary files in build/tmp; never run the KiCad AppImage with --version
(use tools/p2k/bin/kipy and tools/p2k/bin/kicad-cli). The schematic and footprints must not change
unless a user decision says so (then re-run gen_footprints, make_sheets, check_footprints,
check_pin_order and the full compare). At the end: tools/check_all.sh passing, STATUS.md updated
(Phase 3 state, measured gaps and PCB_RULES, copper / DRC results, accepted DRC items with reasons,
check output, p2k candidates, decisions), README.md "Status" updated, next_prompt.md replaced with the
prompt for Phase 4 (independent verification: ipc356_diff, gerber_roundtrip with DRILL_EXCELLON, the
D1 and SMD-test-pad acceptance there), commit and push (git push origin main). If something needs a
user decision, stop, record it in STATUS.md, commit and push, and report it.
```
