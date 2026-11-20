#!/usr/bin/env python3
"""Generate lib/tube_control_card.kicad_sym, the project symbol library (helpers: p2k.symgen).

Pin numbers equal the Proteus/IPC pin ids. Box symbols carry the Proteus pin names of the
device pinouts in ROOT.DSN (STATUS.md "Phase 1 preparation"); the U10 symbol (Efinix
Ti60F225, 225 balls, units A-H as in the PDF) is generated from the DSN pinout
`*PINOUT BGA225C65P15X15` read by `ti60_pinout()` below (p2k.pdsprj.dsn_pinouts misses it:
its PIN lines do not start with "{", STATUS.md p2k candidates). Simple symbols are copied
from the KiCad 10 standard library (flattened, pins renumbered). Power symbols carry the IPC
net names of the rails drawn as Proteus power terminals.

Run:  tools/gen_symbols.py           (needs the AppImage mount for the std libs)
      tools/gen_symbols.py --check   (fail if lib/tube_control_card.kicad_sym is not up to date)
"""
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "p2k"))  # proteus2kicad
from p2k import board, pdsprj  # noqa: E402
from p2k.symgen import *  # noqa: E402,F401,F403
from p2k.symgen import run  # noqa: E402

PRJ = board.path("source", "fpga_boardv2.5.pdsprj")

GROUNDS = ["GND", "RS485_GND"]
SUPPLIES = ["1V", "1V8", "3V3", "5V", "12V", "AD_3V3", "ISO5V", "OPAMP_-15V"]

NC, BI = "no_connect", "bidirectional"


# ---------------------------------------------------------------- U10 (Ti60F225)

def ti60_pinout():
    """{ball: (Proteus pin name, unit letter)} from the BGA225 pinout of ROOT.DSN.

    Lines look like `PIN "GPIOL_N_03_CDI1" = *,*,L1,*,*,*,*,*}` (8 elements = units A-H). The
    DSN holds eight identical copies; all must agree and cover 225 distinct balls."""
    lines = pdsprj._strings(pdsprj._read(PRJ, "ROOT.DSN"))
    copies = []
    for i, line in enumerate(lines):
        if line != "*PINOUT BGA225C65P15X15":
            continue
        pins = {}
        j = i + 1
        while j < len(lines) and (lines[j].startswith("{") or lines[j].startswith("PIN ")):
            m = re.match(r'\{?PIN "(.*)" = ([^}]*)\}', lines[j])
            if m:
                pins[m.group(1)] = m.group(2).split(",")
            j += 1
        copies.append(pins)
    assert copies and all(c == copies[0] for c in copies), "ti60_pinout: DSN copies differ"
    balls = {}
    for name, elems in copies[0].items():
        assert len(elems) == 8, (name, elems)
        for u, b in enumerate(elems):
            if b != "*":
                assert b not in balls, f"ti60_pinout: ball {b} twice"
                balls[b] = (re.sub(r"\{\{\d+\}\}$", "", name), "ABCDEFGH"[u])
    assert len(balls) == 225, len(balls)
    return balls


def ballkey(b):
    return (b[0], int(b[1:]))


def gpio_key(name):
    m = re.match(r"GPIO[LRTB]_(?:([PN])_)?(\d+)", name)
    return (int(m.group(2)), {"P": 0, "N": 1}.get(m.group(1), 0))    # P before N, as in the PDF


def ti60_type(name):
    if name.startswith("GPIO") or name == "CDONE":
        return BI
    if name.startswith(("VCC", "GND")):
        return PI
    if name.startswith("REF_RES"):
        return PAS
    return OUT if name == "TDO" else IN    # CRESET_N, TCK, TDI, TMS


# first index on the right-hand side of the IO bank units (as drawn in the PDF)
SPLIT = {"C": 10, "D": 10, "E": 9, "F": 8}
POWER_LEFT = [["VCC"], ["VCCIO33_BL", "VCCIO33_BR", "VCCIO33_TL", "VCCIO33_TR"], ["VCCIO1A", "VCCIO1B"],
              ["VCCIO2A", "VCCIO2B"], ["VCCIO3A", "VCCIO3B"], ["VCCIO4A", "VCCIO4B"]]
POWER_RIGHT = [["VCCAUX"], ["VCCA_BL", "VCCA_BR", "VCCA_TL", "VCCA_TR"], ["REF_RES_1A1", "REF_RES_1B1"],
               ["REF_RES_2A1", "REF_RES_2B1"], ["REF_RES_3A1", "REF_RES_3B1"], ["REF_RES_4A1", "REF_RES_4B1"]]


