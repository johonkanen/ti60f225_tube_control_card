#!/usr/bin/env python3
"""Sheet 4 - Level shifters (PDF page 4): five SN74AXC8T245 (U1, U2, U9, U7, U8) between the 1V8 FPGA
banks (A side, VCCA = 1V8) and the 3V3 signals of the connectors (B side, VCCB = 3V3), each with two
100n capacitors. On every one DIR1 is on 1V8, DIR2 and ~OE on GND. U1 B1-B4 and U9 B1-B2 are
single-pin nets (STATUS.md finding 2).

Differences from the PDF drawing (same nets): all five blocks are drawn like U1 (supply labels at the
sides; the PDF has them above U9, U7, U8), U2 and U9 stand lower and U9 further right than in the PDF
(the KiCad symbol is taller), the direction table of the page is a text note."""
from _common import *  # noqa: F401,F403

sh = sheet("04_level_shifters.kicad_sch")

level_shifter(sh, "U1", 34, 24, "C32", "C34")
level_shifter(sh, "U2", 34, 80, "C28", "C31")
level_shifter(sh, "U9", 34, 136, "C26", "C27")
level_shifter(sh, "U7", 108, 92, "C39", "C38")
level_shifter(sh, "U8", 160, 30, "C35", "C37")

for i, s in enumerate(["Direction table of the PDF page (as drawn there):",
                       "DIR 1   DIR 2   bits 1 : 4   bits 5 : 8",
                       "  L       L       B to A       B to A",
                       "  L       H       B to A       A to B",
                       "  H       L       A to B       A to B",
                       "  H       H       A to B       B to A",
                       "All five: DIR1 = 1V8 (H), DIR2 = GND (L), ~OE = GND."]):
    note(sh, s, 150, 96 + 3 * i, size=1.6)
sh.save()
print("sheet04: written")
