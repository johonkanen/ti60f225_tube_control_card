# Status: Tube control card v2.5 (Ti60F225, `fpga_boardv2.5`)

Plan: [PLAN.md](PLAN.md). Playbook: `tools/p2k/CONVERSION_PLAYBOOK.md`.

| Phase | State |
|---|---|
| 0 Skeleton and inventory | **done** 2026-11-20 (Opus 5.5) |
| 1 Schematic | **done** 2026-11-20: preparation (Opus 5.5), transcription sessions T1, T2, T3 (Fable 5.2): 12 sheets, 146 of 146 parts, full netlist comparison clean, ERC 0 errors |
| 2 Footprints | **done** 2026-11-20 (Opus 5.5): 146/146 parts fit the IPC pads (worst 0.030 mm), pin order checked, findings 9 and 12 answered |
| 3 PCB | not started |
| 4 Verification | not started |
| 5 Clean-up | not started |

## Phase 2 – done (Opus 5.5, 2026-11-20)

New (all generated; the `--check` steps are in `tools/check_all.sh`):

- **`tools/gen_footprints.py`** (RULES + PROJECT of this board, shared code `p2k.footprints`) →
  **`lib/footprint_map.csv`** (146 parts, 28 footprints) and **`lib/tube_control_card.pretty`** (15
  project footprints: 10 derived from KiCad footprints, 3 built from the IPC pads, 2 board-only), plus
  **`kicad/fp-lib-table`** (board-local helper as on tube_hv_supplies: `footprints.run` does not write
  it, p2k candidate 22). The board-only **SMD test pad** (`TestPad_SMD_D0.711mm`, F.Cu + F.Mask, pad 1)
  is built board-locally: `gen_footprints.py` wraps `footprints.build_library` for specs with
  `smd_pad=` (`footprints.single_pad` makes THT pads only, p2k candidate 2/21), so `run()` writes it and
  `--check` verifies it like every other footprint.
- **`p2k_config.py`**: `FOOTPRINT_PAD_SIZES = "kicad"`; for Phase 3 `HOLE_FOOTPRINT` =
  `tube_control_card:MountingHole_3.0mm_PTH_Pad6.35mm` (plated 3.0 mm, 6.35 mm pad on `*.Cu`, no net),
  `FREE_PAD_FOOTPRINT` = `tube_control_card:TestPad_SMD_D0.711mm` (prefix `TP`). Whether
  `p2k.build_pcb` places an SMD footprint at the four `free_pad` records correctly (net, top side) is a
  Phase 3 check.
- The 12 sheet scripts re-run (`tools/make_sheets.sh`): **only the Footprint fields changed** (193
  lines, checked with `git diff`: no other line); `make_sheets --check`, ERC (0 errors, 14 warnings) and
  the full compare (0 wrong-net pins, 298/298 nets complete) unchanged. gen_symbols / check_symbols /
  test_no_connect not affected (no symbol change).
