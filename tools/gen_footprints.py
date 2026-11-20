#!/usr/bin/env python3
"""Footprint assignment and the project footprint library of the control card (stdlib only).

Writes (through the shared generator tools/p2k/p2k/footprints.py)
  lib/footprint_map.csv           refdes -> footprint for all 146 parts of lib/part_map.csv
  lib/tube_control_card.pretty/   project footprints: derived from KiCad library footprints (pads
                                  renumbered to the Proteus ids, pad centres moved onto the Proteus
                                  positions), built from the IPC-D-356A pads where KiCad has nothing,
                                  and the board-only footprints of Phase 3 (mounting hole, SMD test pad)
  kicad/fp-lib-table              registers the project library (p2k_config.py FP_LIB_TABLE = True)

Usage: python3 tools/gen_footprints.py [--check]      (needs the KiCad AppImage mount)

This file holds what is decided for this board: RULES (symbol + IPC pad pattern -> footprint) and
PROJECT (the project footprint specs); the rule syntax and the spec keys are documented in
tools/p2k/p2k/footprints.py. Pad numbers always equal the IPC pin ids (U10: ball ids A1..R15).

Pad sizes: p2k_config.py FOOTPRINT_PAD_SIZES = "kicad" (KiCad library pads and drills; the
footprints built from the IPC pads - blade terminals, IZB03, X2QFN-8, SMD test pad - have the
Proteus pads), except the PROTEUS_PADS parts (user decision, Phase 3: "_ProteusPads" specs with
ipc_sizes=True, Proteus pad size and drill). tools/p2k check_footprints verifies every footprint against the IPC pads (residual
< 0.05 mm per pad) and reports the pad size / drill differences (STATUS.md "Phase 2").

The SMD test pad is a board-only spec with `smd_pad=(diameter, side)` (p2k.footprints).
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools", "p2k"))  # proteus2kicad
from p2k import footprints  # noqa: E402

P = "tube_control_card:"

# Phase 3 pad-size decision (user, 2026-11-20, option A; STATUS.md "Phase 3 - pad sizes",
# Decisions): these 15 parts get the Proteus pad sizes (J7 / J11 also the Proteus drill 0.558 mm)
# because their KiCad pads short or come closer than the clearance to the Proteus tracks / vias
# (DRC with KiCad pads: 13 shorts, 85 clearance, 17 solder-mask bridges, 2 hole clearance, all at
# these parts). Every other part keeps the KiCad pads (U10 keeps the KiCad 0.28 mm balls). The
# rules with `refdes=PROTEUS_PADS` come before the general rule of their symbol (where one is left);
# p2k.footprints fails if a refdes listed here is taken by no such rule.
PROTEUS_PADS = frozenset("""
    U1 U2 U3 U5 U6 U7 U8 U9 U11 U14 ADC1 U4 U12 J7 J11
