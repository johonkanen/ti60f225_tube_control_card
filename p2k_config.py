"""proteus2kicad configuration of the fpga_boardv2.5 board (tools in tools/p2k, see its README).

Plain Python; every value here is specific to this board. Coordinates in mm, IPC frame (Y up).
Every key is read by the shared tools (no board-local keys since the shared-tool migration of
2026-11-20, STATUS.md).
"""

PROJECT = "tube_control_card"  # KiCad project / library name

# Sources (relative to the repo root). The CADCAM export with Gerber X2 attributes
# (2026-11-19). source/cadcam_rs274x/ is the RS-274X + Excellon export of 2025-03-22:
# the same design (STATUS.md "Phase 0"), cross-check only.
CADCAM = "source/cadcam"
IPC = "source/cadcam/fpga_boardv2.5 - CADCAM Netlist.IPC"

# --- Schematic skeleton (make_skeleton) ----------------------------------------------

# (Proteus page, sheet name, file). The PDF title blocks carry no sheet name (only
# "fpga_boardv2.5.pdsprj", date 26/03/2025, page n of 12), so the names describe the
# content of each page (STATUS.md "Phase 0").
SHEETS = [
    (1, "Net aliases and power inputs", "01_net_aliases_power_inputs.kicad_sch"),
    (2, "FPGA configuration and clock", "02_fpga_config_clock.kicad_sch"),
    (3, "Regulators", "03_regulators.kicad_sch"),
    (4, "Level shifters", "04_level_shifters.kicad_sch"),
    (5, "FPGA IO banks", "05_fpga_io_banks.kicad_sch"),
    (6, "FPGA power", "06_fpga_power.kicad_sch"),
    (7, "ADC multiplexer", "07_adc_mux.kicad_sch"),
    (8, "Power stage connector J11", "08_power_stage_connector.kicad_sch"),
    (9, "JFET drivers 1-12", "09_jfet_drivers_1_12.kicad_sch"),
    (10, "Connectors and bias ADC", "10_connectors_bias_adc.kicad_sch"),
    (11, "Bias DAC and RS485", "11_bias_dac_rs485.kicad_sch"),
    (12, "JFET drivers 13-16", "12_jfet_drivers_13_16.kicad_sch"),
]
SCH_TITLE = "Tube control card (Ti60F225)"
SCH_COMPANY = "Tube amplifier"
SCH_REV = "rev A (as built)"
SCH_COMMENT = "Redrawn from Proteus fpga_boardv2.5"
SCH_NOTE = ("Tube control card v2.5 (Efinix Ti60F225) - redrawn from Proteus. One sheet per Proteus PDF page.\n"
            "Net names follow the IPC-D-356A netlist (reference/pins_by_net.md).")

# ERC (p2k erc): no_connect_connected is fatal (decision D2: a wired N/C pin must not pass).
ERC_FATAL_WARNINGS = {"no_connect_connected"}

# --- IPC-D-356A fix-ups (ipc356) -----------------------------------------------------

# No truncated refdes: the three 6-character IPC refdes (FLASH1, RS485A, RS485B) are the
# full names printed in the PDF (pages 2 and 11), and every IPC refdes occurs in the PDF.
TRUNCATED_REFDES = {}
TRUNCATED_NETS = {}

# Every Proteus refdes is usable in KiCad ([A-Za-z][A-Za-z0-9_]*: ISO_G, ISO5V, RS485A ...).
KICAD_REFDES = {}

# J11 (40-pin ribbon to the HV supplies board, finding 25): Proteus numbers the header as the mirror image
# of a standard header (odd / even rows swapped). Renumbered to the standard numbering at both ends of the
# ribbon (user decision 2026-11-20, D-PIN; tube_hv_supplies J1 the same way): Proteus pin k = KiCad pad
# k + 1 for odd k, k - 1 for even k (1 <-> 2, 3 <-> 4, ..., 39 <-> 40). Positions, nets, copper unchanged.
IPC_PIN_IDS = {"J11": {str(k): str(k + 1 if k % 2 else k - 1) for k in range(1, 41)}}