- **`tools/check_pin_order.py`** (board-local, after tube_hv_supplies'): the **unmoved** KiCad base
  footprints with the Proteus renumbering fitted onto the IPC pads, both mirror states; every footprint
  is taken **from `gen_footprints.RULES` / `PROJECT`** (`rule()`), so a changed renumbering or rule fails
  here even though `check_footprints` passes (negative tests T3, T4). New against the HV version: an
  expected fit **angle** (U10 must fit at 180 deg, else the A1 corner of the footprint graphics is wrong,
  T4). `--render` draws the fitted KiCad graphics over the Proteus silk / assembly of the part's side
  (`reports/pin_order/<refdes>.png`, git-ignored; 19 parts compared by eye).
- **`reports/footprint_fit.csv`** (placement input for Phase 3) and `reports/footprint_pads.csv`.

### Footprints and fit (`p2k check_footprints --pcbnew`)

**146/146 parts fitted, 884 pads, 28 footprints, worst residual 0.030 mm (limit 0.05); pcbnew placement
of 146 parts, worst pad offset 0.030 mm.** One note: `J3: THT pad pattern fits only mirrored -> bottom
side` – correct, J3 is drawn on the Proteus **bottom** assembly layer (render). All 80 bottom SMD parts
fit mirrored; every other THT part fits on top.

| Footprint | Parts | Max res. mm | IPC pattern / why |
|---|---|---|---|
| `Package_BGA:TFBGA-225_10x10mm_Layout15x15_P0.65mm` | U10 | **0.000** | KiCad footprint unchanged (its descr cites the Efinix Titanium packaging guide): pad names A1..R15 (no I, O) = the IPC ball ids = the symbol pins; placed at **180 deg** (A1 at IPC (41.573, -18.26)); KiCad pads 0.28 mm (Proteus 0.30), NSMD mask margin 0.075 |
| `Package_SO:TSSOP-24_4.4x7.8mm_P0.65mm` | U1 U2 U7 U8 U9 | 0.013 | unchanged |
| `Package_SO:TSSOP-16_4.4x5mm_P0.65mm` | U3 (bottom) | 0.013 | unchanged |
| `tube_control_card:TSSOP-14_4.4x5mm_P0.65mm_Proteus` | U5 U6 U11 U14 | 0.000 | rows 5.85 (KiCad 5.725 = 0.063 off): derived, pads moved |
| `tube_control_card:SOT-23-5_Proteus` | U4 V4 (bottom) | 0.000 | rows 2.39 (KiCad 2.30, 0.068 off) |
| `tube_control_card:SOT-23-6_ADC121C027_Proteus` | ADC1 | 0.000 | KiCad pads 1-6 → A1 A2 COM2 K2 K1 COM1 (as tube_hv_supplies), rows 2.65 (KiCad 2.275) |
| `tube_control_card:SOT-363_SC-70-6_Proteus` | U12 | 0.000 | rows 1.80 (KiCad 1.675, 0.063 off) |
| `tube_control_card:SOT-563_Proteus` | PWR1 PWR2 PWR3 (bottom) | 0.000 | rows 1.27 (KiCad 1.425, 0.078 off) |
| `tube_control_card:Texas_X2QFN-8_RUG_1.5x1.5mm_P0.5mm` | AD2 (bottom) | 0.000 | KiCad has no TI RUG: built from the IPC pads (Proteus pad sizes, body 1.5 x 1.5) |
| `tube_control_card:Oscillator_SMD_2.0x1.6mm_Proteus` | OSC1 | 0.000 | from the SiT 2.0 x 1.6 PQFN-4, pads moved to 1.8 x 1.2 (KiCad 1.5 x 1.1) |
| `tube_control_card:SOIC-8_7.5x5.85mm_P1.27mm_Proteus` | RS1 | 0.000 | Proteus `SO8W`, pad rows **9.14** (KiCad wide SOIC-8 10.65) |
| `tube_control_card:SOIC-8_5.3x5.3mm_P1.27mm_Proteus` | FLASH1 | 0.000 | 208 mil SOIC-8 (W25Q64JW**SS**) on the same Proteus `SO8W` pattern, rows 9.14 (KiCad 7.175): finding 24 |
| `tube_control_card:R_Array_Convex_4x0402_Proteus` | R14 R15 R17 R18 R22-R25 | 0.000 | ROHM MNR04 style, rows 0.95 (KiCad 1.0, 0.056 off) |
| `Resistor_SMD:R_0201_0603Metric` | R11 R32 R35-R40 (bottom) | 0.030 | Proteus `CAPC0603X33` (0201), 0.70 apart |
| `Resistor_SMD:R_0402_1005Metric` | 29 (R1-R10, R12, R13, R16, R19-R21, R26-R31, R33, R34, R41-R44, R59) | 0.010 | RESC1005X40 |
| `Resistor_SMD:R_1206_3216Metric_Pad1.30x1.75mm_HandSolder` | R67 R68 R69 | 0.025 | 1206, 3.15 apart (plain R_1206 0.112 off) |
| `Capacitor_SMD:C_0201_0603Metric` | C21-C25 C29 C30 C33 C36 C40 (bottom) | 0.030 | CAPC0603X33 |
| `Capacitor_SMD:C_0402_1005Metric` | 40 | 0.030 | CAPC1005X55 |
| `Capacitor_SMD:C_0603_1608Metric` | C19 C20 C51 C53 C54 | 0.025 | CAPC1608X87 |
| `Capacitor_SMD:C_1206_3216Metric` | C55 C58 | 0.025 | CAPC3216X140 |
| `Inductor_SMD:L_0805_2012Metric` | L1 L3 L4 L5 (bottom) | 0.025 | IND805 |
| `tube_control_card:PinHeader_2x20_P1.27mm_Vertical_RowsSwapped` | J11 | 0.000 | KiCad 2x20 1.27 mm header, odd / even pad numbers swapped (finding 25); pins 37 / 38 N/C |
| `Connector_PinHeader_1.27mm:PinHeader_2x15_P1.27mm_Vertical` | J7 | 0.000 | standard numbering, top |
| `Connector_PinHeader_1.27mm:PinHeader_2x08_P1.27mm_Vertical` | J3 (**bottom**), J6 | 0.000 | standard numbering |
| `Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical` | J8 | 0.000 | CON3_1X3_U_FCI |
| `TerminalBlock_Phoenix:TerminalBlock_Phoenix_MPT-0,5-5-2.54_1x05_P2.54mm_Horizontal` | J1 | 0.000 | TBLOCK-I5, P2.54 (JTAG); see "open questions" |
| `tube_control_card:Converter_IZB03_SIP7` | PWR4 | 0.000 | built from the IPC pads: 7 pins at 2.54, pin 4 position empty (gap 5.08 between pins 3 and 4) |
| `tube_control_card:Terminal_2x1_P5.00mm_D2.0mm_Drill1.4mm` | J2 J4 J5 J9 ISO5V ISO_G RS485A RS485B | 0.000 | from the IPC pads (J2): two 1.4 mm holes 5 mm apart, **both pad 1** (D1) |
| `tube_control_card:MountingHole_3.0mm_PTH_Pad6.35mm` | (board-only, Phase 3 H1-H4) | | plated 3.0 mm, 6.35 mm pad, every copper layer, no net |
| `tube_control_card:TestPad_SMD_D0.711mm` | (board-only, Phase 3 TP1-TP4) | | 0.711 mm round SMD pad, top (SMD_FREE_PADS) |

**D1 terminals in check_footprints:** the five split terminals need nothing board-local here:
`fpgeom.ipc_pads_by_refdes` keeps both IPC records of pin 1 (one per net) and `fpgeom.fit` pairs pads
that share a number by trying the permutations, so both pads of J2, ISO5V, ISO_G, RS485A and RS485B are
fitted (884 pads = all IPC component pads; residual 0.000). The nets of the two pads are not compared by
this check; the D1 acceptance is needed in the Phase 3-4 net checks (p2k candidate 1).

### Pin order (`tools/check_pin_order.py`)

| Check | Unmoved KiCad base | Unmirrored | Mirrored | Result |
|---|---|---|---|---|
| U10 | TFBGA-225 P0.65 | **0.000 @ 180** | 9.795 | ball ids = KiCad pad names; A1-top-left footprint at 180 deg. The Proteus top silk has a dot next to ball A1, where the KiCad A1 corner mark lands (render) |
| ADC1, A1 A2 COM2 K2 K1 COM1 = 1-6 | SOT-23-6 | **0.188** (rows) | 1.909 | fits on top |
| ADC1, COM2 on 1 / A1 on 3 (datasheet wiring) | SOT-23-6 | 1.909 | 0.188 | fits only mirrored: impossible on a top part |
| U4 V4 (bottom) | SOT-23-5 | 1.906 | **0.068** | chirality right for a bottom part |
| U12 | SOT-363 SC-70-6 | **0.063** | 1.302 | top |
| PWR1-3 (bottom) | SOT-563 | 1.003 | **0.078** | bottom |
| U5 U6 U11 U14 | TSSOP-14 | **0.063** | 3.901 | top |
| U1 U2 U7 U8 U9 | TSSOP-24 | **0.013** | 7.150 | top |
| U3 (bottom) | TSSOP-16 | 4.550 | **0.013** | bottom |
| R14 ... R25 | R_Array_Convex_4x0402 | **0.056** | 0.976 | top |
| OSC1 | SiT PQFN-4 2.0x1.6 | **0.150** | 1.209 | top (pads 1 EN, 2 GND, 3 OUT, 4 VCC counter-clockwise from the top, as the MC2016) |
| RS1 / FLASH1 | SOIC-8 wide / 208 mil | **0.753 / 0.985** (rows) | 3.88 / 3.94 | top |
| J11, KiCad numbering | PinHeader_2x20_P1.27mm | 1.270 | **0.000** | fits only mirrored, but J11 is a top part (finding 25) |
| J11, odd / even swapped | PinHeader_2x20_P1.27mm | **0.000** | 1.270 | the footprint used |
| J3 | PinHeader_2x08_P1.27mm | 1.270 | **0.000** | standard numbering on a **bottom** part (Proteus bottom assembly outline + "J3") |
| J6 / J7 | PinHeader 2x08 / 2x15 | **0.000** | 1.270 | standard, top |
| J1 / J8 | MPT 1x05 / PinHeader 1x03 | 0.000 | 0.000 | inline (symmetric) |

Without a KiCad base (built from the IPC pads, so the pad ids are the IPC's by construction): AD2
(X2QFN-8, bottom: pads 1-3 / 4 / 5-7 / 8 run counter-clockwise seen from below = JEDEC order for a
bottom part; pin 8 AINM on GND, 6 AVDD on #00427 behind L3, 4 DVDD on 1V8, as finding 17), PWR4 (inline),
the blade terminals. The dual-row SMD patterns are symmetric under 180 deg, so the geometry confirms the
chirality, and the pin-1 end follows from the nets checked in Phase 1 (supply / GND pins on the
datasheet pads).

- **Finding 9 – ADC1 (ADC121C027): reproduced exactly and confirmed** (same result as tube_hv_supplies
  finding 6). The project footprint's pads are the IPC pads; the chirality test puts A1-A2-COM2-K2-K1-COM1
  counter-clockwise from the top = JEDEC 1-6. With A1 = pad 4 instead, GND would be on SCL, so:

  | SOT-23-6 pad | Proteus id | IPC position | ADC121C027 datasheet pin | IPC net on the board |
  |---|---|---|---|---|
  | 1 | A1 | (99.30, -22.10) | **VA** (supply, reference) | **#00660** = filtered BIASFEEDBACK (R34 / C68) |
  | 2 | A2 | (99.30, -21.15) | GND | GND |
  | 3 | COM2 | (99.30, -20.20) | **VIN** (analog input) | **3V3** |
  | 4 | K2 | (96.65, -20.20) | ADR0 | N/C (floating = one of the three address states) |
  | 5 | K1 | (96.65, -21.15) | SCL | GPIOR_22 |
  | 6 | COM1 | (96.65, -22.10) | SDA | GPIOR_28 |

  So on the built board **3V3 is on the input pin VIN and the filtered bias-feedback signal on the
  supply pin VA**: VA / VIN are swapped (unless the board was reworked). The KiCad pin-1 mark lands at
  A1; the Proteus silk / assembly have no pin-1 mark.
- **Finding 12 – AP61202 pin 6: resolved.** Diodes datasheet DS44251 (AP61200/1/2/3, "Pin
  Descriptions"): SOT563 pin 1 FB, 2 GND, 3 VIN, 4 SW, 5 EN, **6 = OUT on AP61200/AP61201, PG
  (open-drain power good, internal 5 MΩ pull-up to VIN, max 6.0 V) on AP61202/AP61203**. The Proteus ids
  1-6 are the datasheet pins (chirality: fits mirrored on the bottom parts, 0.078; pin 1 FB on the
  divider #00148 of PWR2, 2 GND, 3 5V, 4 SW node, 5 EN on 5V). So PWR2 pin 6 is PG and drives 1V_ENABLE
  (R1 10k to 5V, within the 6.0 V PG rating) = the EN pins of PWR1 / PWR3: a correct power-good
  sequencing (1V core first, then 1V8 / 3V3). Only the Proteus pin **name** "VOUT" is wrong (the
  AP61200 name); PG is N/C on PWR1 / PWR3.
- **J11 (ribbon to the HV supplies board): numbered as the MIRROR of a standard 2x20 header, mounted on
  top** – exactly like tube_hv_supplies J1 (its finding 12), the other end of the ribbon. See finding 25.

### Pad sizes and drills vs Proteus (OPEN USER DECISION, Phase 3 / 4)

`FOOTPRINT_PAD_SIZES = "kicad"`: KiCad pad sizes and drills everywhere except the footprints built
from the IPC pads (terminals, IZB03, X2QFN-8, test pad). Per refdes (`reports/footprint_pads.csv`,
IPC size → KiCad size as written in the files, not rotated):

| Parts | Proteus pad | KiCad pad | Proteus drill | KiCad drill |
|---|---|---|---|---|
| U10 | 0.30 round | 0.28 round (NSMD, mask +0.075) | | |
| J11 J7 J3 J6 | 0.812 round | 1.0 | 0.558 | 0.65 (larger); gap between KiCad pads at 1.27 mm pitch 0.27 (Proteus 0.458) |
| J8 | 2.032 | 1.7 (pad 1 square) | 1.016 | **1.0 (smaller: needs a `DRILL_SMALLER` entry or the Proteus pads)** |
| J1 | 2.032 | 2.2 | 1.016 | 1.1 (larger) |
| PWR4, J2 J4 J5 J9 ISO5V ISO_G RS485A RS485B | 1.27 / 2.0 | same | 0.762 / 1.4 | same |
| U1 U2 U7 U8 U9, U3, U5 U6 U11 U14 | 0.4 x 1.1 | 0.4 x 1.475 | | |
| U4 V4 | 0.508 x 0.635 | 0.6 x 1.325 | | |
| ADC1 | 0.5 x 0.65 | 0.6 x 1.325 | | |
| U12 | 0.35 x 0.5 | 0.35 x 1.025 | | |
| PWR1 PWR2 PWR3 | 0.3 x 0.67 | 0.35 x 0.675 | | |
| RS1 | 0.635 x 2.032 | 0.6 x 1.8 | | |
| FLASH1 | 0.635 x 2.032 | 0.65 x 1.625 | | |
| OSC1 | 0.8 x 0.6 | 0.9 x 0.8 (long axis turned 90 deg against Proteus) | | |
| R14 R15 R17 R18 R22-R25 | 0.4 / 0.3 x 0.5 | 0.5 x 0.4 / 0.3 (same) | | |
| R67 R68 R69 | 1.016 x 1.524 | 1.3 x 1.75 | | |
| L1 L3 L4 L5 | 1.016 x 1.524 | 0.875 x 1.2 (smaller) | | |
| C55 C58 | 1.143 x 1.803 | 1.15 x 1.8 | | |
| C19 C20 C51 C53 C54 | 0.939 x 0.99 | 0.9 x 0.95 | | |
| 40 0402 capacitors | 0.609 round | 0.56 x 0.62 | | |
| 29 0402 resistors | 0.558 x 0.609 | 0.54 x 0.64 | | |
| 10 0201 capacitors, 8 0201 resistors | 0.406 x 0.457 | 0.46 x 0.4 | | |
| AD2 | 0.3 x 0.6, 0.55 x 0.2 / 0.25 | same (built from the IPC) | | |

Likely Phase 3 DRC trouble spots (to be measured there, not decided now): the KiCad pads that are
**much longer** than the Proteus pads – TSSOP (1.475 vs 1.1), SOT-23-5 / SOT-23-6 (1.325 vs 0.635),
SC-70-6 (1.025 vs 0.5) – reach Proteus tracks / vias between and beyond the pad rows; the 1.0 mm
header pads at 1.27 mm pitch (0.27 mm between pads, Proteus tracks between header pins?); the BGA
needs nothing larger (KiCad 0.28 pads make finding 4's gaps 0.010 mm wider: 0.075 → 0.085 mm, still
far below any normal clearance, so `PCB_RULES.clearance` has to follow the measured Proteus gaps).
Switching parts to the Proteus pads (`refdes=` rules with `ipc_sizes`, as tube_psu did) is the user's
call after the Phase 3 DRC.

### Open questions for the user (not blocking Phase 3)

1. **Pad sizes** (table above): KiCad pads kept; which parts switch to the Proteus pads follows from the
   Phase 3 DRC (record per refdes then).
2. **J8 drill:** the KiCad 1x03 header has a 1.0 mm drill, Proteus 1.016 (the only KiCad drill smaller
   than Proteus). Accept it (`DRILL_SMALLER = {(1.016, 1.0): ...}` for Phase 4) or give J8 the Proteus
   pads / drill.
3. **J1 (JTAG, Proteus "TBLOCK-I5 / 5 PIN TERMINAL BLOCK"):** the Proteus outline is a 14 x 3.1 mm
   rectangle centred on the pins (a pin-header-like body), so the KiCad Phoenix MPT terminal block
   (6.2 mm deep) is a guess; a 1x05 2.54 mm pin header would match the outline better (but has a 1.0 mm
   drill). Phase 5 choice; the copper is the same either way.
4. **FLASH1** (finding 24): reproduced on the Proteus SO8W pad rows; nothing to decide for rev A.

### Negative tests (scratch copy `build/tmp/neg`, `P2K_BOARD`, script `build/tmp/negtest.sh`, not committed)

- **T1 a pad moved 0.06 mm** (J11 project footprint, pad 7, x + 0.06 in the .kicad_mod) →
  `gen_footprints --check` "out of date: …RowsSwapped.kicad_mod"; check_footprints "J11 … residual
  0.059 mm (pad 7 0.059 …)" and "J11: pcbnew placement off by 0.059 mm", FAILED.
- **T2 swapped pad numbers in a footprint file** (TSSOP-14 project footprint, pads 3 / 4) →
  gen_footprints out of date; check_footprints "U5 … residual 0.650 mm (pad 4 0.650, pad 3 0.650)" (and
  U6, U11, U14), FAILED.
- **T3 swapped renumbering in `gen_footprints.py`** (ADC A1 ↔ COM2) and regenerated → gen_footprints
  up to date, **check_footprints passes** (`derive` moves the pads onto the IPC positions),
  `check_pin_order` "ADC1: unmirrored 1.909, expected unmirrored <= 0.19", FAILED.
- **T4 wrong rotation** (U10 as a project footprint derived from the KiCad BGA with the ball ids turned
  by 90 deg) and regenerated → gen_footprints up to date, check_footprints passes (the ids land on the
  right IPC pads, only the footprint's A1 corner / outline is turned), `check_pin_order` "U10 BGA:
  unmirrored 0.000 @90 deg, expected unmirrored <= 0.001 @180 deg", FAILED (the angle check is new for
  this reason).
- T5 a rule note edited without regenerating → gen_footprints "out of date: lib/footprint_map.csv".

### Phase 2 verification (`tools/check_all.sh`)

```
(KiCad environment, IPC self-check, X2 vs IPC: unchanged, see Phase 0)
(Part map, symbol library, symbol pin sets, sheets up to date: unchanged)
== ERC
erc: 0 errors, 14 warnings (14 isolated_pin_label) (reports/erc.rpt)
== Netlist comparison vs IPC (D1 merges accepted)
compare: parts 146/146 present, 0 missing, 0 extra; pins compared 876, wrong-net pins 0; IPC nets touched 298, complete 298
compare: OK
== Footprint library, map and fp-lib-table up to date
gen_footprints: 146 parts, 28 footprints (15 project), up to date
== Footprints vs IPC pad geometry (fit and pcbnew placement)
check_footprints: pcbnew placement of 146 parts, worst pad offset 0.030 mm
check_footprints: note: J3: THT pad pattern fits only mirrored -> bottom side
check_footprints: 146/146 parts fitted, 884 pads, 28 footprints, worst residual 0.030 mm (limit 0.05)
check_footprints: OK
== Pin order vs unmoved KiCad base footprints
(table above)
check_pin_order: OK (results as recorded in STATUS.md)

ALL CHECKS PASSED
```

## Phase 0 – done (Opus 5.5)

- Inventory measured and written into PLAN.md section 1 (the pre-check had 228 nets: the IPC
  declares **227**; everything else confirmed, details added: pours, drills, BGA, test pads).
- **Sources cross-checked:** the RS-274X export (`source/cadcam_rs274x/`, 2025-03-22) is the
  same design as the X2 export (2026-11-19): copper, silk, paste, assembly and outline gerbers
  identical after normalising the direction of draws and region contours; solder resist differs
  only in the arc resolution of rounded openings (60 flashes); Excellon drill = X2 drill gerber
  (377 hits 1:1, `DRILL_EXCELLON` set for Phase 4). The two IPC files have identical records;
  only the 4 SMD test-pad records sit at a different place (after the vias in X2, at the end in
  RS-274X).
- **PDF:** 12 pages rendered with `pdftoppm -r 200 -png source/schematic_pdf/fpga_boardv2.5.PDF
  build/tmp/pdf/hi` (`build/tmp/pdf/hi-NN.png`, git-ignored; re-run the command when needed).
  The title blocks carry **no sheet name** (design title = `fpga_boardv2.5.pdsprj`, date
  26/03/2025, "page n of 12"), so the SHEETS names describe the page content:
  1 Net aliases and power inputs, 2 FPGA configuration and clock, 3 Regulators,
  4 Level shifters, 5 FPGA IO banks, 6 FPGA power, 7 ADC multiplexer,
  8 Power stage connector J11, 9 JFET drivers 1-12, 10 Connectors and bias ADC,
  11 Bias DAC and RS485, 12 JFET drivers 13-16.
- **p2k_config.py** complete for Phase 0: SHEETS, empty `TRUNCATED_REFDES` / `KICAD_REFDES`
  (no truncated refdes: FLASH1, RS485A, RS485B are the full PDF names; every refdes is
  KiCad-usable; all 146 IPC refdes occur in the PDF), `NET_ALIASES` (`GND=POWER` → GND,
  `VCC/VDD=POWER` → AD_3V3, `5V.00026` → 5V, `ISO5V.00255` → ISO5V, `RS485_GND.00256` →
  RS485_GND), `VIA_DRILLS` 0.2, holes 3.0 plated, `EXPECTED_IPC`, `STACKED_VIAS = 0`, COPPER
  (Top Copper / Inner  1 / Inner  2 / Bottom Copper), plated drill gerber only, outline
  (13.87, -42.75, 97.79, 55.88), plus the board-local keys `SPLIT_PIN_NETS` and
  `SMD_FREE_PADS` (see p2k candidates).
- `p2k ipc356` wrote `reference/` (ipc356_pads.json/csv, pin_nets_by_component.md,
  pins_by_net.md).
- `p2k ipc356 --check` and `p2k check_sources` **fail on this board for tool reasons only**
  (5 split terminal pins + 4 SMD test pads in ipc356; 225 `BGAPad` flashes + the 4 test pads
  as OtherPad/OtherDrill in check_sources). Board-local wrappers `tools/ipc356_check.py` and
  `tools/check_sources.py` run the shared checks and accept exactly these (from the config
  tables); the BGA wrapper also checks that the 225 BGAPad flashes are the 225 U10 balls.
  Negative-tested: a test pad moved 0.05 mm, a wrong split-net entry, a wrong via count, the
  outline moved 0.1 mm, U10-H8 moved 0.05 mm in the reference table – each fails.
- `tools/check_all.sh`: KiCad environment, IPC self-check, X2 vs IPC.

### U10 (Efinix Ti60F225) facts for Phases 1-2

- 225 balls, ids A1..R15 (rows A B C D E F G H J K L M N P R, columns 1-15), the Proteus pin
  ids = JEDEC ball names. Pitch **0.65 mm**, pads 0.3 mm round, top side, centre
  (37.023, -13.710) in the IPC frame.
- A1 at (41.573, -18.26): column numbers increase towards -x, row letters towards +y (IPC,
  Y up) = a standard A1-top-left KiCad BGA footprint rotated by 180 deg (no mirror).
- 62 balls N/C, 12 GND, 12 1V, 20 1V8, 4 3V3 (VCCIO33), the rest single signals. The PDF
  draws U10 as units A-H (A config/JTAG p2, C bank L p2, B/D/E/F IO banks p5, G power + H GND
  p6).
- No via-in-pad. 61 vias lie under the BGA, 22 of them dog-bone vias on the interstitial grid.

### Phase 0 verification (`tools/check_all.sh`)

```
== KiCad environment
pcbnew 10.0.7
== IPC-D-356A parser self-check (p2k ipc356 --check + board exceptions)
ipc356: nets=227, records=1132, refdes_raw=147, tht_records=377, smd_records=755, smd_top=557, smd_bottom=198, nc_pads=76, vias=240, free_pads=4, holes=4, parts=146
  accepted (board-local): 5 two-pad pins on split nets (SPLIT_PIN_NETS): ISO5V-1, ISO_G-1, J2-1, RS485A-1, RS485B-1
  accepted (board-local): 4 SMD test pads without refdes (SMD_FREE_PADS)
ipc356: OK
== Gerber X2 export vs IPC (p2k check_sources + board exceptions)
  14 gerbers, one SameCoordinates id
  Top Copper: Draw:Conductor 2152, Draw:Profile 5, Flash:ComponentPad 133, Flash:OtherPad,Unknown 4, Flash:SMDPad,CuDef 332, Flash:SMDPad,CuDef,BGAPad 225, Flash:ViaPad 240
  Inner  1: Draw:Conductor 4122, Draw:Profile 5, Flash:ComponentPad 133, Flash:OtherPad,Unknown 4, Flash:ViaPad 240, Region:- 185
  Inner  2: Draw:Conductor 2165, Draw:Profile 5, Flash:ComponentPad 133, Flash:OtherPad,Unknown 4, Flash:ViaPad 240, Region:- 150
  Bottom Copper: Draw:Conductor 3094, Draw:Profile 5, Flash:ComponentPad 133, Flash:OtherPad,Unknown 4, Flash:SMDPad,CuDef 198, Flash:ViaPad 240, Region:- 148
  drills: 377 plated, 0 non-plated
  outline 97.8 x 55.9 mm at (13.87, -42.75)
check_sources: OK
  board-local: 225 BGAPad flashes = 225 U10 balls; 4 SMD test pads matched as SMD pads only
check_sources (board wrapper): OK

ALL CHECKS PASSED
```

## Phase 1 preparation – done (Opus 5.5, 2026-11-20)

New in this repo (all generated, `--check` in check_all.sh):

- `tools/make_part_map.py` → `lib/part_map.csv` (146 parts; columns refdes, sheet, lib_id,
  value, package, units). Values from ROOT.DSN (`p2k.pdsprj.dsn_values`, 146/146). Packages
  from ROOT.LYT by the board-local reader `lyt_packages()` (p2k candidate 4): the refdes token
  of each record carries binary junk (`C75B7` = C7, `R405` = R40), so it is matched as the
  longest known refdes prefix and accepted only when the value token after `PART REFERENCE`
  starts with the DSN value; 146/146 found, each once. Pages from `p2k.pdftext`;
  `PAGE_OVERRIDES` for 41 refdes whose other hits are FPGA ball names in the U10 units
  (C4-C15, J2-J9, J11, L1, R1-R15 ...) or page-1 alias labels, resolved on the renders (value
  printed next to the refdes). U10 is listed on sheet 2 (unit A); the `units` column gives
  the page of every unit (A, C: 2; B, D, E, F: 5; G, H: 6). **Page 5 holds only U10 units**
  (0 parts in the part map). Parts per sheet: 1:6 2:19 3:28 4:15 5:0 6:18 7:11 8:3 9:9
  10:9 11:17 12:11.
- `tools/gen_symbols.py` → `lib/tube_control_card.kicad_sym` (36 symbols: 25 part symbols,
  PWR_FLAG, 10 power symbols GND, RS485_GND, 1V, 1V8, 3V3, 5V, 12V, AD_3V3, ISO5V,
  OPAMP_-15V). KiCad std copies: R, C, L, R_ARRAY4 (`R_Pack04_Split`, units A-D = pins
  1-8, 2-7, 3-6, 4-5 = the Proteus pinout), TERMINAL (`TestPoint`, one pin 1), TBLOCK-I5,
  CONN_01X03, TLV316IDBVR (as in tube_psu), TLV9304PWR and TL084HIDYYR (std quad op-amps,
  units A-D like the PDF + unit E = power pins 4/11; Proteus draws the power pins on the
  units). Box symbols with the Proteus pin names of the DSN pinouts: ADS7056, ADC121C027,
  AD5622, W25Q64JWSSIQ, MC2016K_OSC, AP61202, IZB03, TPS73030, MAX22025, SN74AXC8T245,
  SN74LV4051, HEADER_2X8/2X15/2X20_50MIL.
- **U10 = `TI60F225`, 8 units A-H generated from the DSN pinout** `*PINOUT
  BGA225C65P15X15` (8 identical copies in ROOT.DSN, 196 pin names, 8 elements = the PDF
  units; read board-locally because `dsn_pinouts` misses it, p2k candidate 6). Pin numbers =
  ball ids = IPC pin ids, every one of the 225 balls on exactly one unit (asserted):
  A config/JTAG 6 (CDONE, CRESET_N, TCK, TDI, TDO, TMS), B GPIOL/GPIOR singles 23,
  C bank L 38, D bank R 40, E bank B 32, F bank T 30, G power + REF_RES 44, H GND 12.
  Pin order as in the PDF: P before N per pair, lower indices left (split C/D 10, E 9, F 8),
  power groups VCC / VCCIO33 / VCCIO1-4 left, VCCAUX / VCCA / REF_RES pairs right. Pin
  types: GPIO and CDONE bidirectional, VCC*/GND power_in, REF_RES passive, TDO output, other
  config inputs; the 62 N/C balls stay on their units (no-connect flags on the sheets).
  The Reference field sits above the tallest unit body, the Value below the deepest: place
  them per unit with `ref_at` / `value_at` in the sheet scripts.
- `p2k check_symbols`: every refdes' symbol pin set = its IPC pin set (OK).
- `p2k make_skeleton` → `kicad/` (tube_control_card.kicad_pro, sym-lib-table, root + 12
  empty A3 sheets, names from `SHEETS`). `tools/erc.sh` (as tube_psu).
- `tools/compare_netlists.py`: `p2k compare_netlists` with decision **D1** accepted
  (below). `tools/sheets/_common.py`: part-map helpers `part()`, `sh_value()`, `sym()`,
  `term()` (TERMINAL with the part-map symbol/value), `place_mirrored()` and `P()` (PDF
  render coordinates), taken over from tube_power_amp_kicad (its p2k candidates 3, 6, 7).
- Smoke test in a scratch copy (build/tmp/smoke, not committed): page 11 RS485 block (RS1,
  R67-R69, RS485A/B, ISO5V, ISO_G) with labels + U10 unit H with GND. Wrapper: 0 wrong-net
  pins; the shared compare: 3 wrong-net pins (RS485A, RS485B merges); R67-1 moved to the A
  node: wrapper fails (merge + split); a wrong or missing `SPLIT_PIN_MERGES` entry: wrapper
  exits with an error. U10 with only unit H placed: compare reports the 151 connected balls
  of the unplaced units as **missing pins (errors)**, ERC reports unplaced units (warnings)
  and the unplaced power unit G (error `missing_power_pin`) – see the transcription order.
  The multi-unit symbol rendered (`p2k render_sheet`) and checked by eye.

### D1 implementation (split terminal nets)

`SPLIT_PIN_MERGES` in p2k_config.py lists the five pins with (kept IPC net, merged IPC net):
J2-1 5V + 5V.00301, ISO5V-1 ISO5V + ISO5V.00299, ISO_G-1 RS485_GND + RS485_GND.00300,
RS485A-1 #00670.00259 + #00670.00260, RS485B-1 #00671.00261 + #00671.00262 (the merged net
also holds R67-1). `tools/compare_netlists.py` checks that the IPC pins whose pads are on two
nets are exactly these (with exactly these nets), joins each merged net into its kept net on
the IPC side and runs the shared comparison unchanged; any other merge/split still fails. The
PCB checks of Phases 3-4 (check_board, ipc356_diff, assign_nets/drc parity) will need the same
acceptance (p2k candidate 1).

### U10 pinout check against Efinix (finding 3 resolved)

The Proteus pinout was compared ball by ball with the Ti60F225 symbol of the Efinix
**Ti60F225 development board schematic v1.4** (efinixinc.com/docs/ti60f225-dev-board-
schematics-v1.4.pdf, pages 4-12; text layer matched name → ball, plus the power page by eye):
all **196 pin names / 225 balls agree** (GPIOR_P_00_PLLIN0 = L11 checked by hand; the dev
board names the reference resistor pins REF_RES_1A … 4B without the trailing "1"). Power:
VCC E13 G7 G9 H6 H8 J7 J9 M3, VCCAUX D4 E11 L4 M11, VCCA_BL L5 / BR L10 / TL E5 / TR G10,
VCCIO1A J4 L2, 1B D2 F4, 2A C7 D6, 2B C11 D9, 3A F14 G12, 3B J11 L14, 4A N9 N11, 4B N5 N7,
VCCIO33_BL P4 / BR N15 / TL B4 / TR B13, **GND A1 A15 D3 G6 G8 H7 H9 J6 J8 M13 R1 R15**.
So the package has exactly 12 GND balls and every GND and supply ball of the package is
connected on this board (GND 12, 1V 12 = VCC + VCCA, 1V8 20 = VCCAUX + VCCIO1-4,
3V3 4 = VCCIO33). The official Efinix pinout spreadsheet needs a login and was not used.

## Phase 1 transcription – session T1 done (Fable 5.2, 2026-11-20)

Sheets 1, 11, 10, 8, 3 drawn by `tools/sheets/sheetNN.py` (63 of 146 parts). Per sheet
(`python3 tools/compare_netlists.py --allow-missing --sheet N`, run after the last sheet; the
totals line is the same for every N: `pins compared 247, wrong-net pins 0; IPC nets touched 114,
complete 31`, `compare: OK`):

| Sheet | Parts | Compare | ERC on the sheet | Notes |
|---|---|---|---|---|
| 1 Net aliases and power inputs | 6/6 | 0 missing, 0 wrong-net pins | 0 errors | J4, J2 (D1), J5, J9 with a PWR_FLAG each (GND, 5V, 12V, OPAMP_-15V enter here); J8; R16; all alias pairs as text notes |
| 11 Bias DAC and RS485 | 17/17 | 0 missing, 0 wrong-net pins | 1 pending error (RS1-2 TXD) | D1 terminals as one pin; B node = R68-2, RS1-7, R67-1, RS485B; PWR4 pins 3, 4, 7 with no-connect flags |
| 10 Connectors and bias ADC | 9/9 | 0 missing, 0 wrong-net pins | 0 errors | J7 (rotated 180), J6, J3 (mirrored); 7 N/C pins flagged (J6 x6, ADC1-K2) |
| 8 Power stage connector J11 | 3/3 | 0 missing, 0 wrong-net pins | 0 errors | J11 mirrored (39 top left); 37, 38 N/C |
| 3 Regulators | 28/28 | 0 missing, 0 wrong-net pins | 0 errors | `buck()` block x3; PWR_FLAG on 1V8, 1V, 3V3 behind the inductors; AD_3V3 driven by V4 VOUT (power output) |

Every render (`reports/render/NN_*.png`, git-ignored) was compared by eye with
`build/tmp/pdf/hi-NN.png`. Drawing differences (same nets) are listed in each script's docstring.

**ERC: 0 errors, 72 warnings, 1 pending error.**
- The 72 warnings are all `isolated_pin_label`: global labels of sheets 1, 8, 10, 11 whose other
  pins are on sheets not drawn yet (pages 2, 4, 5, 7, 9, 12; checked: every one of these nets has
  2 or more IPC pins). They must disappear in T2 / T3; what remains then are the single-pin nets
  of the transcription rules.
- Pending (`tools/erc_pending.txt`): `pin_not_driven RS1 2` – RS1 TXD is an input whose only
  driver is U10 ball G1 (sheet 2, T3). `tools/erc_check.py` accepts exactly the listed errors and
  fails on a listed error that no longer occurs, so the list has to be empty at the end of T3.

**New in this session (board-local):**
- Decision D2 (no pin of type no_connect, `no_connect_connected` fatal), `tools/erc_check.py`,
  `tools/erc_pending.txt`, `tools/test_no_connect.py` – see Decisions.
- `tools/sheets/_common.py`: IPC-driven helpers. `net(ref, pin)`, `pin_of(ref, net)`,
  `net_kind(net)` (power / global / local / wire, from the IPC pads, the part-map pages and the
  U10 unit pages), `tie(sh, net, point, side, n)` (power symbol, global or local label – chosen by
  `net_kind`, asserts that the name is an IPC net), `pin_tie(sh, placed, pin, side, n)` (the same
  for the IPC net of a pin; no-connect flag on an N/C pad), `two(sh, ref, x, y, top=|left=)`
  (two-pin part oriented by the IPC net or pin number of its top / left pin), `place_pin()`
  (symbol placed by one of its pins), `header()` (dual-row header in the three PDF orientations
  with all its pin ties), `note()`. So no net name is typed from the PDF: a wrong orientation or
  a wrong name fails in the script, a wrong wire in compare.
- `tools/make_sheets.sh [--check]`: re-runs every sheet script; `--check` (in check_all.sh)
  fails when a committed sheet is not what the scripts and the library generate.
- `tools/gen_symbols.py`: AP61202 and TPS73030 pins arranged as in the PDF (AP61202: VIN, EN
  left; VOUT, SW, FB right; GND bottom. TPS73030: VIN, EN, GND left; VOUT, NR right).
- `.gitignore`: `reports/render/`.

## Phase 1 transcription – session T2 done (Fable 5.2, 2026-11-20)

Sheets 7, 9, 12, 4 drawn by `tools/sheets/sheetNN.py` (46 parts; 109 of 146 now). Per sheet
(`python3 tools/compare_netlists.py --allow-missing --sheet N`; totals after the last sheet:
`pins compared 568, wrong-net pins 0; IPC nets touched 206, complete 117`, `compare: OK`):

| Sheet | Parts | Compare | ERC on the sheet | Notes |
|---|---|---|---|---|
| 7 ADC multiplexer | 11/11 | 0 missing, 0 wrong-net pins | 2 pending errors (AD2-1 ~CS, AD2-3 SCLK) | U3 hidden supply pins drawn below the body; PWR_FLAG on the filtered analog supply behind L3 (#00427); AGND = DGND = GND |
| 9 JFET drivers 1-12 | 9/9 | 0 missing, 0 wrong-net pins | 0 errors | `jfet_quad()` x3: U5, U6, U11 units A-D + power unit E over unit A; R14/R15, R22/R23, R24/R25 units A-D; the 12 alias pairs as notes |
| 12 JFET drivers 13-16 | 11/11 | 0 missing, 0 wrong-net pins | 0 errors | `jfet_quad()` for U14 / R17 / R18; 8 decoupling capacitors |
| 4 Level shifters | 15/15 | 0 missing, 0 wrong-net pins | 0 errors | `level_shifter()` x5; direction table as a note |

Every render (`reports/render/NN_*.png`) was compared by eye with `build/tmp/pdf/hi-NN.png`; drawing
differences (same nets) are in each script's docstring. Unit / pin assignment checked against
`reference/pin_nets_by_component.md` by the helpers themselves: `jfet_cell()` takes the array unit
from the IPC net of the op-amp pin and asserts pins {k, 9-k}, the feedback resistor's other pin = the
output net, and every unit of both arrays used once; the PDF label of every cell input / output is
asserted in sheet09.py / sheet12.py (IPC name or its alias).

**ERC: 0 errors, 86 warnings, 3 pending errors.**
- The 86 warnings are all `isolated_pin_label`:
  - **6 stay for good** (single-pin nets, finding 2): PWM_Q7, GPIO_BYPASS_RLY_ISO, PWM_TRANS5, PWM_Q8
    (U1 B1-B4), GPIO_BYPASS_RLY_ISOLATED, ADCLK_ISO (U9 B1-B2);
  - **80 still open**: labels of nets whose only other pin is a U10 ball (checked by script: each of
    the 80 nets has a U10 pin in the IPC). They must disappear in T3; then the 6 above plus the 8
    single-ball nets of U10 (transcription rules) remain.
- Pending (`tools/erc_pending.txt`, 3): `pin_not_driven RS1 2` (TXD, U10 G1), `pin_not_driven AD2 1`
  (~CS, U10 P2), `pin_not_driven AD2 3` (SCLK, U10 P5): inputs driven only by a U10 ball, session
  T3. The three U3 select inputs (pending after sheet 7) were resolved by sheet 4 (U9 B5-B7) and
  removed.
- PWR_FLAGs added: one on the analog supply node behind L3 (sheet 7).

**New in this session (board-local):**
- `tools/gen_symbols.py`: ADS7056, SN74LV4051 and SN74AXC8T245 pins arranged as in the PDF
  (SN74AXC8T245: VCCA / VCCB on top, the two GND pins below, DIR left, VCCB / ~OE right;
  SN74LV4051: X0-X7 and A, B, C, INH left, X right, the Proteus-hidden VDD / VEE / VSS below).
  Pin sets and types unchanged; make_sheets (0 files changed), check_symbols and
  test_no_connect.py re-run: OK.
- `tools/sheets/_common.py`: `unit_of()`, `unit_pins()`, `array_r()` (one unit of an R_ARRAY4 chosen
  by the IPC net of a pin), `jfet_cell()` / `jfet_quad()` (pages 9 and 12), `level_shifter()` (page 4).

## Phase 1 transcription – session T3 done (Fable 5.2, 2026-11-20): Phase 1 complete

Sheets 2, 5, 6 drawn by `tools/sheets/sheet02.py`, `sheet05.py`, `sheet06.py` (37 parts + all eight
units of U10; 146 of 146 now). The three sheets were checked together (compare reports the balls of
unplaced units as errors) and committed together.

| Sheet | Parts | Compare (full, no `--allow-missing`) | ERC on the sheet | Notes |
|---|---|---|---|---|
| 2 FPGA configuration and clock | 19/19 + U10 units A, C | 0 missing, 0 wrong-net pins | 0 errors; 3 expected warnings (GPIOL_N_10, GPIOL_N_18, GPIOL_P_18) | CDONE / CRESET_N nets (#00113, #00114) as wires; 9 no-connect flags (unit C); alias pairs and the two hand notes as text |
| 5 FPGA IO banks | 0 + U10 units B, D, E, F | 0 wrong-net pins | 0 errors; 5 expected warnings (GPIOL_10, GPIOL_11, GPIOR_20, GPIOR_N_11, GPIOT_N_01) | 53 no-connect flags (D 22, E 15, F 16, B 0); the six alias balls of unit B carry the IPC name, pairs as a note |
| 6 FPGA power | 18/18 + U10 units G, H | 0 missing, 0 wrong-net pins | 0 errors, 0 warnings | supply groups on bus lines with one power symbol each (`rail_bus()`), REF_RES nets #00388-#00395 as wires to the eight 10k0 resistors |

**Full comparison** (`python3 tools/compare_netlists.py`): parts 146/146 present, 0 missing, 0 extra;
pins compared 876, **wrong-net pins 0**; IPC nets touched 298, **complete 298** (= 227 IPC nets − 5
merged by D1 + 76 N/C pads, each its own net). No-connect flags on U10: **62** (9 + 53), the list of
the transcription rules.

**ERC: 0 errors, 14 warnings, `tools/erc_pending.txt` empty** (the entries RS1-2, AD2-1, AD2-3 were
resolved by balls G1, P2, P5). The 80 warnings open after T2 are gone. The 14 remaining warnings are all
`isolated_pin_label` = the single-pin nets of the board (finding 2), a label on one pin each:

| Label | Pin | Sheet | Why it stays |
|---|---|---|---|
| PWM_Q7, GPIO_BYPASS_RLY_ISO, PWM_TRANS5, PWM_Q8 | U1 B1-B4 (21, 20, 19, 18) | 4 | level-shifter outputs that go nowhere |
| GPIO_BYPASS_RLY_ISOLATED, ADCLK_ISO | U9 B1, B2 (21, 20) | 4 | level-shifter outputs that go nowhere |
| GPIOL_N_10 | U10 G2 | 2 | ball + one via only (Phase 3) |
| GPIOL_N_18, GPIOL_P_18 | U10 A2, B2 | 2 | balls with a label, no other pin |
| GPIOL_10, GPIOL_11 | U10 B5, C5 | 5 | ball + an SMD test pad each (board-only pads, Phase 3) |
| GPIOR_20, GPIOR_N_11, GPIOT_N_01 | U10 D12, G14, C6 | 5 | balls with a label, no other pin |

Renders (`reports/render/02_*.png`, `05_*.png`, `06_*.png`) compared by eye with
`build/tmp/pdf/hi-02/05/06.png`; drawing differences (same nets) are in each script's docstring: uniform
2.54 mm ball pitch (the PDF spaces the pairs), power symbols instead of terminals, the reference
resistors at an even pitch.

**New in this session (board-local):**
- `tools/gen_symbols.py`: unit C draws GPIOL 15, 16 and 18 N before P, as the PDF does (`N_FIRST`);
  afterwards the order of the balls on every side of every unit equals the PDF order (checked against
  the PDF text layer). Pin sets and types unchanged; `make_sheets` (0 files changed), `check_symbols`
  and `test_no_connect.py` re-run: OK.
- `tools/sheets/_common.py`: `fpga_unit()` (one U10 unit: reference / value at the body, `pin_tie()`
  over all its balls with the side from the pin position; global labels stand beyond the local labels
  of the same side so the texts do not overlap at the 2.54 mm pitch), `ball_texts()` (pin name and
  terminal label of every ball from the PDF text layer), `rail_bus()` (supply bus of unit G).
  `fpga_unit()` **asserts for every ball**: PDF pin name = symbol pin name; no PDF label ⇔ N/C, rail or
  auto-named net; PDF label = IPC net (case-insensitive) or a listed alias, and every listed alias is
  used. Negative-tested: an alias removed (`U10-N13: PDF label GPIOR_24, IPC net MOS_GATE_1`) and an
  unused alias added both fail.
- `tools/check_all.sh`: the netlist comparison runs without `--allow-missing`.

### Verification at the end of Phase 1 (`tools/check_all.sh`; latest: Phase 2 above)

```
(KiCad environment, IPC self-check, X2 vs IPC: unchanged, see Phase 0 / T1)
== Part map up to date
make_part_map: lib/part_map.csv up to date (146 parts)
== Symbol library up to date
gen_symbols: lib/tube_control_card.kicad_sym up to date (36 symbols)
== Symbol pin sets vs IPC
symbols: 25 part types, 146 refdes, 10 power symbols
symbols: OK
== Sheets up to date (tools/sheets/sheetNN.py)
make_sheets: 12 sheet scripts, kicad/ up to date
== ERC
erc: 0 errors, 14 warnings (14 isolated_pin_label) (reports/erc.rpt)
== Netlist comparison vs IPC (D1 merges accepted)
accepted (D1, board-local): 5 merged IPC net pairs: ISO5V-1 ISO5V + ISO5V.00299; ISO_G-1 RS485_GND + RS485_GND.00300; J2-1 5V + 5V.00301; RS485A-1 #00670.00259 + #00670.00260; RS485B-1 #00671.00261 + #00671.00262 (with R67-1)
compare: parts 146/146 present, 0 missing, 0 extra; pins compared 876, wrong-net pins 0; IPC nets touched 298, complete 298
compare: per sheet (drawn/total) 1:6/6 2:19/19 3:28/28 4:15/15 6:18/18 7:11/11 8:3/3 9:9/9 10:9/9 11:17/17 12:11/11
compare: OK

ALL CHECKS PASSED
```

### Transcription rules (used by the sheet sessions; Phase 1 is done)

- Use only `tube_control_card:` symbols, exactly the `lib_id` of `lib/part_map.csv` per
  refdes and that file's value (`sym()`, `sh_value()` in `_common.py`). Refdes = IPC refdes.
- **Net names = IPC names** (`reference/pins_by_net.md`, `reference/pin_nets_by_component.md`),
  whatever the PDF label says; look up the pin, not the label:
  - case: the PDF writes `3v3`, `1v`, `gnd`, `rs485_gnd`, `opamp_-15V`, `biasfeedback`,
    `RLY5_enable` ... – use the IPC spelling;
  - PDF aliases (page 1 pairs, page 10 `GPIOL_6`–`LOOP_BYPASS_RLY`, `JFET_1`–`A`,
    `JFET_13`–`C'`, `JFET_15`–`D'`, `POWERSDA`–`GPIOL_N_17`, page 11 `GPIOR_18`–`dac_clock`,
    `GPIOR_16`–`dac_data`, page 2 `TXD`–`GPIOL_N_09`, `RXD`–`GPIOL_P_10`, page 9 bottom
    `GPIOR_19`–`JFET_GPIO_11` ...): Proteus joined the two labels and the IPC keeps one name
    (`A`, `GPIOR_18`, `TXD`, `RLY3_ENABLE` ...). Put the **IPC name** on every pin of the net
    and draw the alias pair itself as a **text note** (e.g. "Proteus alias: JFET_1 = A"), not
    as two labels on a wire (ERC `multiple_net_names`, and a global label on a power net is an
    error). Never two names on one net.
  - page 1 (finding 2): pairs drawn with a **dashed** line (R11–PWM_G2_ISO,
    GPIOR_25–ADASEL2_ISO, N14–ADCLK_ISO) are not joined in Proteus (the IPC keeps the nets
    apart); pairs whose second name occurs nowhere else (L1, N1, P1, T3, T4, RGB1_R, P8,
    R10-R14, T15, R3, R4, T7, N8, T11-T13, R16, T6, R6, MDATA_INU, T_IRQ, ISOADA1-3,
    GPIOR_29 …) add no connection. All page-1 pairs → text notes. Sheet 1 parts: J2, J4,
    J5, J9 (terminals: GND, 5V, 12V, OPAMP_-15V), J8 (1 GPIOL_2, 2 GPIOL_1, 3 GND; PDF
    `ISOGND` = GND), R16 (3V3 – GPIOL_1).
- **Power symbols** for the 10 rails: GND (PDF GND, DGND, AGND, gnd, ISOGND), 1V, 1V8, 3V3,
  5V, 12V, AD_3V3 (PDF `VCC/VDD`, U3 VDD, V4 output), ISO5V, RS485_GND, OPAMP_-15V. Use
  `flagged_power` (power symbol + PWR_FLAG) once per rail where ERC reports an undriven power
  pin – where the rail enters (terminals J2/J4/J5/J9 on sheet 1, PWR4 outputs on sheet 11) or is
  generated (PWR1-3 / L1, L4, L5 on sheet 3; V4 on sheet 3 for AD_3V3).
- **D1 terminals** (J2, ISO5V, ISO_G, RS485A, RS485B, and J4, J5, J9): one TERMINAL symbol,
  one pin 1, drawn as in the PDF (`term()` in `_common.py`): J2 on 5V, ISO5V on ISO5V, ISO_G on
  RS485_GND, RS485A on the A node (R67-2, R69-1, RS1-6), RS485B on the B node (R68-2, RS1-7 and
  R67-1). `tools/compare_netlists.py` accepts exactly these five merges.
- Other named nets → labels: **global labels** for the 141 named nets with pins on more than
  one sheet (U10 balls count on the page of their unit: A, C → 2; B, D, E, F → 5; G, H → 6),
  local labels for one-sheet nets. The 39 auto-named `#00xxx` nets are plain wires (none
  crosses a sheet).
- **N/C pins: always a no-connect flag, never a pin of type no_connect** (decision D2). Use
  `pin_tie()`: it places the flag when the IPC pad is N/C. A flag on a wired pin fails ERC
  (`no_connect_connected` is fatal), a wired N/C pin without a flag fails compare. The pins:
  ADC1-K2 J11-37 J11-38 J6-6 J6-8 J6-10 J6-12 J6-13 J6-14
  PWR1-6 PWR3-6 PWR4-3 PWR4-4 PWR4-7 (all flagged in T1), and the 62 U10
  balls C8 C9 C10 C13 D5 D7 D8 D10 D13 E3 E6 E7 E8 E9 E10 E12 F3 F5 F7 F8 F9 F10 F11 F12 F13
  G3 G4 G5 G11 G13 H3 H10 H11 H12 H13 J10 J12 K3 K4 K6 K7 K8 K9 K10 K11 K12 K13 L6 L7 L8 L9
  L11 L12 L13 M6 M7 M8 M9 M10 M14 N6 N8 (the PDF draws these balls without a wire).
- **Single-pin nets** (finding 2): ADCLK_ISO (U9-20), GPIO_BYPASS_RLY_ISOLATED (U9-21),
  GPIO_BYPASS_RLY_ISO (U1-20), PWM_Q7 (U1-21), PWM_Q8 (U1-18), PWM_TRANS5 (U1-19), and U10
  GPIOL_10 (B5), GPIOL_11 (C5), GPIOL_N_10 (G2), GPIOL_N_18 (A2), GPIOL_P_18 (B2),
  GPIOR_20 (D12), GPIOR_N_11 (G14), GPIOT_N_01 (C6): a label on the pin; ERC "isolated
  label" warnings for them are expected (GPIOL_10, GPIOL_11 also reach an SMD test pad on the
  board, GPIOL_N_10 a via – Phase 3). The D1 singletons (5V.00301 …) disappear by D1.
- Hand notes of the PDF (finding 6, "FIX BUGS!", "1v8 oscillator voltage!!!", ...) → text items.
- Grid 1.27 mm; one script per sheet `tools/sheets/sheetNN.py` (NN = PDF page) rebuilding
  `kicad/NN_*.kicad_sch` from scratch (`sheet()` clears it); `P()` maps the 200-dpi render
  (`build/tmp/pdf/hi-NN.png`, re-render with pdftoppm if missing) onto the A3 sheet. Render
  with `tools/p2k/bin/p2k render_sheet kicad/NN_*.kicad_sch` and compare with the PDF page.
- U10 units: `sh.place("TI60F225", "U10", x, y, unit=k)` with k = 1..8 for A..H; give
  `ref_at` / `value_at` per unit (e.g. "U10" above the box as in the PDF).
- **Use the IPC-driven helpers of `_common.py`** (session T1, list above): `two()` for R / C / L,
  `place_pin()` for ICs, `pin_tie()` / `tie()` for every label, power symbol and no-connect
  flag, `header()` for dual-row headers. Type no net name from the PDF; read the PDF only for
  the placement, the wires of the `#00xxx` nets, the notes and to compare its labels with the
  IPC names (a difference that is not a known alias is a finding).
- KiCad details met in T1: a symbol pin on the **middle** of a wire segment is not connected
  (ERC `pin_not_connected`): end a wire segment at every pin (`sh.wire(a, pin_point, b)`). A
  wire end on the middle of another wire needs `sh.junction()`. A supply symbol next to
  horizontal pin rows: `body="left"` / `"right"` in `tie()` / `pin_tie()` so the arrow does not
  touch the neighbouring wire. `two(..., text="above"|"below")` moves the texts of a horizontal
  part.
- **ERC errors that need a later sheet** (an input pin driven only by a U10 ball, a rail
  generated on an undrawn sheet): add `<type> <refdes> <pin>  # why` to
  `tools/erc_pending.txt`; never leave another error. Stale entries fail: remove an entry when
  its sheet is drawn. Empty at the end of T3. PWR_FLAGs so far: GND, 5V, 12V, OPAMP_-15V
  (sheet 1), 1V8, 1V, 3V3 (sheet 3), the analog supply #00427 behind L3 (sheet 7); AD_3V3, ISO5V, RS485_GND are driven by power outputs.
- After a change of `tools/gen_symbols.py` run `tools/make_sheets.sh` (all sheets embed the
  symbols) and, if N/C handling or `tools/erc.sh` / `tools/erc_check.py` changed, `tools/test_no_connect.py`.
- After each sheet: `python3 tools/compare_netlists.py --allow-missing --sheet N` (the
  board wrapper, not the bare p2k tool) and `tools/erc.sh`, then `tools/check_all.sh`.
  Target per sheet: 0 missing on that sheet, 0 compare errors, 0 ERC errors (warnings
  explained here).
- **Order** (easy sheets first to build the label vocabulary; U10 last and in one go, because
  compare reports the balls of unplaced U10 units as missing pins = errors, and ERC an
  unplaced power unit G as an error, until all eight units are drawn):
  session T1 (done): 1 net aliases/power inputs → 11 bias DAC/RS485 (D1) → 10 connectors/bias ADC →
  8 J11 → 3 regulators; session T2 (done): 7 ADC mux → 9 JFET drivers 1-12 → 12 JFET drivers 13-16
  → 4 level shifters; session T3: 2 FPGA config/clock + 5 IO banks + 6 FPGA power (all U10
  units), then the full compare without `--allow-missing`.

## Findings about the original design

Reported, not fixed (PLAN.md section 5.3).

1. **Split terminal nets.** The terminals J2, J4, J5, J9, ISO5V, ISO_G, RS485A, RS485B have
   two 1.4 mm holes 5 mm apart, both pin 1. On J2, ISO5V, ISO_G, RS485A and RS485B the two
   pads are on different IPC nets (Proteus names `<net>.<id>`): the second pad of J2
   (`5V.00301`), ISO5V (`ISO5V.00299`), ISO_G (`RS485_GND.00300`) and RS485A
   (`#00670.00260`) has no other connection; on **RS485B the second pad alone carries R67-1**
   (`#00671.00262` = RS485B-1 + R67-1; `#00671.00261` = RS485B-1 + R68-2 + RS1-7). The PDF
   (page 11) draws R67, R68, RS1 B and RS485B as one node, so the board joins R67 to the
   RS485 B line only through whatever is fitted in the two RS485B holes. See decision D1.
2. **Level-shifter outputs and FPGA balls that go nowhere** (single-pin nets): U1 B1-B4
   (PWM_Q7, GPIO_BYPASS_RLY_ISO, PWM_TRANS5, PWM_Q8), U9 B1-B2 (GPIO_BYPASS_RLY_ISOLATED,
   ADCLK_ISO); U10 A2 GPIOL_N_18, B2 GPIOL_P_18, C6 GPIOT_N_01, D12 GPIOR_20, G2 GPIOL_N_10
   (plus one via), G14 GPIOR_N_11. Page 1 joins pairs of labels. Pairs whose names both
   occur elsewhere work (e.g. RLY3_ENABLE – GPIOR_21 puts ball N14 on RLY3_ENABLE; gnd –
   ISOGND puts J8-3 on GND), but in many pairs one label occurs nowhere else, so the pair adds
   no connection: mostly FPGA ball names (L1, N1, P1, T3, T4, P8, R3, R4, R10-R14, R16, T6,
   T7, T11-T13, T15, N8, N14) plus RGB1_R, GPIOR_25, GPIOR_27, GPIOR_29, ISOADA1-3,
   MDATA_INU, T_IRQ – leftovers of an older wiring? (page 1 also says "FIX BUGS!").
   GPIO_BYPASS_RLY_ISO (U1) and GPIO_BYPASS_RLY_ISOLATED (U9) are two different nets.
3. **U10 power/ground balls:** only 12 balls are on GND and 62 balls are N/C. **Resolved in
   Phase 1:** the Ti60F225 has exactly these 12 GND balls, and every supply ball is connected
   (all 225 ball names agree with the Efinix dev-board schematic, "Phase 1 preparation").
   The 62 N/C balls are unused GPIOs (banks L, R, B, T).
4. **Tight copper near the BGA:** different-net via-pad to ball-pad gaps down to 0.075 mm
   (vias next to the N/C balls F3, H3, M6), 0.088 mm (DATA2 via to ball H4 DATA3), 0.090 mm
   (1V via to ball L4 1V8). Same-net vias overlap their balls by up to 0.028 mm. Phase 3
   `PCB_RULES` clearance has to follow the measured Proteus gaps.
5. **Board thickness:** the CADCAM READ-ME stack (0.3 prepreg + 1.6 core + 0.3 prepreg, 4 x
   0.035 Cu) gives 2.34 mm – probably the Proteus default stack, not the ordered board.
   Confirm with the user before setting `PCB_THICKNESS` (Phase 3).
6. Notes on the PDF to carry over as text: "FIX BUGS!" (p1), "1v8 oscillator voltage!!!",
   "1v8 flash voltage!!!" (p2), "note, needs to be 0.95V and not 1.0V" (p3, PWR2 = core
   supply 1V), "check logic" (p7, U3), "Possible choises are 2x8 ... 2x25" (p8),
   "I2C address = 11, 3-state io", "use reference", "VDDA either 3v3 or 1v8, VDDB max 5.25v"
   (p11).
7. Net naming: GND, DGND, AGND, gnd and ISOGND of the PDF are one net (`GND=POWER`; AGND and
   DGND are tied on page 7, ISOGND via the page 1 alias), so J8 pin 3 "ISOGND" is plain GND.
   The isolated RS485 ground is RS485_GND. `VCC/VDD=POWER` is the AD_3V3 rail (V4 output,
   U3 hidden VDD). The PDF uses lower-case labels (1v, 3v3, gnd, rs485_gnd, biasfeedback,
   dac_clock): Proteus nets are case-insensitive, the IPC spells them upper-case.
8. The PDF metadata date is 2026-10-12 (title blocks 26/03/2025); the X2 CADCAM is from
   2026-11-19, the RS-274X CADCAM from 2025-03-22. All three agree in content as far as checked
   (refdes, nets on the pages read).
9. **ADC1 (ADC121C027) pin names:** the Proteus device uses diode-style pin ids
   (A1 A2 COM1 COM2 K1 K2). As drawn (page 10), the pin named **VIN** (COM2) is on 3V3 and
   the pin named **VA** (A1) on the filtered BIASFEEDBACK input (#00660, R34/C68); ADR0 (K2)
   is N/C. In the ADC121C027 the supply is VA and the input VIN, so either the Proteus symbol
   swaps the names or the board feeds 3V3 into the input. Phase 2 must map the ids to the
   SOT-23-6 pads from the IPC positions and check which pad gets 3V3.
   **Phase 2 result (confirmed):** A1 = SOT-23-6 pad 1 = datasheet **VA** carries #00660 (the filtered
   BIASFEEDBACK input), COM2 = pad 3 = datasheet **VIN** carries **3V3** (A2 = pad 2 GND, K2 = pad 4
   ADR0 N/C, K1 = pad 5 SCL, COM1 = pad 6 SDA): the supply and the input are swapped on the built board,
   as on the three ADCs of tube_hv_supplies (its finding 6). Table in "Phase 2 - pin order". A redesign
   item (and a check of the real board: reworked?).
10. **J8** (3-pin connector, rx/tx/ISOGND on page 1) has the value "1k" in the schematic.
11. **Page 1 dashed alias lines** (R11–PWM_G2_ISO, GPIOR_25–ADASEL2_ISO, N14–ADCLK_ISO) are
   not connections in Proteus (the IPC keeps the nets apart); the solid pairs are joins.
12. **AP61202 pin 6 "VOUT"** (Proteus name) is N/C on PWR1 and PWR3; on PWR2 (the 1V core
   supply) it drives 1V_ENABLE = the EN pins of PWR1 and PWR3 (R1 10k pull-up to 5V), while
   PWR2's own EN is tied to 5V: a power-good style sequencing output, so the Proteus name
   "VOUT" is probably wrong (pin type passive in the symbol). Check the AP61202 pinout in
   Phase 2.
   **Phase 2 result (resolved):** Diodes DS44251: SOT563 pin 6 is **OUT on AP61200/AP61201 and PG
   (open-drain power good, max 6.0 V) on AP61202/AP61203**; pins 1-5 FB, GND, VIN, SW, EN = the Proteus
   ids. So the circuit is a correct PG sequencing (PWR2 = 1V core enables PWR1 / PWR3 through R1 10k to
   5V); only the Proteus pin name "VOUT" is wrong (copied from the AP61200). Nothing to change but the
   name in the redesign.

13. **Page 11 label `bias_feedback`** sits on the DAC output node together with `biasref`
   (IPC net BIASREF: U12-6, R59, C4, J6-15, J6-16). Page 10 spells the ADC input
   `biasfeedback` (IPC net BIASFEEDBACK: J6-5, R34-1 only). The two names differ by the
   underscore, so on the board the DAC output and the ADC input are **not** joined; they meet
   only outside, through J6 (pins 15/16 and 5). Intended (loop closed on the power board) or a
   naming slip – the user's call in the redesign. Drawn as built (note on sheet 11).
14. **PWR4 (IZB03) On/Off pin 3 and Ripple pin 7 are N/C** (page 11 draws them as open stubs),
   as is its pin 4 "NC". Drawn with no-connect flags.
15. **Unconnected terminals in the PDF:** page 10 has 12 `JFET_GATE_*` terminals and page 8
   two lists (T_IRQ, T_DO, T_DIN, T_CS, T_CK, MOSI, LED, SCK, MISO, DATA/COMMAND, LCD_RESET,
   LCD_CS, ISOGND, 3V3; ADB2, ADB1, ADB0, ADB3, ADB4, AGND, ADB5, ADB6) with a wire stub and
   nothing on it: no nets (leftovers of an older design, cf. "FIX BUGS!"). Page 10 also has
   loose texts "3V3" and "-15V" beside J7. All carried over as text notes.
16. **Labels of pages 1, 3, 8, 10, 11 vs IPC:** every pin of the 63 parts drawn in T1 was
   compared with its PDF label; all differences are the known aliases (page 1, 10, 11 pairs),
   the case (rs485_gnd, 1V_enable, L1sw, RLY5_enable ...) and DGND / gnd / ISOGND = GND. No
   other difference.

17. **Page 7 multiplexer channel order** (PDF note "check logic"): ADB2 → X0, ADB1 → X1, ADB0 → X2,
   ADB3 → X3, ADB4 → X4, ADB7 → X5, ADB5 → X6, ADB6 → X7 (U3 pins 13, 14, 15, 12, 1, 5, 2, 4), so
   the select code is not the ADB index. INH, VEE and VSS on GND, VDD on AD_3V3 (hidden pins in
   Proteus). AD2 AINM is on GND; its AVDD, U4 V+, C6 and C7 hang on AD_3V3 through L3 (22uH),
   DVDD on 1V8. The page ties the terminals AGND and DGND together (one net GND).
18. **JFET driver inputs and outputs (pages 9, 12):**
   - The alias table of page 9 names JFET_GPIO_1 = GPIOL_11, JFET_GPIO_2 = GPIOL_9, JFET_GPIO_3 =
     GPIOL_10, but the drivers of JFET_1 (IPC net A), JFET_2 and JFET_4 take GPIOL_N_14, GPIOL_P_14
     and GPIOL_P_15, and the JFET_3 driver takes JFET_GPIO_4 (GPIOT_P_03). GPIOL_10 and GPIOL_11
     are single-ball nets (plus a test pad each); a terminal JFET_GPIO_1 with an open stub stands
     above U5:C. GPIOL_9 (= JFET_GPIO_2) is the input of the **JFET_14** driver on page 12.
   - **JFET_3 and JFET_4 (U5 A, B outputs) reach no other part** (only R15 and U5); JFET_5 and
     JFET_6 (U6 D, C) only an SMD test pad each. Compare the unconnected JFET_GATE terminals of
     page 10 (finding 15).
   - All four quad op-amps (TLV9304 x3, TL084H) run from 3V3 / OPAMP_-15V with the + inputs on GND
     (inverting, gain -4.7): drawn as built.
19. **Page 4 direction table – to verify against the datasheet.** All five SN74AXC8T245 have DIR1 on
   1V8 (H), DIR2 and ~OE on GND (L). The table on the page says H / L = "A to B" for bits 1:4 **and**
   5:8. If DIR2 = L means B to A for bits 5-8 (DIR1 for A1-A4, DIR2 for A5-A8, H = A to B, as the
   TI text says for the two banks), then B5-B8 of every shifter run from the 3V3 side to the FPGA –
   among them ADBSEL0-2 (U3 select), RLY7_ENABLE, RLY2/5/6_ENABLE, MOS_GATE_2, PWM_Q5/Q6,
   PWM_TRANS1-3_ISO, PWM_G1/G3/G4_ISO. A text extract of TI's online datasheet (Table 7-1) was
   read in this session but its rows came out misaligned, so this is **not confirmed**: check the
   function table by eye (and the built board) before the redesign. Drawn as built; the PDF table
   is a text note on sheet 4.
20. **Labels of pages 4, 7, 9, 12 vs IPC:** every pin of the 46 parts drawn in T2 was compared with
   its PDF label (pages 9 / 12 by assertions in the scripts): the only differences are the page 9
   alias pairs (JFET_GPIO_n), JFET_1 = A, the case (gnd) and AGND / DGND = GND. `GPIOB_N12`
   (U2-9, U10-P9) is spelled without the second underscore in both the PDF and the IPC.

21. **Labels of pages 2, 5, 6 vs IPC:** `fpga_unit()` compares every one of the 225 balls with the PDF
   text layer. All pin names agree with the symbol. The only label differences are Proteus aliases:
   page 2 GPIOL_N_09 = TXD (G1), GPIOL_P_10 = RXD (H2), GPIOL_N_16 = POWERSCL (C1), GPIOL_N_17 =
   POWERSDA (C2); page 5 GPIOL_6 = LOOP_BYPASS_RLY (C3), GPIOR_21 = RLY3_ENABLE (N14), GPIOR_24 =
   MOS_GATE_1 (N13), GPIOR_25 = MOS_GATE_3 (P15), GPIOR_27 = MDATA_DAB (P13), GPIOR_29 = SDATA1_ISO
   (R13); plus the case (FLASH_nCE, 3v3, 1v) and DGND = GND, and clk32Mhz = GPIOR_P_19_PLLIN0 (OSC1 OUT,
   ball C14). Unit B labels GPIOL_1 ... GPIOL_9 are the IPC names (pin names GPIOL_01 ...). The other
   parts of pages 2 and 6 were compared by eye: no difference. **Correction of finding 2:** GPIOR_25,
   GPIOR_27 and GPIOR_29 are not names that "occur nowhere else": they are the page-5 labels of balls
   P15, P13 and R13, so the page-1 pairs MOS_GATE_3 = GPIOR_25, GPIOR_27 = MDATA_DAB and SDATA1_ISO =
   GPIOR_29 do connect those balls (as the IPC shows).
22. **FPGA configuration (page 2), as built:** CRESET_N (J5) has only R21 330k to 1V8 and C17 1u to GND
   (power-on RC, no supervisor, no access from J1); CDONE (L3) only the pull-up R27 100k (no LED, no test
   point). CBSEL0 / CBSEL1 (F3, E3) are N/C. The JTAG pull-ups R4-R7 (4.7k, also on TDO) go to **3V3**
   while the configuration pull-ups go to 1V8; J1 carries TDI, TCK, TMS, TDO, GND and **no supply pin**
   for the programmer's reference. TEST_N (E2, GPIOL_N_15) and CSI (N2, GPIOL_P_02) have 100k pull-ups
   to 1V8; DATA2 / DATA3 (flash IO2 / IO3 = WP / HOLD) have no pull-up. The oscillator OSC1 (EN tied to
   VCC) drives ball C14 directly (no series resistor). To check against the Efinix Titanium
   configuration guide in the redesign; drawn as built.
23. **FPGA decoupling (page 6), as built:** page 6 has six 47n on 1V (12 balls) and four 47n on 3V3
   (4 balls) and **no capacitor on 1V8**, which feeds 20 balls (VCCAUX and all eight VCCIO banks). The
   1V8 capacitors of the whole board are C1, C2 (flash, oscillator), the five level-shifter capacitors
   of page 4, C51 (page 11), C71 1u (page 7) and the regulator output C16 10u. Whether some of those sit
   at the BGA is a Phase 3 question (placement). The eight REF_RES pins each have their own 10k0 to GND.
   The PDF value is `10k0` for these and `47n` for all FPGA capacitors.

24. **FLASH1 (W25Q64JWSSIQ, 208 mil SOIC-8) sits on a wide-body pad pattern:** both SO8W parts (RS1
   MAX22025, a 7.5 mm wide-body part, and FLASH1) have pad rows 9.14 mm apart with 2.03 mm long pads
   (inner pad edges 7.11 mm apart). The W25Q64JW "SS" package is the 208 mil (5.3 mm body) SOIC-8, whose
   lead tips span about 7.9-8.3 mm, so its feet overlap the pads only by roughly 0.4-0.6 mm at the inner
   end: solderable by hand, but not the land pattern for that package (IPC: rows about 7.2-7.4 mm).
   Reproduced as built (KiCad 208 mil body graphics, pads on the Proteus rows). A redesign item.
25. **J11 (40-pin ribbon to the HV supplies board) is numbered as the mirror image of a standard 2x20
   header** while mounted on the top side (Proteus top assembly outline and top silk "J11"): the KiCad
   2x20 1.27 mm header fits only mirrored (1.270 mm unmirrored, 0.000 mirrored); with odd / even pad
   numbers swapped it fits on top (0.000). tube_hv_supplies J1, the other end of the ribbon, has
   **the same mirrored numbering, also on top** (its finding 12). With a straight IDC ribbon (pin n to
   pin n) the two swaps cancel: Proteus pin n of J11 meets Proteus pin n of HV J1, so the as-built
   cable connects the nets as drawn – **no pin swap on the ribbon**. But neither header follows the
   standard numbering, so any standard part on this cable (a third board, a breakout, a header with a
   printed pin 1) would see pairs 1-2, 3-4 … exchanged, and KiCad's pin-1 corner mark lands on the pad
   numbered 2. Reproduced (`PinHeader_2x20_P1.27mm_Vertical_RowsSwapped`, as on the HV board). The
   other 1.27 mm headers are standard: J6, J7 on top, J3 (16 pins) on the **bottom** side (Proteus
   bottom assembly) where the mirrored fit is the standard one. Redesign item: number both ribbon
   headers as standard together (never only one end).

## p2k candidates

Shared-tool limitations met on this board, with the board-local workaround used. To be
solved in tools/p2k later (with the ac_psu regression); until then the wrappers stay.

1. **Two-pad pins on different nets** (Proteus `<net>.<id>` names on the two pads of one
   pin): `ipc356 --check` fails "same refdes-pin on different nets". Workaround:
   `SPLIT_PIN_NETS` + `tools/ipc356_check.py`. `compare_netlists.load_ipc` keys pins by
   (refdes, pin) so the later pad record wins (J2-1 looks like it is only on `5V.00301`, and
   R67-1's net looks unrelated to RS485B's other pad). Phase 1 workaround (decision D1):
   `SPLIT_PIN_MERGES` + `tools/compare_netlists.py` (monkey-patches `load_ipc`: verifies the
   split pins = the table, joins each merged net into its kept net, then runs the shared
   compare). The shared compare would need: a config key (e.g. `SPLIT_PIN_MERGES`, pin ->
   nets to join) read by `load_ipc`, which then keys a pin to the union of its pads' nets
   (all pins of the joined nets renamed to one), the accepted merges printed, and a check that
   the IPC split pins equal the key. Phases 3-4 will need the same accepted merges in
   `check_board` / `ipc356_diff` (pad nets compared 1:1 while KiCad gives both pads one net)
   and the DRC parity.
2. **SMD pads without a part** (327 records with a blank refdes): `ipc356` makes them
   `free_pad` and its self-check wants a plated drill; `check_sources` expects free pads as
   OtherPad flashes on every layer and as OtherDrill flashes. Workaround: `SMD_FREE_PADS` +
   both wrappers (kind `smd_test_pad` in a temporary copy of the table). Phase 3 will need a
   board-only SMD footprint for them in `build_pcb` / `check_board` / `ipc356_diff` /
   `gerber_roundtrip` (today free pads are THT with `FREE_PAD_FOOTPRINT`).
3. **`BGAPad,CuDef` aperture function** (U10 balls): `check_sources` reports "unexpected
   function" and finds no flash for the SMD records; `gerber_to_tracks` raises on it
   (`fn in ("ComponentPad", "SMDPad,CuDef")`) and `gerber_roundtrip.PAD_FUNCTIONS` lacks it.
   Workaround in `tools/check_sources.py`: renamed to `SMDPad,CuDef,BGAPad` for the shared
   check. Needs: treat `BGAPad` like `SMDPad` everywhere.
4. **`pdsprj.lyt_parts` returns nothing** for this ROOT.LYT (no `EID` / `EID_A` markers; the
   part records look like `<package> <refdes><junk> ... PART REFERENCE <value><junk> ...
   PART VALUE ... <nets>`). `dsn_values` (146 of 146) works. Workaround (Phase 1):
   `lyt_packages()` in `tools/make_part_map.py` (longest refdes prefix of the token before
   `PART REFERENCE`, accepted only when the value token starts with the DSN value; package =
   the token before the refdes; 146/146). The shared reader would need this record form as a
   fallback (anchor on `PART REFERENCE`, refdes and value tokens with trailing junk).
5. Cosmetic: with an empty `TRUNCATED_REFDES` the cheat sheet prints "Refdes restored from
   6-char truncation: ." (`ipc356.render_by_component`).
6. **`pdsprj.dsn_pinouts` misses pinouts whose PIN lines do not start with "{"**: in this
   ROOT.DSN many `*PINOUT` blocks have lines `PIN "name" = ...}` (the "{" is not in the
   printable run), so the BGA225 (U10), SOT563 (AP61202), SO8W (MAX22025, flash), TSSOP24
   (SN74AXC8T245), SOT-26 (ADC121C027), IZB03, quad op-amp, resistor array ... pinouts come
   back with 0 pins. Workaround: `ti60_pinout()` in `tools/gen_symbols.py` (regex
   `\{?PIN "(.*)" = ([^}]*)\}`, 8 identical copies checked); the other box symbols were
   written from the pinouts read the same way. The shared tool would need the optional "{"
   and should return the element (unit) lists of multi-element pinouts.
7. **`symgen.box` draws single-unit symbols only.** Workaround: `multi_box()` in
   `tools/gen_symbols.py` (one `box()` per unit, its rectangle and pins moved into
   `<name>_<k>_1`, Reference/Value fields from the tallest/deepest body). A shared
   `symgen.multi_box(name, ref, units)` would serve every FPGA/MCU board.
8. **Multi-unit symbols spread over several sheets:** `lib/part_map.csv` has one `sheet` per
   refdes, and `compare_netlists` reports the connected pins of unplaced units as errors
   ("missing pin ... unit not placed?") even with `--allow-missing`, so the U10 sheets (2, 5,
   6) have to be drawn in one session. Board-local: a `units` column (page per unit) in the
   part map, used only as documentation. The shared compare would need: per-unit pages (e.g.
   the `units` column) so `--sheet N` and `--allow-missing` treat the pins of units on undrawn
   sheets as pending (warnings), like the missing parts.
9. Workarounds adopted from tube_power_amp_kicad (its candidates 3, 6, 7): `term()` instead of
   `sheetkit.terminal` (symbol / value from the part map, text justification), and
   `place_mirrored()` (no mirror option in `sch_builder.Sheet.place`), in
   `tools/sheets/_common.py`.

10. **Pins of type no_connect hide wiring mistakes** (found by the preamp conversion, closed
   here by decision D2): KiCad 10 keeps such a pin in its own `unconnected-(...)` net even when
   a wire joins it, so `compare_netlists` sees an N/C pad as N/C although the schematic wires
   it; ERC only warns `no_connect_connected`. Board-local: no pin of that type
   (`tools/gen_symbols.py` asserts it), no-connect flags on the sheets, `tools/erc_check.py`
   fails on `no_connect_connected`; negative test `tools/test_no_connect.py`. Needed in p2k:
   `check_symbols` (or `symgen.run`) should reject pin type no_connect, the playbook (Phase 1
   step 2 and section 5 "KiCad 10") should state the rule, and a shared ERC judge should treat
   `no_connect_connected` as fatal.
11. **No shared ERC judge:** every board copies `tools/erc.sh` (grep on the report). Board-local
   here: `tools/erc_check.py` (parses the report, fatal warning types, a pending list for
   errors that need a sheet not drawn yet, stale entries fail, warnings counted by type). A
   `p2k erc` with these options would serve every board; the pending list matters for boards
   with a multi-unit part drawn last.
12. **IPC-driven sheet helpers** (`net()`, `net_kind()`, `tie()`, `pin_tie()`, `two()`,
   `place_pin()`, `header()` in `tools/sheets/_common.py`): the label kind (power symbol /
   global / local / no-connect flag) and the orientation of two-pin parts follow from the IPC
   netlist and the part map, so they need not be typed per pin. Candidates for `p2k.sheetkit`
   (they need the per-unit pages of candidate 8 for multi-unit parts). Also `Sheet.place`
   could take a pin to anchor on, and `make_sheets --check` (sheets reproducible from the
   scripts) is generic.
13. `compare_netlists.natkey` / `pinkey` build mixed int / str sort keys and raise `TypeError`
   when a refdes without a number is drawn next to a numbered one with the same prefix (reported
   by the PI/FX conversion, e.g. SEND and SEND1). **Not hit on this board**: all 146 refdes and
   876 pins sort without error (checked; the only refdes without a digit is ISO_G). No wrapper
   change made; fix in p2k (type-safe key).
14. `sch_builder`: a pin placed on the middle of a wire segment is not connected in KiCad;
   `Sheet.wire` could split segments at pin points (or `Sheet.save` could warn).

15. `symgen.box`: top / bottom pins get a body margin sized for the pin name inside the body
   (VCCA → 7.62 mm), so a symbol with supply pins on top is 4 grid rows taller than the Proteus
   one and page 4 does not fit at the PDF pitch (U2, U9 moved down). An option for the margin
   (or names outside) would keep the PDF layout.
16. Multi-unit helpers of `tools/sheets/_common.py` – `unit_of()`, `unit_pins()`, `array_r()`
   (resistor-array unit chosen by the IPC net) and the power unit laid over unit A
   (`jfet_quad()`) – are candidates for `p2k.sheetkit` together with candidate 12.

17. **U10 sheet helpers** (`fpga_unit()`, `ball_texts()`, `rail_bus()` in `tools/sheets/_common.py`): a
   multi-unit part placed unit by unit with all its pin ties, and the **PDF text layer used as a check**
   (pin name and terminal label of every pin vs symbol and IPC net, aliases listed explicitly).
   `p2k.pdftext` could offer "the words left / right of a pin-number word on its row" so every sheet
   script can assert its labels instead of comparing them by eye (candidates 12 and 16).
18. `sch_builder` / `sheetkit`: at a 2.54 mm pin pitch a local label (text above its wire) lies on the
   global label of the row above. Board-local: `fpga_unit()` puts the global labels of a side beyond
   its longest local label. A shared helper could do the same (or draw local labels below the stub).

19. **Two pads with one number on different nets** (the D1 terminals) need nothing in
   `footprints` / `check_footprints`: `fpgeom.fit` pairs same-number pads by permutation and fits both
   (candidate 1 concerns only the net checks of Phases 1, 3, 4).
20. **`check_pin_order` as a shared tool** (tube_hv_supplies candidate 14): board-local copy here with
   two additions worth sharing – the footprint of every check taken from the board's RULES (`rule()`),
   not typed again, and an expected fit **angle** (a pure rotation of all pad ids, e.g. a BGA's ball
   grid turned by 90 deg, fits with residual 0 and passes check_footprints; only the angle shows that
   the footprint graphics / A1 mark are turned; negative test T4).
21. **Board-only SMD pad** (candidate 2): `footprints.single_pad` makes THT pads only. Board-local:
   `smd_pad=(diameter, side)` specs built by a wrapper around `footprints.build_library` in
   `tools/gen_footprints.py`. Needed: an `smd=True` (layer F/B) option in `single_pad`, and
   `build_pcb` / `check_board` / `ipc356_diff` / `gerber_roundtrip` treating SMD `free_pad` records
   (Phase 3-4).
22. `footprints.run` does not write `kicad/fp-lib-table` (needed for ERC with project footprints and
   for pcbnew); board-local `fp_lib_table()` in gen_footprints.py, as tube_hv_supplies / tube_power_amp.
23. `p2k.footprints.derive` moves base pads onto the IPC positions however far (tube_hv_supplies
   candidate 12; negative test T3 here); `check_footprints` accepts a THT part that fits only mirrored
   with a note (tube_hv_supplies 13: J11 with the plain header would silently go to the bottom side;
   here J3 really is a bottom part). A side source (Proteus assembly layers, as `tools/check_pin_order.py
   --render` shows) would let the shared check decide.

## Decisions

- **D1 (decided by the user, 2026-11-20): split terminal nets** (finding 1). The five split
  terminals J2, ISO5V, ISO_G, RS485A and RS485B are drawn as **one pin each, as the PDF draws
  them**, so KiCad puts both pads on one net (for RS485B this joins R67-1 to the RS485 B net,
  as in the PDF). The five merged IPC net pairs are recorded as an accepted difference in the
  checks: `SPLIT_PIN_MERGES` in p2k_config.py, accepted exactly by the board-local
  `tools/compare_netlists.py` (Phase 1); `check_board` / `ipc356_diff` / DRC parity get the
  same acceptance in Phases 3-4 (p2k candidate 1). Pad numbers stay = IPC pin ids (both pads 1).

- **D2 (coordinating session, 2026-11-20): no pin of type no_connect.** KiCad 10 keeps a pin
  of type no_connect in its own `unconnected-(...)` net even when a wire joins it (ERC only
  warns `no_connect_connected`), so `compare_netlists` cannot see an N/C pad that is wired by
  mistake. On this board: (a) no symbol pin has the type – IZB03 pin 4 "NC" (PWR4-4, the only
  one) is passive, `tools/gen_symbols.py` asserts that the library has none; (b) every N/C pad
  gets a no-connect flag on its sheet (`pin_tie()`); (c) `tools/erc.sh` (`tools/erc_check.py`)
  fails on the warning `no_connect_connected`. Negative test `tools/test_no_connect.py` (scratch
  board in build/tmp/nctest, PWR4 only, the real erc.sh and compare wrapper), result:

  ```
  ok          ERC pass, compare pass   -> as expected
  wired_flag  ERC FAIL, compare FAIL   -> as expected   (pin 4 wired to ISO5V, flag kept)
  wired       ERC pass, compare FAIL   -> as expected   (wired, no flag: N/C mismatch PWR4-4)
  old_lib     ERC FAIL, compare pass   -> as expected   (pin type no_connect: the blind spot; only the fatal warning catches it)
  ```

  The 62 N/C balls of U10 already had real pin types (bidirectional GPIOs): flagged in T3 (62 flags).

Open (not blocking Phase 3): pad sizes per refdes, J8 drill, J1 body – "Phase 2 / open questions";
the board thickness (finding 5) for Phase 3.
