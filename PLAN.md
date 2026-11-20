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

## 1. Inventory (pre-check 2026-11-20; Phase 0 confirms and corrects it)

| Item | Value |
|---|---|
| Proteus project | `source/fpga_boardv2.5.pdsprj` (values, devices, packages, pin names via `p2k.pdsprj`) |
| Schematic PDF | `source/schematic_pdf/fpga_boardv2.5.PDF`, 12 pages |
| CADCAM export | `source/cadcam/` (Gerber X2, metric, with the IPC-D-356A netlist) |
| IPC netlist (the reference) | `source/cadcam/fpga_boardv2.5 - CADCAM Netlist.IPC` |
| Copper layers | 4 (Top, Inner 1, Inner 2, Bottom) |
| Outline | 97.79 x 55.88 mm (Mechanical 1) |
| Parts (IPC refdes) | 146 |
| Nets (IPC) | 228 |
| Technology | mostly SMD (755 records) plus through-hole (377) |
| Mounting holes | 4 (3.0 mm plated; positions in README.md "Mechanical baseline") |

## 2. Board-specific notes and expected pitfalls

- v2.5, built 2025; v1 (2024, same outline and holes) is not converted. `source/cadcam_rs274x/` is an earlier RS-274X export of the same version: cross-check only.
- `U10` is the Efinix Ti60F225 (225-ball BGA). The ball ids in the IPC are the Proteus pin ids: the symbol and footprint must use them (A1, B2, ...). Draw the FPGA as several symbol units (banks, power) and fit the BGA footprint to the IPC pads; check the ball pitch and the via-in-pad / dog-bone vias against the gerbers.
- Connectors: `J11` (40 pins, the HV supplies ribbon), `J7` (30), `J3`, `J6` (16), plus RS485 (`RS*`, isolated `ISO*`), flash, oscillator, ADC, regulators (`PWR*`).
- Single-pad parts: `J2`, `J4`, `J5`, `J9` (power inputs), `ISO5V`, `ISO_G`, `RS485A`, `RS485B`.
- 248 IPC records without refdes (vias): many, check stacked duplicates (`STACKED_VIAS`) as in tube_psu.
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