NET_ALIASES = {
    "GND=POWER": "GND",          # GND, DGND, AGND, gnd, ISOGND of the PDF are one Proteus net
    "VCC/VDD=POWER": "AD_3V3",   # V4 VOUT, L3, C9, C10, U3 VDD: labelled AD_3V3 (pages 3, 7)
    # Proteus appends ".<net id>" when one name covers several nets. These three are the
    # main nets of the PDF labels 5V, ISO5V and rs485_gnd; the other half of each name is the
    # second pad of a two-pad terminal (J2, ISO5V, ISO_G), kept under its raw name.
    "5V.00026": "5V",
    "ISO5V.00255": "ISO5V",
    "RS485_GND.00256": "RS485_GND",
}

# Decision D1 (user, 2026-11-20; STATUS.md "Decisions"): each split terminal is drawn as one
# pin 1, as in the PDF, so KiCad puts both pads on one net. Two-pad terminals whose two pads (both
# pin 1) carry different IPC nets: pin -> (kept IPC net, merged IPC net), IPC names after
# NET_ALIASES. Read by every shared check (ipc356 --check, check_sources, compare_netlists,
# build_pcb / check_board / assign_nets / drc, ipc356_diff): exactly these five merges are accepted
# (the IPC split pins must equal the key) and printed as "accepted (SPLIT_PIN_MERGES)"; the second
# pad of each terminal has no copper to the first, so the open / unconnected item of each D1 net is
# accepted too. On RS485B the merged net also carries R67-1 (the PDF draws R67 on the RS485 B node).
SPLIT_PIN_MERGES = {
    ("J2", "1"): ("5V", "5V.00301"),
    ("ISO5V", "1"): ("ISO5V", "ISO5V.00299"),
    ("ISO_G", "1"): ("RS485_GND", "RS485_GND.00300"),
    ("RS485A", "1"): ("#00670.00259", "#00670.00260"),
    ("RS485B", "1"): ("#00671.00261", "#00671.00262"),
}

# Blank-refdes records: a net and one of these drills = via; no net = hole (4 plated
# 3.0 mm mounting holes, 6.35 mm copper on every layer, in the plated drill file).
VIA_DRILLS = (0.2,)
FREE_PAD_DRILLS = ()
HOLE_DRILLS = (3.0,)
HOLES_PLATED = True

# Four SMD pads without a part (327 records with a blank refdes, 0.711 mm round, top: test pads),
# (x, y) -> raw IPC net. The shared tools treat them as SMD free pads (ipc356 --check, check_sources:
# SMDPad flashes; build_pcb: board-only FREE_PAD_FOOTPRINT, an SMD pad on F.Cu; gerber_to_tracks,
# check_board, ipc356_diff: exactly one SMD record per listed position).
SMD_FREE_PADS = {
    (72.9, -36.0): "JFET_6",
    (74.4, -36.0): "JFET_5",
    (86.7, -26.6): "GPIOL_10",
    (88.3, -26.6): "GPIOL_11",
}

# U10 balls: Proteus flashes them with the aperture function `BGAPad,CuDef` (treated as SMDPad by the
# shared tools); check_sources requires per copper layer the BGAPad flashes = the balls of U10, 1:1.
BGA_REFDES = "U10"

# Expected counts in the Proteus file (PLAN.md section 1).
EXPECTED_IPC = {
    "nets": 227,          # NNAME declarations
    "records": 1132,
    "refdes_raw": 147,    # distinct refdes fields, incl. the blank one of vias/holes/SMD test pads
    "tht_records": 377,   # 133 component pads + 240 vias + 4 holes
    "smd_records": 755,
    "smd_top": 557,       # 225 BGA balls (U10) + 328 SMD pads + 4 SMD test pads
    "smd_bottom": 198,
    "nc_pads": 76,        # 62 on U10, 14 elsewhere
    "vias": 240,          # 0.419 / 0.2 mm, no stacked duplicates
    "free_pads": 4,       # the SMD test pads (SMD_FREE_PADS)
    "holes": 4,
    "parts": 146,
}

