# Status: Tube control card v2.5 (Ti60F225, `fpga_boardv2.5`)

Plan: [PLAN.md](PLAN.md). Playbook: `tools/p2k/CONVERSION_PLAYBOOK.md`.

| Phase | State |
|---|---|
| 0 Skeleton and inventory | **done** 2026-11-20 (Opus 5.5) |
| 1 Schematic | not started (open decision D1 below must be settled before its netlist comparison) |
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

ALL CHECKS PASSED
```

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
3. **U10 power/ground balls:** only 12 balls are on GND and 62 balls are N/C. Check in
   Phase 1 against the Efinix Ti60F225 pinout whether all GND (and supply) balls of the
   package are connected.
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

## p2k candidates

Shared-tool limitations met on this board, with the board-local workaround used. To be
solved in tools/p2k later (with the ac_psu regression); until then the wrappers stay.

1. **Two-pad pins on different nets** (Proteus `<net>.<id>` names on the two pads of one
   pin): `ipc356 --check` fails "same refdes-pin on different nets". Workaround:
   `SPLIT_PIN_NETS` + `tools/ipc356_check.py`. Later phases will also meet it:
   `compare_netlists.load_ipc` keys pins by (refdes, pin) so the later pad record wins (J2-1
   would look like it is only on `5V.00301`); `check_board` / `ipc356_diff` compare pad nets 1:1
   while KiCad puts both pads on one net. Needs: a config key for such pins, compare by the
   union of the nets, and accepted net merges in the PCB checks (depends on decision D1).
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
   part records look like `<package> <refdes> ... PART REFERENCE <value> ... PART VALUE ...
   <nets>`). `dsn_values` (146 of 146) and `dsn_pinouts` (74) work. Phase 1 needs a
   board-local reader for device / package or takes them from the DSN pinouts.
5. Cosmetic: with an empty `TRUNCATED_REFDES` the cheat sheet prints "Refdes restored from
   6-char truncation: ." (`ipc356.render_by_component`).

## Decisions

Open:

- **D1 (user, before the Phase 1 netlist comparison is final):** the five split terminals
  (finding 1). Proposal: draw each terminal as one pin as in the PDF, so KiCad puts both pads
  on one net (RS485B: R67-1 joins the RS485 B net, as the PDF draws it), and record the five
  merged IPC net pairs as an accepted difference in compare_netlists / check_board /
  ipc356_diff. The alternative (reproduce the split exactly) needs different pad numbers
  on the second pads, which breaks "pad numbers = IPC pin ids".