""".split())

# (symbol, conditions, footprint, note). Conditions: n = pad count, tht, span (mm, +-0.02),
# pad = (w, h) of the IPC pads, drill, package / device (lib/part_map.csv columns), refdes.
RULES = [
    # --- resistors
    ("R", dict(tht=False, span=0.70, pad=(0.406, 0.457)), "Resistor_SMD:R_0201_0603Metric", "0201 (CAPC0603X33 pads)"),
    ("R", dict(tht=False, span=1.00, pad=(0.558, 0.609)), "Resistor_SMD:R_0402_1005Metric", "0402 (RESC1005X40)"),
    ("R", dict(tht=False, span=3.15, pad=(1.016, 1.524)), "Resistor_SMD:R_1206_3216Metric_Pad1.30x1.75mm_HandSolder",
     "1206 (Proteus 1206_RES, pads 3.15 mm apart)"),
    ("R_ARRAY4", dict(), P + "R_Array_Convex_4x0402_Proteus", "4 x 0402 array (2 x 1 mm), Proteus pad rows 0.95 mm apart"),
    # --- capacitors, inductors
    ("C", dict(tht=False, span=0.70, pad=(0.406, 0.457)), "Capacitor_SMD:C_0201_0603Metric", "0201 (CAPC0603X33)"),
    ("C", dict(tht=False, span=0.90, pad=(0.609, 0.609)), "Capacitor_SMD:C_0402_1005Metric", "0402 (CAPC1005X55)"),
    ("C", dict(tht=False, span=1.60, pad=(0.939, 0.99)), "Capacitor_SMD:C_0603_1608Metric", "0603 (CAPC1608X87)"),
    ("C", dict(tht=False, span=3.00, pad=(1.143, 1.803)), "Capacitor_SMD:C_1206_3216Metric", "1206 (CAPC3216X140)"),
    ("L", dict(tht=False, span=2.077, pad=(1.016, 1.524)), "Inductor_SMD:L_0805_2012Metric", "0805 (IND805)"),
    # --- ICs
    ("TI60F225", dict(), "Package_BGA:TFBGA-225_10x10mm_Layout15x15_P0.65mm",
     "Efinix Ti60F225 (BGA225C65P15X15), ball ids = pad names; placed at 180 deg"),
    ("SN74AXC8T245", dict(refdes=PROTEUS_PADS), P + "TSSOP-24_4.4x7.8mm_P0.65mm_ProteusPads",
     "TSSOP-24, Proteus pad size"),
    ("SN74LV4051", dict(refdes=PROTEUS_PADS), P + "TSSOP-16_4.4x5mm_P0.65mm_ProteusPads", "TSSOP-16, Proteus pad size"),
    ("TLV9304PWR", dict(refdes=PROTEUS_PADS), P + "TSSOP-14_4.4x5mm_P0.65mm_Proteus_ProteusPads",
     "TSSOP-14, Proteus pad rows 5.85 mm apart, Proteus pad size"),
    ("TL084HIDYYR", dict(refdes=PROTEUS_PADS), P + "TSSOP-14_4.4x5mm_P0.65mm_Proteus_ProteusPads",
     "TSSOP-14, Proteus pad rows 5.85 mm apart, Proteus pad size"),
    ("TLV316IDBVR", dict(refdes=PROTEUS_PADS), P + "SOT-23-5_Proteus_ProteusPads",
     "SOT-23-5, Proteus pad rows 2.39 mm apart, Proteus pad size"),
    ("TPS73030", dict(), P + "SOT-23-5_Proteus", "SOT-23-5, Proteus pad rows 2.39 mm apart"),
    ("ADC121C027", dict(refdes=PROTEUS_PADS), P + "SOT-23-6_ADC121C027_Proteus_ProteusPads",
     "SOT-23-6, Proteus pin ids A1 A2 COM2 K2 K1 COM1 = pads 1-6, rows 2.65 mm apart (finding 9), Proteus pad size"),
    ("AD5622", dict(refdes=PROTEUS_PADS), P + "SOT-363_SC-70-6_Proteus_ProteusPads",
     "SC-70-6, Proteus pad rows 1.8 mm apart, Proteus pad size"),
    ("AP61202", dict(), P + "SOT-563_Proteus", "SOT-563, Proteus pad rows 1.27 mm apart (pin 6 = PG, finding 12)"),
    ("ADS7056", dict(), P + "Texas_X2QFN-8_RUG_1.5x1.5mm_P0.5mm", "X2QFN-8 (TI RUG), Proteus land pattern"),
    ("MC2016K_OSC", dict(), P + "Oscillator_SMD_2.0x1.6mm_Proteus", "2.0 x 1.6 mm oscillator, Proteus pad positions"),
    ("MAX22025", dict(), P + "SOIC-8_7.5x5.85mm_P1.27mm_Proteus", "wide SOIC-8 (Proteus SO8W), pad rows 9.14 mm apart"),
    ("W25Q64JWSSIQ", dict(), P + "SOIC-8_5.3x5.3mm_P1.27mm_Proteus",
     "208 mil SOIC-8 on the Proteus SO8W pattern (pad rows 9.14 mm apart, finding 24)"),
    ("IZB03", dict(), P + "Converter_IZB03_SIP7", "IZB03 isolated DC/DC, 7 pins (SIP-8 with pin 4 position empty)"),
    # --- connectors, terminals
    ("HEADER_2X20_50MIL", dict(refdes=PROTEUS_PADS), P + "PinHeader_2x20_P1.27mm_Vertical_ProteusPads",
     "2x20 1.27 mm header (IDC), standard numbering (IPC_PIN_IDS: Proteus rows swapped, finding 25), pins 37 / 38 N/C, "
     "Proteus pad size and drill"),
    ("HEADER_2X15_50MIL", dict(refdes=PROTEUS_PADS), P + "PinHeader_2x15_P1.27mm_Vertical_ProteusPads",
     "2x15 1.27 mm header, Proteus pad size and drill"),
    ("HEADER_2X8_50MIL", dict(), "Connector_PinHeader_1.27mm:PinHeader_2x08_P1.27mm_Vertical",
     "2x8 1.27 mm header (J3 on the bottom side, J6 on top)"),
    ("CONN_01X03", dict(), "Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical", "1x3 2.54 mm (FCI)"),
    ("TBLOCK-I5", dict(), "TerminalBlock_Phoenix:TerminalBlock_Phoenix_MPT-0,5-5-2.54_1x05_P2.54mm_Horizontal",
     "5-pin terminal block, P2.54"),
    ("TERMINAL", dict(n=2), P + "Terminal_2x1_P5.00mm_D2.0mm_Drill1.4mm", "blade terminal, two holes both pad 1 (D1)"),
]

# Project footprints (spec keys: see p2k.footprints). `ipc` = refdes whose IPC pads give the pad
# centres; the footprint is built for the top side and mirrored by placement when needed.
PROJECT = {
    # KiCad's MNR04 pad rows are 1.0 mm apart, Proteus 0.95: 0.056 mm off -> derived, pads moved
    "R_Array_Convex_4x0402_Proteus": dict(
        base="Resistor_SMD:R_Array_Convex_4x0402", ipc="R14",
        descr="4 x 0402 resistor array (convex), Proteus pad rows 0.95 mm apart"),
    # Phase 3 pad decision (PROTEUS_PADS): `_ProteusPads` = ipc_sizes=True (Proteus pad size and
    # drill, pad centres from the IPC pads). The KiCad-pad specs no part uses any more (TSSOP-14,
    # ADC121C027, SC-70-6, the 2x20 header) were dropped; SOT-23-5_Proteus stays for V4.
    "TSSOP-24_4.4x7.8mm_P0.65mm_ProteusPads": dict(
        base="Package_SO:TSSOP-24_4.4x7.8mm_P0.65mm", ipc="U1", ipc_sizes=True,
        descr="TSSOP-24, Proteus pad sizes"),
    "TSSOP-16_4.4x5mm_P0.65mm_ProteusPads": dict(
        base="Package_SO:TSSOP-16_4.4x5mm_P0.65mm", ipc="U3", ipc_sizes=True,
        descr="TSSOP-16, Proteus pad sizes"),
    "TSSOP-14_4.4x5mm_P0.65mm_Proteus_ProteusPads": dict(
        base="Package_SO:TSSOP-14_4.4x5mm_P0.65mm", ipc="U5", ipc_sizes=True,
        descr="TSSOP-14, Proteus pad positions (rows 5.85 mm apart); Proteus pad sizes"),
    "SOT-23-5_Proteus": dict(
        base="Package_TO_SOT_SMD:SOT-23-5", ipc="U4",
        descr="SOT-23-5, Proteus pad positions (rows 2.39 mm apart)"),
    "SOT-23-5_Proteus_ProteusPads": dict(
        base="Package_TO_SOT_SMD:SOT-23-5", ipc="U4", ipc_sizes=True,
        descr="SOT-23-5, Proteus pad positions (rows 2.39 mm apart); Proteus pad sizes"),
    # ADC121C027 with the Proteus pin ids (diode-array style names): JEDEC pads 1-6 =
    # A1 A2 COM2 K2 K1 COM1 (check_pin_order confirms; finding 9 for what that means)
    "SOT-23-6_ADC121C027_Proteus_ProteusPads": dict(
        base="Package_TO_SOT_SMD:SOT-23-6",
        renumber={"1": "A1", "2": "A2", "3": "COM2", "4": "K2", "5": "K1", "6": "COM1"}, ipc="ADC1", ipc_sizes=True,
        descr="SOT-23-6 (ADC121C027), Proteus pin ids A1 A2 COM2 K2 K1 COM1 on pads 1-6, "
              "Proteus pad positions (rows 2.65 mm apart); Proteus pad sizes"),
    "SOT-363_SC-70-6_Proteus_ProteusPads": dict(
        base="Package_TO_SOT_SMD:SOT-363_SC-70-6", ipc="U12", ipc_sizes=True,
        descr="SC-70-6, Proteus pad positions (rows 1.8 mm apart); Proteus pad sizes"),
    "SOT-563_Proteus": dict(
        base="Package_TO_SOT_SMD:SOT-563", ipc="PWR1",
        descr="SOT-563, Proteus pad positions (rows 1.27 mm apart)"),
    # KiCad has no TI RUG (X2QFN-8, 1.5 x 1.5 mm): built from the IPC pads of AD2 (bottom side)
    "Texas_X2QFN-8_RUG_1.5x1.5mm_P0.5mm": dict(
        ipc="AD2", body=(1.5, 1.5),
        descr="TI RUG X2QFN-8 1.5 x 1.5 mm (ADS7056), Proteus land pattern"),
    "Oscillator_SMD_2.0x1.6mm_Proteus": dict(
        base="Oscillator:Oscillator_SMD_SiT_PQFN-4Pin_2.0x1.6mm", ipc="OSC1",
        descr="2.0 x 1.6 mm 4-pad oscillator (MC2016K), Proteus pad positions (1.8 x 1.2 mm)"),
    "SOIC-8_7.5x5.85mm_P1.27mm_Proteus": dict(
        base="Package_SO:SOIC-8_7.5x5.85mm_P1.27mm", ipc="RS1", max_move=0.8,  # pad 8 moves 0.753 mm (intended)
        descr="wide SOIC-8 (MAX22025), Proteus pad positions (rows 9.14 mm apart, KiCad 10.65)"),
    "SOIC-8_5.3x5.3mm_P1.27mm_Proteus": dict(
        base="Package_SO:SOIC-8_5.3x5.3mm_P1.27mm", ipc="FLASH1", max_move=1.0,  # rows move 0.985 mm (intended)
        descr="208 mil SOIC-8 (W25Q64JW-SS), Proteus SO8W pad positions (rows 9.14 mm apart, KiCad 7.175)"),
    "Converter_IZB03_SIP7": dict(
        ipc="PWR4", descr="IZB03 isolated DC/DC module, 7 pins at 2.54 mm (pin 4 position empty), Proteus pads"),
    # J11: Proteus numbers the IDC header as the mirror image of a standard header seen from the top (odd /
    # even rows swapped; finding 25). Since 2026-11-20 (user decision, D-PIN, together with tube_hv_supplies J1)
    # the board uses the standard numbering: p2k_config.IPC_PIN_IDS renames the IPC pins (Proteus k -> k + 1 for
    # odd k, k - 1 for even k), so the stock header fits unmirrored; its square pad 1 is KiCad's pin-1 position,
    # where the Proteus pin 2 pad was square already (copper unchanged).
    "PinHeader_2x20_P1.27mm_Vertical_ProteusPads": dict(
        base="Connector_PinHeader_1.27mm:PinHeader_2x20_P1.27mm_Vertical", ipc="J11", ipc_sizes=True,
        descr="2x20 1.27 mm header, standard numbering; Proteus pad sizes and drill"),
    "PinHeader_2x15_P1.27mm_Vertical_ProteusPads": dict(
        base="Connector_PinHeader_1.27mm:PinHeader_2x15_P1.27mm_Vertical", ipc="J7", ipc_sizes=True,
        descr="2x15 1.27 mm header, Proteus pad sizes and drill"),
    "Terminal_2x1_P5.00mm_D2.0mm_Drill1.4mm": dict(
        ipc="J2", descr="Blade wire terminal, two holes both pad 1"),
    # Board-only (no symbol; placed by p2k.build_pcb in Phase 3)
    "MountingHole_3.0mm_PTH_Pad6.35mm": dict(
        board_only=True, pad=(6.35, 3.0), plated=True,
        descr="Plated 3.0 mm mounting hole with a 6.35 mm pad on all copper layers, no net"),
    "TestPad_SMD_D0.711mm": dict(
        board_only=True, smd_pad=(0.711, "F"),
        descr="SMD test pad, 0.711 mm round, top copper (the 4 Proteus SMD pads without a part)"),
}

if __name__ == "__main__":
    footprints.run(RULES, PROJECT)