# Proteus via records stacked on an already recorded via position: none on this board.
STACKED_VIAS = 0

# --- Gerbers (check_sources, later the PCB tools) ------------------------------------

# Proteus copper gerber name -> KiCad copper layer, User layer for the pour outlines.
COPPER = [
    ("Top Copper", "F.Cu", "User.1"),
    ("Inner  1", "In1.Cu", "User.2"),
    ("Inner  2", "In2.Cu", "User.3"),
    ("Bottom Copper", "B.Cu", "User.4"),
]
DRILL_PLATED = "Drill TOP-BOT Plated"
DRILL_NONPLATED = None          # Proteus wrote no non-plated drill file (no unplated holes)
OUTLINE = "Mechanical 1"
OUTLINE_RECT = (13.87, -42.75, 97.79, 55.88)  # x, y, width, height

# Excellon drill of the RS-274X export (same 377 hits as the X2 drill gerber, Phase 0).
DRILL_EXCELLON = "source/cadcam_rs274x/fpga_boardv2.5 - CADCAM Drill.DRL"

# --- Footprints (Phase 2: tools/generate/gen_footprints.py, p2k check_footprints) ----

# KiCad library pad sizes and drills; pad centres on the Proteus positions. Differences per refdes
# in STATUS.md "Phase 2 - pad sizes and drills" (open user decision for Phase 3 / 4).
FOOTPRINT_PAD_SIZES = "kicad"

# Board-only footprints for Phase 3 (p2k.build_pcb): the 4 plated 3.0 mm mounting holes and the
# 4 SMD test pads (IPC 'free_pad' records, SMD_FREE_PADS; the footprint is an SMD pad, spec smd_pad in
# tools/generate/gen_footprints.py).
HOLE_FOOTPRINT = "tube_control_card:MountingHole_3.0mm_PTH_Pad6.35mm"
HOLE_VALUE = "MountingHole_3.0mm_PTH"
FREE_PAD_FOOTPRINT = "tube_control_card:TestPad_SMD_D0.711mm"
FREE_PAD_VALUE = "TestPad"
FREE_PAD_PREFIX = "TP"

# tools/generate/gen_footprints.py (footprints.run) also writes / --checks kicad/fp-lib-table.
FP_LIB_TABLE = True
# THT parts mounted on the bottom side (p2k check_footprints: a THT pattern that fits only mirrored
# must be listed here, a listed part must fit only mirrored).
BOTTOM_THT = {"J3": "2x8 1.27 mm header on the bottom side (Proteus bottom assembly)"}

# --- PCB (Phase 3: tools/generate/make_pcb.sh (frozen), p2k build_pcb / pours_to_zones / drc)

# Board thickness: 1.6 mm (user decision 2026-11-20, finding 5; the CADCAM READ-ME stack of
# 2.34 mm is a Proteus default). Stack-up (agent's choice, a common 4-layer 1.6 mm build; only
# the total goes into the board, the copper layers are what the checks compare):
# F.Cu 0.035 / prepreg 0.2104 / In1.Cu 0.0152 / core 1.065 / In2.Cu 0.0152 / prepreg 0.2104 /
# B.Cu 0.035 = 1.586 mm + 2 x ~0.01 mm solder resist = 1.6 mm.
PCB_THICKNESS = 1.6
# Design rules from the Proteus copper as built (STATUS.md "Phase 3", tools/measure_gaps.py), mm.
# Proteus routed this board at 4 mil (0.1016) almost everywhere; 75 different-net pairs are
# closer than 0.1 mm, all on F.Cu (BGA fan-out, the TSSOP / resistor-array rows), down to
# 0.0754 (pad-track, track-via, ball-via: finding 4), so the clearance is 0.07.
PCB_RULES = dict(
    min_track=0.1,        # thinnest conductor draw 0.1016 (4 mil) on every layer
    min_via=0.4,          # all 240 vias 0.419 / 0.2
    min_annular=0.1,      # (0.419 - 0.2) / 2 = 0.1095
    min_drill=0.2,
    clearance=0.07,       # smallest different-net gap 0.0754 (F.Cu); 0.1016 on the inner layers / B.Cu
    hole_clearance=0.15,  # via drill to other-net copper >= 0.1095 annular + 0.0755
    hole_to_hole=0.25,    # smallest drill-to-drill 0.320 (two vias at the BGA)
    edge_clearance=0.4,   # copper to outline >= 0.4826 (In2.Cu pour)
    track=0.254,          # Default netclass
    via=0.419,
    via_drill=0.2,
)

