"""proteus2kicad configuration of the fpga_boardv2.5 board (tools in tools/p2k, see its README).

Plain Python; every value here is specific to this board. Coordinates in mm, IPC frame (Y up).
Keys marked "board-local" are read only by this repo's tools/ (not by tools/p2k).
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

# --- IPC-D-356A fix-ups (ipc356) -----------------------------------------------------

# No truncated refdes: the three 6-character IPC refdes (FLASH1, RS485A, RS485B) are the
# full names printed in the PDF (pages 2 and 11), and every IPC refdes occurs in the PDF.
TRUNCATED_REFDES = {}
TRUNCATED_NETS = {}

# Every Proteus refdes is usable in KiCad ([A-Za-z][A-Za-z0-9_]*: ISO_G, ISO5V, RS485A ...).
KICAD_REFDES = {}

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

# Board-local (tools/ipc356_check.py): two-pad terminals whose two pads (both pin 1) carry
# different IPC nets; accepted exactly in the "same refdes-pin on different nets" self-check.
# Raw IPC net names, in IPC file order.
SPLIT_PIN_NETS = {
    ("J2", "1"): ("5V.00026", "5V.00301"),
    ("ISO5V", "1"): ("ISO5V.00299", "ISO5V.00255"),
    ("ISO_G", "1"): ("RS485_GND.00300", "RS485_GND.00256"),
    ("RS485A", "1"): ("#00670.00259", "#00670.00260"),
    ("RS485B", "1"): ("#00671.00261", "#00671.00262"),
}

# Decision D1 (user, 2026-11-20; STATUS.md "Decisions"): each split terminal is drawn as one
# pin 1, as in the PDF, so KiCad puts both pads on one net. Board-local
# (tools/compare_netlists.py, later the PCB checks): the accepted net merges, pin ->
# (kept IPC net, merged IPC net), IPC names after NET_ALIASES. Exactly these five; on RS485B
# the merged net also carries R67-1 (the PDF draws R67 on the RS485 B node).
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

# Board-local (tools/ipc356_check.py, tools/check_sources.py): four SMD pads without a part
# (327 records with a blank refdes, 0.711 mm round, top: test pads). p2k ipc356 classifies them
# as `free_pad` (its self-check wants a plated drill) and p2k check_sources expects free pads
# as OtherPad flashes + drills; the wrappers accept exactly these (x, y) -> raw IPC net.
SMD_FREE_PADS = {
    (72.9, -36.0): "JFET_6",
    (74.4, -36.0): "JFET_5",
    (86.7, -26.6): "GPIOL_10",
    (88.3, -26.6): "GPIOL_11",
}

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
