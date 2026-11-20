# Conversion plan: Tube control card v2.5 (Ti60F225, `fpga_boardv2.5`)

Goal: redraw the Proteus schematic in KiCad 10 and rebuild the PCB from the Proteus Gerber X2
export, so that every pad, track, via and pour carries a net from the new schematic, and **prove
with scripted checks** that the KiCad design is electrically identical to the Proteus one. The
result is **rev A, the as-built baseline** for the redesign (see README.md).

This plan follows the generic playbook **`tools/p2k/CONVERSION_PLAYBOOK.md`** (read it first) and
lists only what is specific to this board. The finished reference is `~/dev/tube_psu_kicad`
(same proteus2kicad version, Phases 0-5 done): look at its `tools/`, `p2k_config.py`, PLAN.md and
STATUS.md for how each step was done.

**Order:** Independent of the 2010 boards: can run in parallel. The largest job (12 sheets, a 225-ball BGA): expect Phase 1 and Phase 2 to take the most sessions.

## 1. Inventory (measured in Phase 0, 2026-11-20; corrects the pre-check)

| Item | Value |
|---|---|
| Proteus project | `source/fpga_boardv2.5.pdsprj` (Proteus 8.12 SP2). `p2k.pdsprj.dsn_values` reads all 146 values; `lyt_parts` finds **no** layout records (this LYT has no `EID` markers, p2k candidate); `dsn_pinouts` reads 74 pinouts |
| Schematic PDF | `source/schematic_pdf/fpga_boardv2.5.PDF`, 12 pages, text layer kept. Title blocks have **no sheet names** (design title = file name, date 26/03/2025): names in `p2k_config.py` SHEETS describe the content. Every IPC refdes occurs in the PDF |
| CADCAM export | `source/cadcam/` Gerber X2 (`%FSLAX45Y45*%`, metric, no arcs, one `SameCoordinates` id), 14 gerbers + IPC, 2026-11-19 |
| Cross-check export | `source/cadcam_rs274x/` RS-274X + Excellon of 2025-03-22: copper, silk, paste, assembly, outline identical after normalising draw/contour direction; solder resist differs only in the arc resolution of rounded openings; Excellon = X2 drill gerber (377 hits 1:1); IPC identical except that 4 records (the SMD test pads) are at the end of the file |
| IPC netlist (the reference) | `source/cadcam/fpga_boardv2.5 - CADCAM Netlist.IPC`: **227 nets** (pre-check said 228), 1132 records, 147 refdes fields (146 parts + blank) |
| Copper layers | 4: Top Copper, Inner  1, Inner  2, Bottom Copper (READ-ME stack: 4 x 0.035 Cu, 0.3 prepreg / 1.6 core / 0.3 prepreg = 2.34 mm + resist) |
| Pours | Top: none. Inner 1: 2 regions + 183 clear holes; Inner 2: 3 + 147; Bottom: 15 + 133. No NonConductor draws. Each layer has the 5 Profile draws of the outline |
| Outline | 97.79 x 55.88 mm at (13.87, -42.75) (Mechanical 1, 5 draws: bottom edge in two pieces) |
| Parts (IPC refdes) | 146: 51 top SMD, 80 bottom SMD, 15 THT. No truncated refdes (FLASH1, RS485A, RS485B are full names), all usable in KiCad |
| Technology | SMD 755 records (557 top = 225 BGA balls + 328 pads + 4 test pads; 198 bottom), THT 377 records (133 component pads, 240 vias, 4 holes) |
| N/C pads | 76 (62 on U10, 14 elsewhere) |
| Vias | 240, all 0.419 / 0.2 mm, through, no stacked duplicates (`STACKED_VIAS = 0`) |
| SMD test pads | 4 SMD pads without refdes (0.711 mm, top) on JFET_6, JFET_5, GPIOL_10, GPIOL_11 |
| Drills | one plated drill gerber: 240 via 0.2, 133 component (0.558 x 102, 1.4 x 16, 1.016 x 8, 0.762 x 7), 4 OtherDrill 3.0 (mounting holes). No non-plated file |
| Mounting holes | 4 x 3.0 mm **plated**, no net, 6.35 mm copper on every layer, at (18, -39), (107, -39), (18, 9), (107, 9) = README.md "Mechanical baseline" |
| U10 (Ti60F225) | 225 balls A1..R15 (rows A-R without I, O; 15 x 15), **0.65 mm pitch**, 0.3 mm round SMD pads (aperture function `BGAPad,CuDef`), top, centre (37.023, -13.710). A1 at (41.573, -18.26): columns run to -x, rows to +y (IPC frame) = a standard A1-top-left footprint rotated 180 deg. No via-in-pad; 61 vias under the BGA area, 22 of them dog-bone vias on the interstitial grid. 62 balls N/C, only 12 GND balls |

## 2. Board-specific notes and expected pitfalls

