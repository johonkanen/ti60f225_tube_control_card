#!/usr/bin/env python3
"""Sheet 3 - Regulators (PDF page 3): the LDO V4 (TPS73030, 5V -> AD_3V3, the analog supply) and the
three AP61202 buck converters from 5V: PWR1 / L1 -> 1V8, PWR2 / L4 -> 1V (core), PWR3 / L5 -> 3V3.
PWR2 pin 6 (Proteus name VOUT) drives 1V_ENABLE (pull-up R1 to 5V) = the EN pins of PWR1 and PWR3;
PWR2's own EN is on 5V (STATUS.md finding 12). Pin 6 of PWR1 and PWR3 is N/C.

The rails AD_3V3, 1V8, 1V and 3V3 are generated here: V4 VOUT is a power output; the buck outputs
(behind the inductors) carry a PWR_FLAG. Differences from the PDF drawing (same nets): the two lower
feedback resistors of PWR2 / PWR3 and the two output capacitors of PWR2 stand side by side on the
feedback / output line; DGND of the PDF is GND."""
from _common import *  # noqa: F401,F403

sh = sheet("03_regulators.kicad_sch")


def buck(ref, x, y, coil, r_up, c_ff, r_low, c_in, c_out, enable_from_5v=False, pullup=None):
    """AP61202 block with its VIN pin (3) at PDF position (x, y), in grid units from there: input
    capacitor, inductor, feedback divider r_up (with c_ff across) / r_low (one or two resistors),
    output capacitors, ground rail. Returns nothing; every net name comes from the IPC pins."""
    Q = lambda dx, dy: P(x + dx, y + dy)
    u = place_pin(sh, ref, 3, Q(0, 0))
    assert u.pin(5) == Q(0, 2) and u.pin(6) == Q(16, 0) and u.pin(4) == Q(16, 2) and u.pin(1) == Q(16, 4) \
        and u.pin(2) == Q(8, 14), u.pins
    fb, rail = net(ref, 1), net(coil, 2)
    YF, YC, YL, YG = 8, 13, 17, 24                           # rows: feedback line, c_ff, lower parts, ground rail
    XR, XO, DX = 22, 50, 7                                   # columns: first lower resistor, first output capacitor, pitch
    # input: 5V, input capacitor
    sh.wire(u.pin(3), Q(-5, 0))
    tie(sh, net(ref, 3), Q(-5, 0), "left", 5)
    sh.junction(*Q(-5, 0))
    a, b = two(sh, c_in, *Q(-5, YL), top=net(ref, 3))
    sh.wire(a, Q(-5, 0))
    sh.wire(b, Q(-5, YG))
    # enable
    if enable_from_5v:
        assert net(ref, 5) == net(ref, 3)
        sh.wire(u.pin(5), Q(-3, 2), Q(-3, 0))
        sh.junction(*Q(-3, 0))
    else:
        pin_tie(sh, u, 5, "left", 10)
    # pin 6 (VOUT): N/C, or the enable output with its pull-up
    if pullup:
        sh.wire(u.pin(6), Q(34, 0))
        tie(sh, net(ref, 6), Q(34, 0), "right", 4)
        a, b = two(sh, pullup, *Q(34, -5), top="5V")
        tie(sh, "5V", a, "up", 2)
        sh.wire(b, Q(34, 0))
        sh.junction(*Q(34, 0))
    else:
        pin_tie(sh, u, 6)
    # switch node, inductor, output rail (PWR_FLAG: the rail is generated here)
    a, b = two(sh, coil, *Q(26, 2), left=net(ref, 4), text="below")
    sh.wire(u.pin(4), Q(18, 2), a)
    sh.label(net(ref, 4), *Q(18, 2))
    assert net_kind(net(ref, 4)) == "local"
    xo = XO + DX * (len(c_out) - 1)                           # last output capacitor
    sh.wire(b, *[Q(XO + DX * i, 2) for i in range(len(c_out))], Q(xo + 4, 2))
    tie(sh, rail, Q(xo + 4, 2), "right", 6)
    sh.pwr_flag(*Q(xo + 4, 2))
    # feedback divider
    a, b = two(sh, r_up, *Q(40, YF), left=fb, text="above")
    sh.wire(u.pin(1), Q(19, 4), Q(19, YF), a)
    sh.wire(b, Q(XO, YF))
    c, d = two(sh, c_ff, *Q(40, YC), left=fb, text="below")
    sh.wire(Q(35, YF), Q(35, YC), c)
    sh.wire(d, Q(45, YC), Q(45, YF))
    sh.junction(*Q(35, YF))
    sh.junction(*Q(45, YF))
    for i, r in enumerate(r_low):
        xr = XR + DX * i
        a, b = two(sh, r, *Q(xr, YL), top=fb)
        sh.wire(a, Q(xr, YF))
        sh.junction(*Q(xr, YF))
        sh.wire(b, Q(xr, YG))
        sh.junction(*Q(xr, YG))
    # output capacitors (the first one also takes the upper feedback resistor)
    for i, cap in enumerate(c_out):
        xc = XO + DX * i
        a, b = two(sh, cap, *Q(xc, YL), top=rail)
        sh.wire(a, Q(xc, 2))
        sh.junction(*Q(xc, 2))
        if i == 0:
            sh.junction(*Q(xc, YF))
        sh.wire(b, Q(xc, YG))
        if xc != xo:
            sh.junction(*Q(xc, YG))
    # ground rail
    sh.wire(Q(-5, YG), Q(xo, YG))
    sh.wire(u.pin(2), Q(8, YG))
    sh.junction(*Q(8, YG))
    tie(sh, net(ref, 2), Q(8, YG), "down", 3)

buck("PWR1", 116, 13, "L1", "R8", "C57", ["R9"], "C15", ["C16"])
buck("PWR2", 116, 72, "L4", "R10", "C70", ["R20", "R2"], "C13", ["C14", "C18"], enable_from_5v=True, pullup="R1")
buck("PWR3", 31, 97, "L5", "R29", "C56", ["R30", "R13"], "C11", ["C12"])
note(sh, "note, needs to be 0.95V and not 1.0V", 110, 58, size=3.0)

# --- V4: 5V -> AD_3V3 (Proteus VCC/VDD) --------------------------------------------------------------
v4 = place_pin(sh, "V4", 1, P(39, 8))
YG = 24
sh.wire(v4.pin(1), P(26, 8))
tie(sh, "5V", P(26, 8), "left", 6)
sh.junction(*P(26, 8))
a, b = two(sh, "C19", *P(26, 15), top="5V")
sh.wire(a, P(26, 8))
sh.wire(b, P(26, YG), P(58, YG))
sh.wire(v4.pin(3), P(33, 10), P(33, 8))                      # EN on 5V
sh.junction(*P(33, 8))
sh.wire(v4.pin(2), P(35, 12), P(35, YG))
sh.junction(*P(35, YG))
a, b = two(sh, "C20", *P(58, 16), top=net("V4", 4))          # NR capacitor
sh.wire(v4.pin(4), P(58, 10), a)
sh.wire(b, P(58, YG))
sh.junction(*P(58, YG))
tie(sh, "GND", P(58, YG), "right", 4)
tie(sh, net("V4", 5), v4.pin(5), "right", 8)
note(sh, "AD_3V3 = Proteus power net VCC/VDD (PDF label AD_3V3); DGND = GND.", 20, 30)
sh.save()
print("sheet03: written")
