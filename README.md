# ti60f225_tube_control_card

KiCad 10 migration of the tube control card with an Efinix Ti60F225 FPGA (channel switching, power scaling, bias control; Ethernet) of the tube amplifier, from Proteus. The schematic is redrawn from
the Proteus PDF and the PCB is rebuilt from the Gerber X2 export, so that every pad, track,
via and pour carries a net from the new schematic. The IPC-D-356A netlist of the CADCAM export
is the reference that every check compares against.

This is **rev A, the as-built baseline**. The redesign (ribbon cables, PCB-mount pots, the new
power section) starts from it. The amplifier project, its specification and the hardware state
are in [tube_amplifier_kicad](https://github.com/johonkanen/tube_amplifier_kicad). This card is not
installed in the amplifier, so the master repo does not include this repo as a submodule.

## Method

The shared [proteus2kicad](https://github.com/johonkanen/proteus2kicad) tools, a submodule in
`tools/p2k` (clone with `git clone --recurse-submodules`, or run `git submodule update --init`).
The phases and checks are in `tools/p2k/CONVERSION_PLAYBOOK.md`. Everything specific to this
board is in `p2k_config.py`.

## Status

Conversion plan: [PLAN.md](PLAN.md); progress: [STATUS.md](STATUS.md); prompt for the next agent session: [next_prompt.md](next_prompt.md).

Phase 0 (skeleton and inventory) and the Phase 1 preparation done: part map, symbol library
(U10 Ti60F225 as 8 units, pinout checked against Efinix), empty KiCad skeleton, netlist
comparison with decision D1 (split terminals drawn as one pin); `tools/check_all.sh` passes.
**Phase 1 (schematic) done**: all 12 sheets drawn by `tools/sheets/sheetNN.py` (146 of 146 parts, all
eight units of U10 with 62 no-connect flags); full netlist comparison against the IPC netlist: 0 missing
parts, 0 wrong-net pins, every net complete; ERC 0 errors, 14 explained warnings (single-pin nets);
decision D2 (no pin of type no_connect, ERC `no_connect_connected` fatal).
**Phase 2 (footprints) done**: `tools/gen_footprints.py` → `lib/footprint_map.csv` and
`lib/tube_control_card.pretty` (U10 = KiCad's TFBGA-225 P0.65 footprint unchanged, at 180 deg); all 146
parts fit their IPC pads within 0.030 mm (`p2k check_footprints --pcbnew`), pin order checked against the
unmoved KiCad footprints (`p2k check_pin_order`, `PIN_ORDER`). Results: ADC1 has VA / VIN swapped on the board
(finding 9 confirmed; fixed 2026-11-20 by hand edit H1); AP61202 pin 6 is PG, the sequencing is correct (finding 12 resolved); J11 is
numbered as a mirrored header like the HV board's J1, so the ribbon connects as drawn (finding 25; renumbered
to standard at both ends on 2026-11-20).
**Phase 3 (PCB) done**: `tools/make_pcb.sh` rebuilds
`kicad/tube_control_card.kicad_pcb` (4 layers, 1.6 mm, 3373 tracks, 240 vias, 20 zones, U10 BGA, SMD test
pads TP1-TP4) byte-identically; the Proteus copper is clean (0 shorts / 0 orphans / 0 opens besides the
five D1 split terminals), every pad / via / hole on its IPC position and net (`check_board`). Design rules
follow the measured Proteus copper (clearance 0.07 mm: 75 gaps under 0.1 mm on F.Cu, finding 26). Pad
decision (user, option A): the 15 parts whose KiCad pads reached Proteus tracks (TSSOP U1-U3 U5-U9 U11
U14, ADC1, U4, U12, headers J7 J11) have the Proteus pads; KiCad pads everywhere else. DRC: 0 shorts, 0
clearance, 0 mask bridges, 0 parity; only the accepted courtyard overlaps and the five D1 unconnected
items remain. `tools/check_all.sh`: ALL CHECKS PASSED.
**Phase 4 (independent verification) done** by a fresh session: KiCad's IPC-D-356 export matches the Proteus
netlist record for record (1132 / 1132; only the five D1 merges differ, accepted exactly), the gerber round
trip finds no copper difference on any of the 4 layers besides the decided KiCad pad shapes (pours
included; drills and the 2025 Excellon file 377 / 377), the only smaller drill is J8 (checked per pad), and
an independent reading of all 876 pins on the 12 PDF pages agrees with the IPC netlist and the KiCad
schematic (`tools/phase4_reading/`). 28 negative tests; finding 19 (level-shifter direction) resolved: no
problem. `tools/check_all.sh`: ALL CHECKS PASSED.
**Phase 5 (clean-up) done**, the user's choices: references placed clear of pads and silk by `p2k
place_refdes` (the last `make_pcb.sh` step; 13 dense passives get their reference on the Fab layer only);
dangling Proteus copper, the J1 body guess, the FLASH1 land pattern and all pad sizes / drills kept as built.
DRC warnings 370 → 83 (silk 326 → 39, none of them a reference); `tools/check_all.sh`: ALL CHECKS PASSED.
**The conversion is complete.** Rev A stays generated (`tools/make_pcb.sh`) until the user's first manual
layout change.
**Design fixes 2026-11-20** (user decisions; generators only, component values unchanged): AP61202 pin 6
renamed VOUT → PG (finding 12), the obsolete PDF sheet notes dropped (finding 6), the dangling Proteus
copper removed (finding 26: 26 draws `REMOVED_TRACKS` incl. the 56 mm GPIOL_N_18 stub, the lone GPIOL_N_10
via `REMOVED_VIAS`; 3347 tracks / 239 vias); DRC 83 → 71 violations, 0 dangling; `tools/check_all.sh`: ALL
CHECKS PASSED. Kept as built: findings 1, 13, 23, 24.
**Shared-tool migration 2026-11-20**: `tools/p2k` bumped to a9a286c and every board-local check wrapper
replaced by the shared proteus2kicad tools and `p2k_config.py` keys (`SPLIT_PIN_MERGES`, `SMD_FREE_PADS`,
`BGA_REFDES`, `PIN_ORDER`, `PHASE4_EXPECTED`, `DRILL_SMALLER` pad set, `ERC_FATAL_WARNINGS`, …); 14 board
tools deleted, generated files identical except the accepted report re-baselines; no strict-check opt-outs
Then **J11 renumbered to the standard 2x20 numbering** (finding 25, user decision, together with the HV
supplies J1 at the other end of the ribbon): `IPC_PIN_IDS` (old pin k → new k + 1 for odd k, k − 1 for even
k), the stock header footprint with its square pad on pin 1, copper unchanged (STATUS.md "Shared-tool
migration 2026-11-20"). `tools/check_all.sh`: ALL CHECKS PASSED.
**Generation stopped 2026-11-20** (user decision; last generated commit 827b0b7): the committed KiCad files
are the source now and are edited directly; the generators are frozen in `tools/generate/` (history, do not
run); `tools/check_all.sh` checks the committed files against the Proteus sources and the KiCad rules (no
regenerate / byte-compare steps).
**First hand edit (H1, 2026-11-20): finding 9 fixed** – ADC1 (ADC121C027) now has 3V3 on VA (pad A1 = SOT-23-6
pin 1) and the filtered BIASFEEDBACK node (R34 / C68) on VIN (pad COM2 = pin 3): the symbol's VA / VIN pins
exchanged in place with their datasheet pin types, on the board 5 F.Cu tracks moved, 5 removed and 8 added
around ADC1 (no via, no part moved); DRC unchanged (71 violations: 0 shorts, the accepted courtyards and D1
items). The checks accept exactly these two pin-net changes, the copper in a small area around ADC1 and the
+3 F.Cu track count (`tools/hand_edits.py`, STATUS.md "Hand edits after generation stopped"); ALL CHECKS PASSED.

Note: this Ti60F225 card is **not installed in the amplifier** (the Agilex 3 control card is). The
finished conversion is a reference and a starting point only.

v2.5, built 2025. `source/cadcam_rs274x/` is the earlier RS-274X export of the same version (cross-check only). v1 (built 2024, same outline and mounting holes) is not converted.

## Source

`fpga_boardv2.5.pdsprj` (Proteus 8.12). Exported 2026-11-19 from Proteus 8.12 SP2: schematic PDF, Gerber X2 CADCAM (metric)
with the IPC-D-356A netlist.

## Mechanical baseline

From the export (the fit reference for the redesign; the KiCad file is
`mechanical/tube_fpga_board_v2.5.kicad_pcb` in tube_amplifier_kicad):

```
outline: 97.79 x 55.88 mm, lower-left corner at (13.870, -42.750) in the Proteus frame
copper layers: 4; components: 146; mounting holes: 4
mounting holes (relative to the lower-left outline corner, mm):
  H1: x   93.130  y    3.750  drill 3.00 plated
  H2: x    4.130  y    3.750  drill 3.00 plated
  H3: x    4.130  y   51.750  drill 3.00 plated
  H4: x   93.130  y   51.750  drill 3.00 plated
```

## Layout

```
source/         Proteus exports (read-only)
  cadcam/         Gerber X2 export with the IPC-D-356A netlist (the reference)
  schematic_pdf/  schematic PDF to redraw from
  *.pdsprj        Proteus project (schematic values, devices, packages, pin names)
  cadcam_rs274x/  earlier RS-274X export (cross-check only)
reference/      tables derived from the IPC netlist (p2k ipc356; do not edit)
lib/            part_map.csv, tube_control_card.kicad_sym, footprints (generated until 2026-11-20, edited since)
kicad/          KiCad project: root sheet + one sheet per PDF page
tools/          board scripts: check_all.sh (every check, on the shared p2k tools), hand_edits.py (the recorded
                hand edits and the wrapper that accepts exactly them), test_no_connect.py, phase4_reading/
                (independent PDF transcript)
  generate/       FROZEN generators (generation stopped 2026-11-20; history, do not run): make_part_map.py,
                  gen_symbols.py, sheets/, gen_footprints.py, make_pcb.sh
tools/p2k/       proteus2kicad (submodule)
p2k_config.py   board configuration for the tools
```
