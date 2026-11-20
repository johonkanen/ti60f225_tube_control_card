#!/usr/bin/env python3
"""Sheet 11 - Bias DAC and RS485 (PDF page 11): the bias reference DAC U12 (AD5622, I2C on
GPIOR_18 / GPIOR_16 = PDF dac_clock / dac_data) with its output filter R59 / C4 (BIASREF), the
isolated 5 V supply PWR4 (IZB03) and the isolated RS485 transceiver RS1 (MAX22025) with the bias
network R67-R69 and the terminals RS485A / RS485B / ISO5V / ISO_G (decision D1: one pin each; the B
node holds R68-2, RS1-7 and R67-1).

Differences from the PDF drawing (same nets): U12 is a box symbol with VA and GND on the right side
(the PDF has them at the top and bottom); C55 and C58 stand next to PWR4 instead of looping around it."""
from _common import *  # noqa: F401,F403

sh = sheet("11_bias_dac_rs485.kicad_sch")

# --- U12 bias DAC ------------------------------------------------------------------------------------
u12 = place_pin(sh, "U12", 3, P(41, 38))
for ref, x, pin in (("R19", 27, 2), ("R26", 36, 3)):          # I2C pull-ups
    a, b = two(sh, ref, *P(x, 26), top="3V3")
    y = u12.pin(pin)[1]
    sh.wire(a, (a[0], P(0, 21)[1]))
    sh.wire(b, (b[0], y))
    sh.junction(b[0], y)
    tie(sh, net("U12", pin), (b[0], y), "left", (x - 21))
    sh.wire((b[0], y), u12.pin(pin))
sh.wire(P(27, 21), P(36, 21))
sh.junction(*P(32, 21))
tie(sh, "3V3", P(32, 21), "up", 2)
tie(sh, net("U12", 4), u12.pin(4), "right", 4)                 # VA
sh.wire(u12.pin(1), P(39, 40), P(39, 46), P(61, 46))           # ADDR to GND
sh.wire(u12.pin(5), P(61, 40), P(61, 46))
sh.junction(*P(61, 46))
tie(sh, net("U12", 5), P(61, 46), "down", 2)
# output filter
sh.wire(u12.pin(6), P(72, 38), P(81, 38))
tie(sh, net("U12", 6), P(81, 38), "right", 9)
for ref, x in (("R59", 72), ("C4", 81)):
    a, b = two(sh, ref, *P(x, 48), top="BIASREF")
    sh.wire(a, P(x, 38))
    sh.wire(b, P(x, 54))
sh.junction(*P(72, 38))
sh.junction(*P(81, 38))
sh.wire(P(72, 54), P(81, 54))
tie(sh, "GND", P(72, 54), "down", 2)
sh.junction(*P(72, 54))
note(sh, "I2C address = 11", 14, 19)
note(sh, "3-state io", 14, 21)
note(sh, "use reference", 57, 19)
note(sh, "Proteus alias: bias_feedback = biasref (terminal on the BIASREF node; the page 10 name is biasfeedback)", 70, 32)
note(sh, "Proteus alias: GPIOR_18 = dac_clock", 10, 61)
note(sh, "Proteus alias: GPIOR_16 = dac_data", 10, 63)

# --- PWR4 isolated 5 V supply ------------------------------------------------------------------------
pwr4 = place_pin(sh, "PWR4", 2, P(38, 75))
a, b = two(sh, "C55", *P(27, 78), top="5V")
sh.wire(pwr4.pin(2), a)
tie(sh, "5V", a, "left", 6)
sh.junction(*a)
sh.wire(pwr4.pin(1), P(33, 79), P(33, 81), b)
tie(sh, "GND", b, "left", 6)
sh.junction(*b)
for pin in (3, 4, 7):                                          # On/Off, NC, Ripple: N/C pads
    pin_tie(sh, pwr4, pin)
a, b = two(sh, "C58", *P(72, 78), top="ISO5V")
sh.wire(pwr4.pin(5), P(64, 77), P(64, 75), a)
tie(sh, "ISO5V", a, "right", 4)
sh.junction(*a)
sh.wire(pwr4.pin(6), P(64, 79), P(64, 81), b)
tie(sh, "RS485_GND", b, "right", 4)
sh.junction(*b)

# --- RS1 isolated RS485 transceiver ------------------------------------------------------------------
rs1 = place_pin(sh, "RS1", 1, P(37, 96))
pin_tie(sh, rs1, 1, "left", 8)
pin_tie(sh, rs1, 2, "left", 8)
pin_tie(sh, rs1, 3, "left", 4, body="left")
pin_tie(sh, rs1, 4, "left", 4)
pin_tie(sh, rs1, 8, "right", 4, body="right")
pin_tie(sh, rs1, 5, "right", 4)
XB, YB, YA = 95, 94, 108                                      # bias chain column, B and A nodes
a, b = two(sh, "R68", *P(XB, 87), top="ISO5V")
tie(sh, "ISO5V", a, "up", 2)
sh.wire(b, P(XB, YB))
a, b = two(sh, "R67", *P(XB, 101), top=net("RS485B", 1))
sh.wire(P(XB, YB), a)
sh.wire(b, P(XB, YA))
a, b = two(sh, "R69", *P(XB, 115), top=net("RS485A", 1))
sh.wire(P(XB, YA), a)
tie(sh, "RS485_GND", b, "down", 2)
sh.wire(rs1.pin(7), P(81, 98), P(81, YB), P(XB, YB))
sh.wire(rs1.pin(6), P(81, 100), P(81, YA), P(XB, YA))
for ref, y in (("RS485B", YB), ("RS485A", YA)):
    t = term(sh, ref, *P(109, y), "right")
    sh.wire(P(XB, y), t.pin(1))
    sh.junction(*P(XB, y))
for ref, y in (("ISO5V", 95), ("ISO_G", 109)):
    t = term(sh, ref, *P(138, y), "right")
    sh.wire(t.pin(1), P(129, y))
    tie(sh, net(ref, 1), P(129, y), n=0)

# --- 1V8 decoupling (RS1 VDDA) -----------------------------------------------------------------------
a, b = two(sh, "C51", *P(11, 119), top="1V8")
tie(sh, "1V8", a, "up", 2)
tie(sh, "GND", b, "down", 2)
note(sh, "VDDA either 3v3 or 1v8", 23, 118, size=3.0)
note(sh, "VDDB max 5.25v", 23, 124, size=3.0)
note(sh, "Terminals ISO5V, ISO_G, RS485A, RS485B: one pin each, two pads on the board (decision D1, STATUS.md).", 100, 127)
sh.save()
print("sheet11: written")
