#!/usr/bin/env python3
"""Sheet 10 - Connectors and bias ADC (PDF page 10): the headers J7 (30 pins: JFET, relay and MOS
gate signals, FPGA bank T pairs), J6 (16 pins: bias feedback / reference, POWERSDA / POWERSCL) and J3
(16 pins: JFET signals, every even pin on GND), and the bias feedback ADC ADC1 (ADC121C027, I2C on
GPIOR_22 / GPIOR_28 with the pull-ups R33 / R31, input filter R34 / C68).

Differences from the PDF drawing (same nets): the paired supply pins of J7 and J6 (3V3, GND) get one
power symbol each instead of the loops around the connector; the J3 ground bus runs down to its GND
symbol. The alias pairs and the unconnected JFET_GATE terminals of the page are text notes."""
from _common import *  # noqa: F401,F403

sh = sheet("10_connectors_bias_adc.kicad_sch")


def header_ties(p, npins, n=8):
    """Labels / power symbols / no-connect flags on every pin of a placed dual-row header."""
    xs = sorted({pt[0] for pt in p.pins.values()})
    for pin in range(1, npins + 1):
        side = "left" if p.pin(pin)[0] == xs[0] else "right"
        if net(p.ref, pin) in RAILS:
            pin_tie(sh, p, pin, side, 3, body=side)
        else:
            pin_tie(sh, p, pin, side, n)


# J7: pin 30 top left, 29 top right, 1 bottom right (the symbol rotated by 180 deg)
x7, y7 = P(39, 12)
j7 = place_pin(sh, "J7", 30, (x7, y7), 180, ref_at=(x7 + g(6), y7 - g(3), 0, None),
               value_at=(x7 + g(6), P(0, 43)[1], 0, None))
header_ties(j7, 30)

# J6: pin 1 top left
j6 = place_pin(sh, "J6", 1, P(103, 15))
header_ties(j6, 16)

# J3: pin 15 top left, 1 bottom left (the symbol mirrored about its X axis); even pins on a GND bus
x3, y3 = P(176, 26)
j3 = place_mirrored(sh, sym("J3"), "J3", x3, y3, "x", value=sh_value("J3"),
                    ref_at=(x3, y3 - g(10), 0, None), value_at=(x3, y3 + g(11), 0, None))
assert j3.pin(15) == P(170, 20) and j3.pin(1) == P(170, 34), (j3.pin(15), j3.pin(1))
xb = P(186, 0)[0]
for pin in range(1, 16, 2):
    pin_tie(sh, j3, pin, "left", 8)
for pin in range(2, 17, 2):
    assert net("J3", pin) == "GND"
    q = (xb, j3.pin(pin)[1])
    sh.wire(j3.pin(pin), q)
    if pin != 16:
        sh.junction(*q)
sh.wire((xb, j3.pin(16)[1]), (xb, j3.pin(2)[1]))
tie(sh, "GND", (xb, j3.pin(2)[1]), "down", 3)

# ADC1 with the I2C pull-ups and the input filter
adc = place_pin(sh, "ADC1", "K1", P(54, 92))
YR = 71                                                       # 3V3 rail of the pull-ups
for ref, x, pin, ylab, n in (("R31", 29, "COM1", 131, 26), ("R33", 38, "K1", 123, 17)):
    a, b = two(sh, ref, *P(x, 80), top="3V3")
    sh.wire(a, P(x, YR))
    y = adc.pin(pin)[1]
    sh.wire(b, (b[0], y), adc.pin(pin))
    sh.junction(b[0], y)
    sh.wire((b[0], y), P(x, ylab))
    tie(sh, net("ADC1", pin), P(x, ylab), "right", n)
sh.wire(P(29, YR), P(38, YR), P(47, YR))
sh.junction(*P(38, YR))
sh.junction(*P(47, YR))
tie(sh, "3V3", P(47, YR), "up", 4)
sh.wire(P(47, YR), P(47, 86), P(83, 86), (P(83, 0)[0], adc.pin("COM2")[1]), adc.pin("COM2"))   # VIN (COM2) on 3V3
pin_tie(sh, adc, "K2")                                        # ADR0: N/C pad
a, b = two(sh, "R34", *P(95, 94), left=net("ADC1", "A1"))
sh.wire(adc.pin("A1"), a)
tie(sh, "BIASFEEDBACK", b, "right", 8)
c, d = two(sh, "C68", *P(87, 104), top=net("ADC1", "A1"))
sh.wire(c, P(87, 94))
sh.junction(*P(87, 94))
sh.wire(d, P(87, 111), P(80, 111))
sh.wire(adc.pin("A2"), P(80, 96), P(80, 111))
sh.junction(*P(80, 111))
tie(sh, "GND", P(80, 111), "down", 4)
a, b = two(sh, "C67", *P(96, 76), top="3V3")
tie(sh, "3V3", a, "up", 2)
tie(sh, "GND", b, "down", 2)

note(sh, "3V3", 9, 20)
note(sh, "-15V", 8, 35)
for i, s in enumerate(["Proteus alias pairs of this page (the IPC name is used on the pins):",
                       "GPIOL_6 = LOOP_BYPASS_RLY (IPC LOOP_BYPASS_RLY, J3 pin 15)",
                       "JFET_1 = A (IPC A, J3 pin 1)",
                       "JFET_13 = C' (IPC JFET_13, J3 pin 7)",
                       "JFET_15 = D' (IPC JFET_15, J3 pin 9)",
                       "POWERSDA = GPIOL_N_17 (IPC POWERSDA, J6 pin 9)",
                       "POWERSCL = GPIOL_N_16 (IPC POWERSCL, J6 pin 11)"]):
    note(sh, s, 140, 48 + 2 * i)
note(sh, "Unconnected terminals in the PDF (no net): JFET_GATE_x3, _x1, _10, _8, _5, _9, _x2, _3, _2, _6, _7, _4", 140, 75)
note(sh, "ADC1: Proteus pin ids A1 = VA, A2 = GND, COM1 = SDA, COM2 = VIN, K1 = SCL, K2 = ADR0;", 92, 102)
note(sh, "VIN is on 3V3 and VA on the filtered input, as drawn (STATUS.md finding 9).", 92, 104)
sh.save()
print("sheet10: written")
