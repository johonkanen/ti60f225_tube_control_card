#!/usr/bin/env python3
"""Sheet 6 - FPGA power (PDF page 6): U10 unit G (core VCC and VCCA on 1V, VCCIO33 on 3V3, VCCAUX and
the eight VCCIO banks on 1V8, the eight REF_RES pins each through a 10k0 resistor to GND) and unit H
(the 12 GND balls), the decoupling capacitors C21-C25, C40 (1V) and C29, C30, C33, C36 (3V3).

Differences from the PDF drawing (same nets): the supply groups of unit G are joined by a bus line as
in the PDF, with a power symbol instead of the terminal; the reference resistors stand at an even
pitch below their pins; DGND of the PDF is GND."""
from _common import *  # noqa: F401,F403

sh = sheet("06_fpga_power.kicad_sch")

# --- U10 unit G ----------------------------------------------------------------------------------------
BUSES = [("left", ["E13", "G7", "G9", "H6", "H8", "J7", "J9", "M3"], "H8"),      # VCC
         ("left", ["P4", "N15", "B4", "B13"], "B4"),                               # VCCIO33
         ("left", ["J4", "L2", "D2", "F4"], "J4"),                                 # VCCIO1
         ("left", ["C7", "D6", "C11", "D9"], "C7"),                                # VCCIO2
         ("left", ["F14", "G12", "J11", "L14"], "F14"),                            # VCCIO3
         ("left", ["N9", "N11", "N5", "N7"], "N9"),                                # VCCIO4
         ("right", ["D4", "E11", "L4", "M11"], "E11"),                             # VCCAUX
         ("right", ["L5", "L10", "E5", "G10"], "L10")]                             # VCCA
REF = [("K5", "R40", 30, 0), ("E4", "R39", 35, 69), ("F6", "R38", 40, 69), ("D11", "R37", 45, 67),
       ("B15", "R36", 50, 65), ("M12", "R35", 55, 63), ("N12", "R32", 60, 61), ("M5", "R11", 65, 59)]   # ball, R, row, bend column
ug = fpga_unit(sh, 7, 43, 42, skip=[b for _, pins, _ in BUSES for b in pins] + [r[0] for r in REF])
assert sorted(ug.pins) == sorted([b for _, pins, _ in BUSES for b in pins] + [r[0] for r in REF])
for side, pins, at in BUSES:
    rail_bus(sh, ug, pins, at, side)
# reference resistors: ball - 10k0 - GND bus
XB = 88
for ball, ref, y, xv in REF:
    a, b = two(sh, ref, *P(78, y), left=net("U10", ball), text="above")
    p = ug.pin(ball)
    if p[1] == a[1]:
        sh.wire(p, a)
    else:
        sh.wire(p, (P(xv, 0)[0], p[1]), (P(xv, 0)[0], a[1]), a)
    assert net(ref, pin_of(ref, "GND")) == "GND"
    sh.wire(b, P(XB, y))
ys = [r[2] for r in REF]
for y0, y1 in zip(ys, ys[1:]):
    sh.wire(P(XB, y0), P(XB, y1))
for y in ys[1:]:
    sh.junction(*P(XB, y))
tie(sh, "GND", P(XB, ys[-1]), "right", 5)

# --- U10 unit H: GND -----------------------------------------------------------------------------------
uh = fpga_unit(sh, 8, 146, 83, skip=["A1", "A15", "D3", "G6", "G8", "H7", "H9", "J6", "J8", "M13", "R1", "R15"])
balls = sorted(uh.pins, key=lambda b: uh.pin(b)[1])
assert len(balls) == 12 and all(net("U10", b) == "GND" for b in balls)
xv = P(154, 0)[0]
for b in balls:
    sh.wire(uh.pin(b), (xv, uh.pin(b)[1]))
for b0, b1 in zip(balls, balls[1:]):
    sh.wire((xv, uh.pin(b0)[1]), (xv, uh.pin(b1)[1]))
for b in balls[1:]:
    sh.junction(xv, uh.pin(b)[1])
tie(sh, "GND", (xv, uh.pin(balls[-1])[1]), "down", 4)


# --- decoupling ----------------------------------------------------------------------------------------
def cap_row(refs, xs, y, rail, x0):
    """Capacitors between a supply rail line (above, power symbol at the left end x0) and a GND line."""
    for ref, x in zip(refs, xs):
        a, b = two(sh, ref, *P(x, y), top=rail)
        assert net(ref, pin_of(ref, "GND")) == "GND"
        sh.wire(a, P(x, y - 7))
        sh.wire(b, P(x, y + 7))
    pts = [x0, *xs]
    for dy, name in ((-7, rail), (7, "GND")):
        for xa, xb in zip(pts, pts[1:]):
            sh.wire(P(xa, y + dy), P(xb, y + dy))
        for x in xs[:-1]:
            sh.junction(*P(x, y + dy))
        tie(sh, name, P(x0, y + dy), "left", 0, body="left")


cap_row(["C36"], [150], 23, "3V3", 125)
cap_row(["C29", "C30", "C33"], [130, 140, 151], 43, "3V3", 125)
cap_row(["C21", "C22", "C23", "C24", "C25", "C40"], [19, 29, 39, 50, 60, 71], 123, "1V", 14)
sh.save()
print("sheet06: written")