def ti60_units():
    """[(left, right)] for units A-H: lists of (ball, name, type), None = gap (PDF order)."""
    balls = ti60_pinout()
    by_unit = {}
    for b, (name, u) in balls.items():
        by_unit.setdefault(u, []).append((b, name))
    pin = lambda b, n: (b, n, ti60_type(n))

    def groups(unit, spec):
        out = []
        for grp in spec:
            if out:
                out.append(None)
            for n in grp:
                out += [pin(b, nm) for b, nm in sorted(by_unit[unit], key=lambda p: ballkey(p[0])) if nm == n]
        return out

    units = []
    for u in "ABCDEFGH":
        pins = by_unit[u]
        if u == "A":
            order = ["CDONE", "CRESET_N", None, "TCK", "TDI", "TDO", "TMS"]
            name_ball = {n: b for b, n in pins}
            units.append(([], [pin(name_ball[n], n) if n else None for n in order]))
        elif u == "B":
            srt = sorted(pins, key=lambda p: gpio_key(p[1]))
            units.append(([pin(b, n) for b, n in srt if n.startswith("GPIOL")],
                          [pin(b, n) for b, n in srt if n.startswith("GPIOR")]))
        elif u in SPLIT:
            srt = sorted(pins, key=lambda p: gpio_key(p[1]))
            units.append(([pin(b, n) for b, n in srt if gpio_key(n)[0] < SPLIT[u]],
                          [pin(b, n) for b, n in srt if gpio_key(n)[0] >= SPLIT[u]]))
        elif u == "G":
            units.append((groups("G", POWER_LEFT), groups("G", POWER_RIGHT)))
        else:  # H: the GND balls
            units.append(([], [pin(b, n) for b, n in sorted(pins, key=lambda p: ballkey(p[0]))]))
    placed = [p[0] for left, right in units for p in left + right if p]
    assert sorted(placed) == sorted(balls), "ti60_units: every ball on exactly one unit"
    return units


def multi_box(name, ref, units, desc):
    """Multi-unit box symbol: unit k = symgen.box(left, right) body k (own rectangle)."""
    bodies = [box(name, ref, left, right) for left, right in units]
    sym = bodies[0]
    subs = []
    for k, b in enumerate(bodies, 1):
        rect = find(next(s for s in find_all(b, "symbol") if s[1] == f"{name}_0_1"), "rectangle")
        pins = find_all(next(s for s in find_all(b, "symbol") if s[1] == f"{name}_1_1"), "pin")
        subs.append([Sym("symbol"), f"{name}_{k}_1", rect, *pins])
    head = [c for c in sym if not (isinstance(c, list) and c[0] in ("symbol", "embedded_fonts"))]
    set_prop(head, "Description", desc)
    # Reference above the tallest body, Value below the deepest one (fields are per symbol,
    # not per unit): never over the pin names; sheet scripts place them per unit (ref_at / value_at).
    for key, pick in (("Reference", max), ("Value", min)):
        best = pick((find(next(p for p in find_all(b, "property") if p[1] == key), "at") for b in bodies),
                    key=lambda at: float(at[2]))
        prop = next(p for p in find_all(head, "property") if p[1] == key)
        prop[3] = list(best)
    return head + subs + [[Sym("embedded_fonts"), Sym("no")]]


# ---------------------------------------------------------------- library