- v2.5, built 2025; v1 (2024, same outline and holes) is not converted. `source/cadcam_rs274x/` is an earlier RS-274X export of the same version: cross-check only.
- `U10` is the Efinix Ti60F225 (225-ball BGA). The ball ids in the IPC are the Proteus pin ids: the symbol and footprint must use them (A1, B2, ...). Draw the FPGA as several symbol units (banks, power) and fit the BGA footprint to the IPC pads; check the ball pitch and the via-in-pad / dog-bone vias against the gerbers.
- Connectors: `J11` (40 pins, the HV supplies ribbon), `J7` (30), `J3`, `J6` (16), plus RS485 (`RS*`, isolated `ISO*`), flash, oscillator, ADC, regulators (`PWR*`).
- Single-pin parts (terminals, see below): `J2`, `J4`, `J5`, `J9` (power inputs), `ISO5V`, `ISO_G`, `RS485A`, `RS485B`.
- 248 IPC records without refdes = 240 vias + 4 mounting holes + 4 SMD test pads (Phase 0: no stacked duplicate vias). The test pads have no part: Phase 3 needs board-only SMD pads for them (p2k candidate).
- Two-pad terminals: `J2`, `J4`, `J5`, `J9`, `ISO5V`, `ISO_G`, `RS485A`, `RS485B` each have two 1.4 mm holes 5 mm apart, both pin 1. On five of them (`J2`, `ISO5V`, `ISO_G`, `RS485A`, `RS485B`) the two pads carry different IPC nets (`<net>.<id>`, STATUS.md findings): KiCad gives both pads one net, so Phase 1/3/4 must handle that difference explicitly (p2k candidate).
- The control card may later be replaced by an SoC card (CTRL-7 in the amplifier spec): this conversion is only the as-built baseline.

## 3. Phases

As in the playbook, section 3. Board-specific done criteria:

| Phase | Done when |
|---|---|
| 0 Skeleton and inventory | `p2k_config.py` complete (sheet names from the PDF title blocks, truncated-refdes table, KiCad refdes map, net aliases, expected IPC counts, layers, drills, outline); `p2k ipc356 --check` and `p2k check_sources` pass; `reference/` cheat sheets written; `tools/check_all.sh` runs; PLAN.md section 1 corrected with the measured inventory |
| 1 Schematic | all 146 parts drawn; `compare_netlists` 0 wrong-net pins, every IPC net complete; ERC 0 errors (warnings explained) |
| 2 Footprints | every part fits the IPC pads within 0.05 mm (`check_footprints`); pin-order oddities reported |
| 3 PCB | copper 0 shorts / 0 orphans / 0 opens after zone fill; DRC 0 shorts, 0 unconnected, 0 parity; remaining DRC items listed and justified; `make_pcb.sh --check` reproducible |
| 4 Verification | `gerber_roundtrip --check` and `ipc356_diff` pass and are in `check_all.sh`; every new check negative-tested; preferably a different session/model |
| 5 Clean-up | only the user's choices (pad sizes, silk, refdes positions) |

When all phases are done: STATUS.md says so, and the amplifier master repo can add this repo as a
submodule (that step is done from the master repo, not here).

## 4. Effort

The playbook's estimates are for a ~270-part, 4-layer, 11-sheet board. This board has
146 parts on 12 sheets and 4 copper layers: scale accordingly.

## 5. Rules for this conversion

Several board conversions run **in parallel**, each in its own repo and session. To keep them
independent:

1. **Don't change the shared tools** in `tools/p2k` (proteus2kicad), and don't move the submodule
   pin (c5682dd). If a tool can't handle something on this board, write a board-local script in
   `tools/` (or a config key the tool already has) and record it in STATUS.md under
   "p2k candidates", with what the shared tool would need. The tool changes are made later, in one
   place, with the ac_psu regression.
2. **Don't touch other repositories.** In particular not `~/dev/tube_amplifier_kicad` (the
   amplifier master repo: it adds this repo as a submodule once the conversion is verified) and not
   `~/dev/ac_psu_kicad` (another session's work in progress). `~/dev/tube_psu_kicad` is the
   finished reference: read it, don't change it.
3. **Reproduce Proteus.** Problems in the original design are reported in STATUS.md
   ("Findings"), not fixed. The redesign happens later, from this baseline.
4. **Generate, don't hand-edit** (playbook section 1): every file in `kicad/`, `lib/` and
   `reference/` is written by a script and is reproducible.
5. **Temporary files in `build/tmp/`** (git-ignored). Never run the KiCad AppImage with
   `--version` (it starts the GUI and hangs); use `tools/p2k/bin/kipy` and `tools/p2k/bin/kicad-cli`.
6. **Commit and push at the end of every phase** (and at the end of a session), with
   STATUS.md and next_prompt.md updated in the same commit.
7. **Ask the user** where the playbook says to (pad sizes when DRC forces them, Phase 5 choices,
   anything that changes the design).

## 6. Session protocol

- Start every session by reading PLAN.md, STATUS.md and `tools/p2k/CONVERSION_PLAYBOOK.md`, then
  run `tools/check_all.sh` (from Phase 0 on) and compare with the last result in STATUS.md.
- One session per phase (Phase 1 transcription may take several, a few sheets each).
- End every session with: `tools/check_all.sh` passing for everything done so far, STATUS.md
  updated (phase state, last check output, findings, p2k candidates, decisions), next_prompt.md
  replaced with the prompt for the next session, commit and push.
