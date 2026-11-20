#!/usr/bin/env python3
"""Sheet 12 - JFET drivers 13-16 (PDF page 12): four inverting amplifiers (gain -47k / 10k) on the
quad op-amp U14 (TL084H, supplies 3V3 and OPAMP_-15V) with the arrays R17 (10k, inputs GPIOL_9,
GPIOL_3, GPIOL_4, GPIOL_7) and R18 (47k), outputs JFET_14, JFET_13, JFET_15, JFET_16, and the supply
decoupling of the four quad op-amps of pages 9 and 12: C60, C62, C64, C66 (3V3 - GND) and C59, C61,
C63, C65 (GND - OPAMP_-15V).

Differences from the PDF drawing (same nets): the power pins 4 / 11 are the power unit E laid over
unit A (Proteus draws them on every unit)."""
from _common import *  # noqa: F401,F403

sh = sheet("12_jfet_drivers_13_16.kicad_sch")

cells = jfet_quad(sh, "U14", "R17", "R18", [(31, 37), (81, 39), (127, 37), (171, 37)])
# PDF labels (input, output) of the four cells in drawing order = the IPC nets
assert cells == [("GPIOL_9", "JFET_14"), ("GPIOL_3", "JFET_13"), ("GPIOL_4", "JFET_15"), ("GPIOL_7", "JFET_16")], cells

for i, (c_pos, c_neg) in enumerate((("C60", "C59"), ("C62", "C61"), ("C64", "C63"), ("C66", "C65"))):
    for ref, x, top in ((c_pos, 18, "3V3"), (c_neg, 25, "GND")):
        a, b = two(sh, ref, *P(x + 30 * i - (2 if i >= 2 else 0), 107), top=top, text="left" if ref == c_pos else None)
        tie(sh, top, a, "up", 4)
        tie(sh, net(ref, pin_of(ref, "GND" if top == "3V3" else "OPAMP_-15V")), b, "down", 4)
note(sh, "PDF page 9 alias: GPIOL_9 = JFET_GPIO_2 (the input of the JFET_14 driver)", 20, 70)
sh.save()
print("sheet12: written")
