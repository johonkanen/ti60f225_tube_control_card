#!/usr/bin/env python3
"""Sheet 1 - Net aliases and power inputs (PDF page 1): the power input terminals J4 (GND), J2 (5V,
decision D1), J5 (12V), J9 (OPAMP_-15V), the UART connector J8 (rx = GPIOL_2, tx = GPIOL_1, ISOGND =
GND) with the pull-up R16 on tx, and the Proteus alias pairs of the page as text notes (transcription
rules: an alias pair is never drawn as two labels on a wire; the IPC name is used on every pin)."""
from _common import *  # noqa: F401,F403

sh = sheet("01_net_aliases_power_inputs.kicad_sch")

# power input terminals (PDF: label - wire - terminal); the rails enter the board here
for ref, y in (("J4", 70), ("J2", 79), ("J5", 88), ("J9", 98)):
    t = term(sh, ref, *P(155, y), "right")
    q = P(140, y)
    sh.wire(t.pin(1), P(147, y), q)          # two segments: a pin connects only at a wire end
    tie(sh, net(ref, 1), q, n=0)
    sh.pwr_flag(*P(147, y))

# J8: 1 rx, 2 tx, 3 ISOGND
j8 = place_pin(sh, "J8", 1, P(151, 43))
pin_tie(sh, j8, 1, "left", 10)
pin_tie(sh, j8, 2, "left", 10)
pin_tie(sh, j8, 3, "left", 10)

# R16: pull-up of tx (GPIOL_1) to 3V3
a, b = two(sh, "R16", *P(135, 26), top="3V3")
tie(sh, "3V3", a, "up", 1)
tie(sh, net("R16", pin_of("R16", "GPIOL_1")), b, "down", 1)

# PDF note "FIX BUGS!" dropped (obsolete; user decision 2026-11-20, STATUS.md "Design fixes 2026-11-20")
note(sh, "Proteus alias pairs of this page (two terminal labels joined by a line). The KiCad sheets use the IPC net name on", 8, 3)
note(sh, "every pin; a pair whose second name occurs nowhere else adds no connection (STATUS.md findings 2 and 11).", 8, 5)
PAIRS_TOP = ["L1 = PWM_TRANS5", "N1 = PWM_Q8", "P1 = PWM_Q6", "T3 = DAB_PWM_LO_SEC", "T4 = DAB_PWM_HI_SEC",
             "RGB1_R = PWM_TRANS4", "P8 = DAB_PWM_PRI_LO_ISO", "R10 = PWM_G3_ISO",
             "R11 - - PWM_G2_ISO (dashed: not joined)", "R12 = PWM_TRANS3_ISO", "R13 = PWM_TRANS1_ISO",
             "R14 = CS1_ISO", "T15 = ADASEL0_ISO", "GPIOR_25 - - ADASEL2_ISO (dashed: not joined)",
             "N14 - - ADCLK_ISO (dashed: not joined)", "ADB1 = ISOADA2", "ADB2 = ISOADA3"]
PAIRS_LEFT = ["GPIOR_28 = MDATA_INU", None, "R3 = PWM_Q5", "R4 = PWM_TRANS6", "GPIOR_27 = MDATA_DAB",
              "T7 = ADCLK_DAB", "N8 = DAB_PWM_PRI_HI_ISO", None, "PWM_G4_ISO = T11", "PWM_TRANS2_ISO = T12",
              "CLK1_ISO = T13", "SDATA1_ISO = GPIOR_29", "ADASEL1_ISO = R16", None, "MOS_GATE_3 = GPIOR_25",
              "ISOADA1 = ADB0", None, "gnd = ISOGND (J8 pin 3 is GND)"]
for i, s in enumerate(PAIRS_TOP):
    note(sh, s, 92, 11 + 2 * i)
for i, s in enumerate(PAIRS_LEFT):
    if s:
        note(sh, s, 16, 80 + 2 * i)
for i, s in enumerate(["rx = T6", "tx = R6", None, "rx = GPIOL_2 (J8 pin 1)", "tx = GPIOL_1 (J8 pin 2, R16)"]):
    if s:
        note(sh, s, 160, 28 + 2 * i)
for i, s in enumerate(["RLY3_ENABLE = GPIOR_21", "MOS_GATE_1 = GPIOR_24", "T_IRQ = GPIOR_22"]):
    note(sh, s, 160, 44 + 3 * i)
sh.save()
print("sheet01: written")
