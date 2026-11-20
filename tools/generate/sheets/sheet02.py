#!/usr/bin/env python3
"""Sheet 2 - FPGA configuration and clock (PDF page 2): U10 unit A (CDONE with the pull-up R27,
CRESET_N with R21 / C17, JTAG) and unit C (bank L pairs: the configuration flash FLASH1 on
FLASH_NCE / DCLK / DATA0-3, pull-ups R41-R44, R3, R28 to 1V8), the 32 MHz oscillator OSC1 (1V8) on
GPIOR_P_19_PLLIN0, the JTAG terminal block J1 with the pull-ups R4-R7 to 3V3.

Proteus alias pairs of the page (text notes; the IPC name is on the pins): TXD = GPIOL_N_09 (ball G1),
RXD = GPIOL_P_10 (ball H2), clk32Mhz = GPIOR_P_19_PLLIN0; from page 10: POWERSCL = GPIOL_N_16 (C1),
POWERSDA = GPIOL_N_17 (C2). The 9 N/C balls of unit C carry no-connect flags; GPIOL_N_10, GPIOL_N_18
and GPIOL_P_18 are single-ball nets (STATUS.md finding 2).

Differences from the PDF drawing (same nets): the unit C pins stand at a uniform 2.54 mm pitch (the
PDF spaces the pairs), DGND of the PDF is GND, the oscillator output carries one label."""
from _common import *  # noqa: F401,F403

sh = sheet("02_fpga_config_clock.kicad_sch")

# --- U10 unit A: configuration and JTAG ----------------------------------------------------------------
ua = fpga_unit(sh, 1, 85, 38, n=6)
assert ua.pin("L3") == P(93, 32) and ua.pin("J5") == P(93, 34), ua.pins
YR = 15                                                       # 1V8 rail of the pull-ups
a, b = two(sh, "R27", *P(104, 23), top="1V8")                 # CDONE pull-up
sh.wire(a, P(104, YR))
sh.wire(ua.pin("L3"), P(104, 32), b)
assert net("R27", 2) == net("U10", "L3")
c, d = two(sh, "R21", *P(115, 23), top="1V8")                 # CRESET_N: R21 to 1V8, C17 to GND
sh.wire(c, P(115, YR))
sh.wire(ua.pin("J5"), P(115, 34))
sh.wire(d, P(115, 34))
sh.junction(*P(115, 34))
e, f = two(sh, "C17", *P(115, 40), top=net("U10", "J5"))
sh.wire(P(115, 34), e)
tie(sh, net("C17", 1), f, "down", 3)
assert net("R21", 2) == net("U10", "J5")
# pull-ups with a label below
for ref, x in (("R3", 126), ("R28", 137)):
    a, b = two(sh, ref, *P(x, 23), top="1V8")
    sh.wire(a, P(x, YR))
    tie(sh, net(ref, 2), b, "down", 6)
# pull-ups of the flash signals, labels at the right
for ref, x, y in (("R41", 146, 47), ("R42", 154, 45), ("R43", 162, 43), ("R44", 170, 41)):
    a, b = two(sh, ref, *P(x, 23), top="1V8")
    sh.wire(a, P(x, YR))
    sh.wire(b, P(x, y), P(176, y))
    tie(sh, net(ref, 2), P(176, y), "right", 0)
xs = (104, 115, 126, 137, 146, 154, 162, 170)
for x0, x1 in zip(xs, xs[1:]):
    sh.wire(P(x0, YR), P(x1, YR))
for x in xs[1:-1]:
    sh.junction(*P(x, YR))
tie(sh, "1V8", P(104, YR), "up", 5)

# --- JTAG pull-ups R4-R7 (3V3) and the terminal block J1 -----------------------------------------------
xs = (8, 15, 22, 31)
for ref, x in zip(("R4", "R5", "R6", "R7"), xs):
    a, b = two(sh, ref, *P(x, 29), top="3V3")
    sh.wire(a, P(x, 19))
    tie(sh, net(ref, 2), b, "down", 5)
for x0, x1 in zip(xs, xs[1:]):
    sh.wire(P(x0, 19), P(x1, 19))
sh.junction(*P(15, 19))
sh.junction(*P(22, 19))
tie(sh, "3V3", P(15, 19), "up", 7)
j1 = place_pin(sh, "J1", 1, P(117, 119))
for pin in range(1, 6):
    pin_tie(sh, j1, pin, "left", 7, body="left")

# --- OSC1: 32 MHz oscillator on 1V8 --------------------------------------------------------------------
osc = place_pin(sh, "OSC1", 1, P(145, 58))
assert osc.pin(4) == P(145, 60) and osc.pin(3) == P(161, 58) and osc.pin(2) == P(153, 70), osc.pins
assert net("OSC1", 1) == net("OSC1", 4) == "1V8"
sh.wire(osc.pin(4), P(140, 60))
sh.wire(osc.pin(1), P(140, 58), P(140, 60))                   # EN on VCC
sh.wire(P(140, 60), P(119, 60), P(119, 56))
sh.junction(*P(140, 60))
tie(sh, "1V8", P(119, 56), "up", 0)
a, b = two(sh, "C2", *P(140, 67), top="1V8")
sh.wire(P(140, 60), a)
tie(sh, net("C2", 1), b, "down", 4)
pin_tie(sh, osc, 2, "down", 4)
pin_tie(sh, osc, 3, "right", 8)
note(sh, "1v8 oscillator voltage!!!", 121, 56)
note(sh, "Proteus alias: clk32Mhz = GPIOR_P_19_PLLIN0 (OSC1 OUT, U10 ball C14 on sheet 5)", 147, 52)
note(sh, "Proteus alias: TXD = GPIOL_N_09 (IPC TXD, U10 ball G1)", 86, 82)
note(sh, "Proteus alias: RXD = GPIOL_P_10 (IPC RXD, U10 ball H2)", 86, 84)
note(sh, "Page 10 alias: POWERSCL = GPIOL_N_16 (ball C1), POWERSDA = GPIOL_N_17 (ball C2)", 86, 86)

# --- FLASH1: configuration flash on 1V8 ----------------------------------------------------------------
fl = place_pin(sh, "FLASH1", 1, P(144, 92))
assert fl.pin(4) == P(144, 98) and fl.pin(8) == P(164, 92) and fl.pin(5) == P(164, 98), fl.pins
for pin in (1, 2, 3):
    pin_tie(sh, fl, pin, "left", 8)
for pin in (7, 6, 5):
    pin_tie(sh, fl, pin, "right", 14)
sh.wire(fl.pin(8), P(169, 92))
sh.junction(*P(169, 92))
tie(sh, net("FLASH1", 8), P(169, 92), "up", 4)
a, b = two(sh, "C1", *P(169, 103), top="1V8")
sh.wire(P(169, 92), a)
sh.wire(b, P(169, 109))
sh.wire(fl.pin(4), P(137, 98), P(137, 109), P(169, 109))
sh.junction(*P(169, 109))
tie(sh, net("FLASH1", 4), P(169, 109), "right", 9)
note(sh, "1v8 flash voltage!!!", 173, 84)

# --- U10 unit C: bank L pairs --------------------------------------------------------------------------
fpga_unit(sh, 3, 52, 97, alias={"GPIOL_N_09": "TXD", "GPIOL_P_10": "RXD",
                                "GPIOL_N_16": "POWERSCL", "GPIOL_N_17": "POWERSDA"})
sh.save()
print("sheet02: written")
