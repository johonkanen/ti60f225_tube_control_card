# Status: Tube control card v2.5 (Ti60F225, `fpga_boardv2.5`)

Plan: [PLAN.md](PLAN.md). Playbook: `tools/p2k/CONVERSION_PLAYBOOK.md`.

| Phase | State |
|---|---|
| 0 Skeleton and inventory | **done** 2026-11-20 (Opus 5.5) |
| 1 Schematic | preparation **done** 2026-11-20 (Opus 5.5); transcription not started (12 sheets) |
| 2 Footprints | not started |
| 3 PCB | not started |
| 4 Verification | not started |
| 5 Clean-up | not started |

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

### Last verification (`tools/check_all.sh`)

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
== Part map up to date
make_part_map: lib/part_map.csv up to date (146 parts)
== Symbol library up to date
gen_symbols: lib/tube_control_card.kicad_sym up to date (36 symbols)
== Symbol pin sets vs IPC
symbols: 25 part types, 146 refdes, 10 power symbols
symbols: OK
== ERC
erc: 0 errors, 0 warnings (reports/erc.rpt)
== Netlist comparison vs IPC (D1 merges accepted)
accepted (D1, board-local): 5 merged IPC net pairs: ISO5V-1 ISO5V + ISO5V.00299; ISO_G-1 RS485_GND + RS485_GND.00300; J2-1 5V + 5V.00301; RS485A-1 #00670.00259 + #00670.00260; RS485B-1 #00671.00261 + #00671.00262 (with R67-1)
compare: parts 0/146 present, 146 missing, 0 extra; pins compared 0, wrong-net pins 0; IPC nets touched 0, complete 0
compare: per sheet (drawn/total) 1:0/6 2:0/19 3:0/28 4:0/15 6:0/18 7:0/11 8:0/3 9:0/9 10:0/9 11:0/17 12:0/11
WARNING: missing parts (146): (see --verbose or --sheet N)
compare: OK

ALL CHECKS PASSED
```

### Transcription rules (for the sheet sessions)

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
- **N/C pins** (no-connect flag): ADC1-K2 J11-37 J11-38 J6-6 J6-8 J6-10 J6-12 J6-13 J6-14
  PWR1-6 PWR3-6 PWR4-3 PWR4-4 (pin type no_connect: no flag needed) PWR4-7, and the 62 U10
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
- After each sheet: `python3 tools/compare_netlists.py --allow-missing --sheet N` (the
  board wrapper, not the bare p2k tool) and `tools/erc.sh`, then `tools/check_all.sh`.
  Target per sheet: 0 missing on that sheet, 0 compare errors, 0 ERC errors (warnings
  explained here).
- **Order** (easy sheets first to build the label vocabulary; U10 last and in one go, because
  compare reports the balls of unplaced U10 units as missing pins = errors, and ERC an
  unplaced power unit G as an error, until all eight units are drawn):
  session T1: 1 net aliases/power inputs → 11 bias DAC/RS485 (D1) → 10 connectors/bias ADC →
  8 J11 → 3 regulators; session T2: 7 ADC mux → 9 JFET drivers 1-12 → 12 JFET drivers 13-16
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
10. **J8** (3-pin connector, rx/tx/ISOGND on page 1) has the value "1k" in the schematic.
11. **Page 1 dashed alias lines** (R11–PWM_G2_ISO, GPIOR_25–ADASEL2_ISO, N14–ADCLK_ISO) are
   not connections in Proteus (the IPC keeps the nets apart); the solid pairs are joins.
12. **AP61202 pin 6 "VOUT"** (Proteus name) is N/C on PWR1 and PWR3; on PWR2 (the 1V core
   supply) it drives 1V_ENABLE = the EN pins of PWR1 and PWR3 (R1 10k pull-up to 5V), while
   PWR2's own EN is tied to 5V: a power-good style sequencing output, so the Proteus name
   "VOUT" is probably wrong (pin type passive in the symbol). Check the AP61202 pinout in
   Phase 2.

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

## Decisions

- **D1 (decided by the user, 2026-11-20): split terminal nets** (finding 1). The five split
  terminals J2, ISO5V, ISO_G, RS485A and RS485B are drawn as **one pin each, as the PDF draws
  them**, so KiCad puts both pads on one net (for RS485B this joins R67-1 to the RS485 B net,
  as in the PDF). The five merged IPC net pairs are recorded as an accepted difference in the
  checks: `SPLIT_PIN_MERGES` in p2k_config.py, accepted exactly by the board-local
  `tools/compare_netlists.py` (Phase 1); `check_board` / `ipc356_diff` / DRC parity get the
  same acceptance in Phases 3-4 (p2k candidate 1). Pad numbers stay = IPC pin ids (both pads 1).

Open: none.