# KiCad footprint drills smaller than the Proteus drill, accepted (ipc356_diff, gerber_roundtrip).
# (ipc356_diff, gerber_roundtrip: the accepted smaller drills of the pair must be exactly these pads)
DRILL_SMALLER = {
    (1.016, 1.0): ("J8 (KiCad PinHeader_1x03_P2.54mm 1.0 mm, Proteus 1.016 mm): user decision 2026-11-20",
                   {("J8", "1"), ("J8", "2"), ("J8", "3")}),
}

# Phase 4: the recorded ipc356_diff summary (STATUS.md "Phase 4"; since the design fixes of 2026-11-20
# the lone GPIOL_N_10 via is a REMOVED_VIAS entry: KiCad 1131 records, 239 vias, the Proteus record
# removed as recorded). The KiCad track draws per layer of the round trip (F 2132 / In1 72 / In2 221 /
# B 922 = gerber_to_tracks without the 26 REMOVED_TRACKS draws) are the strict check roundtrip_counts.
PHASE4_EXPECTED = dict(proteus=1132, kicad=1131, matched=1131, pads=884, nc=76, vias=239, holes=4, free=4, nets=227)

# Error-severity DRC types that remain by design ({type: reason}, STATUS.md "Phase 3").
DRC_ACCEPTED = {
    "courtyards_overlap": "KiCad IPC-7351 courtyards vs the Proteus placement (parts at the Proteus positions)",
}
# Exact DRC warning counts (since generation stopped, 2026-11-20): a hand edit must not add a dangling track /
# via or new silk conflicts unnoticed (the silk counts are the Phase 5 state, footprint body graphics).
DRC_EXPECTED_WARNINGS = {"track_dangling": 0, "via_dangling": 0, "silk_over_copper": 28, "silk_overlap": 11}