def build():
    syms = [
        from_std("Device", "R", "R", "R", "R"),
        from_std("Device", "C", "C", "C", "C"),
        from_std("Device", "L", "L", "L", "L"),
        from_std("Device", "R_Pack04_Split", "R_ARRAY4", "R",
                 desc="4-resistor array 0508, units A-D = pins 1-8, 2-7, 3-6, 4-5 (Proteus RESISTOR ARRAY 2X1MM)"),
        from_std("Connector", "TestPoint", "TERMINAL", "J", "TERMINAL",
                 desc="Proteus TERMINAL (blade connector): one pin 1, the footprint has two pads numbered 1 "
                      "(decision D1: both pads on one net)"),
        from_std("Connector_Generic", "Conn_01x05", "TBLOCK-I5", "J", desc="5-pin terminal block (JTAG)"),
        from_std("Connector_Generic", "Conn_01x03", "CONN_01X03", "J", desc="3-pin connector (CON3_1X3_U_FCI)"),
        from_std("Amplifier_Operational", "MCP6L91T-EOT", "TLV316IDBVR", "U",
                 desc="Op-amp SOT-23-5, Proteus 1=OP 2=V- 3=+IN 4=-IN 5=V+"),
        from_std("Amplifier_Operational", "TLV9304xPW", "TLV9304PWR", "U",
                 desc="Quad op-amp TSSOP-14, units A-D as in the PDF, unit E = power (4 V+, 11 V-)"),
        from_std("Amplifier_Operational", "TL084", "TL084HIDYYR", "U",
                 desc="Quad op-amp TSSOP-14, units A-D as in the PDF, unit E = power (4 V+, 11 V-)"),
    ]

    syms += [
        box("ADS7056", "AD", [(6, "AVDD", PI), (4, "DVDD", PI), (7, "AINP", IN), (8, "AINM", IN)],
            [(1, "~{CS}", IN), (3, "SCLK", IN), (2, "SDO", OUT), (5, "GND", PI)],
            desc="14-bit ADC X2QFN-8, Proteus pin ids"),
        # Proteus pin ids of this SOT-26 device are diode-style (A1 A2 COM1 COM2 K1 K2). As drawn,
        # VIN is on 3V3 and VA on the analog input (STATUS.md findings): both passive so that ERC
        # does not flag the signal net as an undriven power pin.
        box("ADC121C027", "ADC", [("K1", "SCL", IN), ("COM1", "SDA", BI), ("K2", "ADR0", IN)],
            [("COM2", "VIN", PAS), ("A1", "VA", PAS), ("A2", "GND", PI)],
            desc="12-bit I2C ADC SOT-6; Proteus ids VA=A1 GND=A2 SDA=COM1 VIN=COM2 SCL=K1 ADR0=K2"),
        box("AD5622", "U", [(2, "SCL", IN), (3, "SCA", BI), (1, "ADDR", IN)],
            [(4, "VA", PI), (6, "VOUT", OUT), (5, "GND", PI)], desc="12-bit I2C DAC SC70-6, Proteus pin ids"),
        box("W25Q64JWSSIQ", "U", [(1, "~{CS}", IN), (2, "DATA1", BI), (3, "DATA2", BI), (4, "GND", PI)],
            [(8, "VCC", PI), (7, "DATA3", BI), (6, "DCLK", IN), (5, "DATA0", BI)],
            desc="1.8 V SPI flash SOIC-8 208 mil, Proteus pin names"),
        box("MC2016K_OSC", "OSC", [(1, "EN", IN), (4, "VCC", PI)], [(3, "OUT", OUT)], bottom=[(2, "GND", PI)],
            desc="Oscillator 2016, Proteus pin ids"),
        box("AP61202", "U", [(3, "VIN", PI), (5, "EN", IN), (1, "FB", IN)],
            [(4, "SW", OUT), (6, "VOUT", PAS), (2, "GND", PI)],
            desc="Buck converter SOT563, Proteus pin ids 1=FB 2=GND 3=VIN 4=SW 5=EN 6=VOUT"),
        box("IZB03", "PS", [(2, "Vin+", PI), (3, "On/Off", IN), (1, "Vin-", PI)],
            [(4, "NC", NC), (5, "Vout+", PO), (6, "Vout-", PO), (7, "Ripple", PAS)],
            desc="Isolated DC/DC module, 7 pins, Proteus pin ids"),
        box("TPS73030", "V", [(1, "VIN", PI), (2, "GND", PI), (3, "EN", IN)], [(4, "NR", PAS), (5, "VOUT", PO), None],
            desc="LDO SOT-23-5, Proteus pin ids"),
        box("MAX22025", "U", [(1, "RXD", OUT), (2, "TXD", IN), (3, "VDDA", PI), (4, "GNDA", PI)],
            [(8, "VDDB", PI), (7, "B", BI), (6, "A", BI), (5, "GNDB", PI)],
            desc="Isolated RS485 half-duplex transceiver SOIC-8 wide, Proteus pin ids"),
        box("SN74AXC8T245", "U",
            [(1, "VCCA", PI), (2, "DIR1", IN), (11, "DIR2", IN), (22, "~{OE}", IN), None]
            + [(i + 2, f"A{i}", BI) for i in range(1, 9)] + [None, (12, "GND", PI), (13, "GND", PI)],
            [(24, "VCCB", PI), (23, "VCCB", PI), None, None, None]
            + [(22 - i, f"B{i}", BI) for i in range(1, 9)],
            desc="Octal dual-supply bus transceiver TSSOP-24, Proteus pin ids"),
        box("SN74LV4051", "U",
            [(16, "VDD", PI), (11, "A", IN), (10, "B", IN), (9, "C", IN), (6, "INH", IN), None,
             (8, "VSS", PI), (7, "VEE", PI)],
            [(3, "X", PAS), None, (13, "X0", PAS), (14, "X1", PAS), (15, "X2", PAS), (12, "X3", PAS),
             (1, "X4", PAS), (2, "X6", PAS), (5, "X5", PAS), (4, "X7", PAS)],
            desc="8-channel analog multiplexer TSSOP-16, Proteus pin ids"),
    ]
    for n, nm in ((16, "2X8"), (30, "2X15"), (40, "2X20")):
        l, r = header(range(1, n + 1))
        syms.append(box(f"HEADER_{nm}_50MIL", "J", l, r, show_pin_names=False,
                        desc=f"{n}-pin dual-row header, 1.27 mm pitch, odd pins left"))

    syms.append(multi_box("TI60F225", "U", ti60_units(),
                          "Efinix Ti60F225 FPGA, BGA-225 0.65 mm; pin numbers = balls; units as in the PDF: "
                          "A config/JTAG, B GPIOL/GPIOR singles, C bank L, D bank R, E bank B, F bank T, "
                          "G power + REF_RES, H GND"))

    syms.append(rename(std_symbol("power", "PWR_FLAG"), "PWR_FLAG"))
    syms += [power(n, True) for n in GROUNDS] + [power(n, False) for n in SUPPLIES]
    return syms


if __name__ == "__main__":
    sys.exit(run(build))