# Dangling Proteus copper (finding 26): REMOVED (user decision 2026-11-20, "Design fixes 2026-11-20";
# reverses Phase 5 decision 2). Every Proteus Conductor draw that KiCad's DRC flagged track_dangling, and
# every draw that dangles once those are gone (the rest of a stub that leads from one pad to nowhere),
# found iteratively with pcbnew's TestTrackEndpointDangling (scratch script build/tmp/fix26/find.py, not
# committed). Keys = the gerber draws exactly (IPC frame), in the drawn direction: a draw and its
# reverse (the zero-length / back-and-forth draws) are separate entries; p2k.pcb.removed_track
# matches the drawn direction first (1e-6 mm), so each entry takes exactly its own draw. 26 draws: F.Cu 20, B.Cu 6.
REMOVED_TRACKS = {
    # zero-length / back-and-forth draws (copper covered by the joined tracks)
    ("F.Cu", 41.8819, -8.86052, 41.87295, -8.86052): "GND 0.009 mm draw (out)",
    ("F.Cu", 41.87295, -8.86052, 41.8819, -8.86052): "GND 0.009 mm draw (back)",
    ("F.Cu", 62.34813, 3.70007, 62.35152, 3.69668): "ADASEL0_ISO 0.005 mm draw",
    ("B.Cu", 46.97032, -11.87033, 46.97032, -11.87032): "DATA2 1e-5 mm draw (out)",
    ("B.Cu", 46.97032, -11.87032, 46.97032, -11.87033): "DATA2 1e-5 mm draw (back)",
    # short stubs on nets that are connected elsewhere
    ("B.Cu", 94.6, 10.1, 94.6, 9.88143): "GND stub 0.22 mm at x 94.6",
    ("B.Cu", 94.6, 9.88143, 94.60143, 9.88): "GND stub 0.002 mm (end of the 0.22 mm stub)",
    ("B.Cu", 94.6, 7.1, 94.6, 7.22784): "5V stub 0.13 mm at x 94.6",
    ("B.Cu", 47.26658, -11.57406, 47.41318, -11.42747): "DATA2 stub 0.21 mm",
    ("F.Cu", 89.89728, -26.10272, 90.16045, -26.36589): "GPIOL_9 stub 0.37 mm",
    ("F.Cu", 79.15, -23.55, 79.3, -23.7): "GPIOL_10 0.21 mm draw back along its own track",
    # whole stubs of single-pin nets (one pad, copper to nowhere)
    ("F.Cu", 26.04813, -2.21034, 26.04813, -2.90577): "ADCLK_ISO stub from U9 B2 (1/3)",
    ("F.Cu", 26.04813, -2.90577, 26.50028, -3.35792): "ADCLK_ISO stub (2/3)",
    ("F.Cu", 26.50028, -3.35792, 26.50028, -5.8): "ADCLK_ISO stub (3/3, open end)",
    ("F.Cu", 26.69813, -2.21034, 26.69813, -3.00633): "GPIO_BYPASS_RLY_ISOLATED stub from U9 B1 (1/3)",
    ("F.Cu", 26.69813, -3.00633, 26.89983, -3.20803): "GPIO_BYPASS_RLY_ISOLATED stub (2/3)",
    ("F.Cu", 26.89983, -3.20803, 26.89983, -5.8): "GPIO_BYPASS_RLY_ISOLATED stub (3/3, open end)",
    ("F.Cu", 40.92313, -18.26034, 40.92313, -18.62313): "GPIOL_N_18 track from U10 A2 to nowhere (1/8)",
    ("F.Cu", 40.92313, -18.62313, 42.5, -20.2): "GPIOL_N_18 (2/8)",
    ("F.Cu", 42.5, -20.2, 59.20001, -20.2): "GPIOL_N_18 (3/8)",
    ("F.Cu", 59.20001, -20.2, 60.00001, -19.4): "GPIOL_N_18 (4/8)",
    ("F.Cu", 60.00001, -19.4, 77.2, -19.4): "GPIOL_N_18 (5/8)",
    ("F.Cu", 77.2, -19.4, 81.04593, -23.24593): "GPIOL_N_18 (6/8)",
    ("F.Cu", 81.04593, -23.24593, 88.35363, -23.24593): "GPIOL_N_18 (7/8)",
    ("F.Cu", 88.35363, -23.24593, 92.5, -27.3923): "GPIOL_N_18 (8/8, open end)",
    ("F.Cu", 40.92313, -14.36034, 40.58081, -14.01802): "GPIOL_N_10 track from U10 G2 to the lone via",
}
# The lone GPIOL_N_10 via (ball G2 + this via, nothing on the other layers; finding 2 / 26).
REMOVED_VIAS = {
    (40.5808, -14.018): "GPIOL_N_10 via: connected only to ball G2 on F.Cu (removed with its track)",
}

# --- Pin order (Phase 2: p2k check_pin_order) ----------------------------------------
# The UNMOVED KiCad base footprints with the Proteus renumbering (rule= takes the footprint of the
# symbol's RULES rule in tools/generate/gen_footprints.py: a project footprint as its base + renumber), fitted
# onto the IPC pads. SMD parts must fit with the mirror of their IPC side (bottom = mirrored), THT
# parts with the mirror of their side on the Proteus assembly layers (all on top except J3). U10 also
# checks the fitted angle (180 deg). Two-pad / inline parts and dual-row SMD packages are symmetric
# under a 180 deg turn: the nets (Phase 1) and the --render overlays decide (STATUS.md "Phase 2 - pin
# order"). Footprints built from the IPC pads only (blade terminals, IZB03, X2QFN-8 AD2) have no base.
# The generators are frozen in tools/generate/ (generation stopped 2026-11-20); check_pin_order imports the
# RULES from there (read only, nothing is written).
FOOTPRINT_SCRIPT = "tools/generate/gen_footprints.py"
PIN_ORDER = [
    dict(name="U10 BGA", refs="U10", rule="TI60F225", mirror=False, res=0.001, angle=180.0,
         note="ball ids = KiCad pad names, A1-top-left footprint at 180 deg"),
    dict(name="ADC1", refs="ADC1", rule="ADC121C027", mirror=False, res=0.19,
         note="A1 A2 COM2 K2 K1 COM1 = JEDEC 1-6: fits (rows 2.65 vs KiCad 2.275 -> 0.1875)"),
    dict(name="ADC1 datasheet", refs="ADC1", footprint="Package_TO_SOT_SMD:SOT-23-6",
         renumber={"1": "COM2", "2": "A2", "3": "A1", "4": "COM1", "5": "K1", "6": "K2"}, mirror=None,
         note="VA / VIN exchanged (COM2 on pad 1, A1 on pad 3, the datasheet wiring): fits only mirrored, "
              "i.e. not on a top-side part; so the land pattern is right and finding 9 was fixed in the nets "
              "(hand edit 2026-11-20: 3V3 on A1 = VA, the R34 / C68 node on COM2 = VIN)"),
    dict(name="SOT-23-5", refs="U4 V4", rule="TLV316IDBVR", mirror=True, res=0.07, note="bottom side, rows 2.39 vs 2.30"),
    dict(name="SC-70-6", refs="U12", rule="AD5622", mirror=False, res=0.07, note="rows 1.80 vs 1.675"),
    dict(name="SOT-563", refs="PWR1 PWR2 PWR3", rule="AP61202", mirror=True, res=0.08, note="bottom side, rows 1.27 vs 1.425"),
    dict(name="TSSOP-14", refs="U5 U6 U11 U14", rule="TLV9304PWR", mirror=False, res=0.07, note="rows 5.85 vs 5.725"),
    dict(name="TSSOP-24", refs="U1 U2 U7 U8 U9", rule="SN74AXC8T245", mirror=False, res=0.02,
         note="KiCad pad positions (Proteus pad size, PROTEUS_PADS)"),
    dict(name="TSSOP-16", refs="U3", rule="SN74LV4051", mirror=True, res=0.02,
         note="bottom side, KiCad pad positions (Proteus pad size)"),
    dict(name="R array", refs="R14 R15 R17 R18 R22 R23 R24 R25", rule="R_ARRAY4", mirror=False, res=0.06,
         note="rows 0.95 vs 1.0"),
    dict(name="OSC1", refs="OSC1", rule="MC2016K_OSC", mirror=False, res=0.16, note="pads 1.8 x 1.2 vs KiCad 1.5 x 1.1"),
    dict(name="SO8W RS1", refs="RS1", rule="MAX22025", mirror=False, res=0.76, note="rows 9.14 vs KiCad 10.65"),
    dict(name="SO8W FLASH1", refs="FLASH1", rule="W25Q64JWSSIQ", mirror=False, res=0.99, note="rows 9.14 vs KiCad 7.175"),
    dict(name="J11", refs="J11", rule="HEADER_2X20_50MIL", mirror=False, res=0.01,
         note="standard numbering (IPC_PIN_IDS) fits on top"),
    dict(name="J3", refs="J3", rule="HEADER_2X8_50MIL", mirror=True, res=0.01,
         note="standard numbering, fits mirrored: J3 is a bottom-side part (Proteus bottom assembly)"),
    dict(name="J6", refs="J6", rule="HEADER_2X8_50MIL", mirror=False, res=0.01, note="standard numbering fits on top"),
    dict(name="J7", refs="J7", rule="HEADER_2X15_50MIL", mirror=False, res=0.01, note="standard numbering fits on top"),
    dict(name="J1", refs="J1", rule="TBLOCK-I5", mirror=False, res=0.01, note="inline: body side by render"),
    dict(name="J8", refs="J8", rule="CONN_01X03", mirror=False, res=0.01, note="inline"),
]
