#!/usr/bin/env python3
"""Sheet 7 - ADC multiplexer (PDF page 7): the 8:1 analog multiplexer U3 (SN74LV4051, inputs ADB0-7
from J11, select ADBSEL0-2, INH on GND), the buffer U4 (TLV316, follower), the filter R12 / C5 and
the ADC AD2 (ADS7056; SPI on GPIOL_P_00_PLLIN0 / GPIOL_N_00 / GPIOB_N_00, DVDD = 1V8). The analog
supply of U4 and AD2 (auto-named net) comes from AD_3V3 through L3, decoupled by C6 and C7.

Differences from the PDF drawing (same nets): the hidden supply pins of U3 (Proteus text VDD=AD_3V3,
VEE=AGND, VSS=AGND) are drawn below the body; AGND and DGND of the PDF are GND (the page ties the two
terminals together: a text note here)."""
from _common import *  # noqa: F401,F403

sh = sheet("07_adc_mux.kicad_sch")

# --- U3 multiplexer ----------------------------------------------------------------------------------
u3 = place_pin(sh, "U3", 13, P(33, 61))
for pin in (13, 14, 15, 12, 1, 5, 2, 4, 11, 10, 9):
    pin_tie(sh, u3, pin, "left", 4)
pin_tie(sh, u3, 6, "left", 4, body="left")                    # INH on GND
for pin, n in ((16, 6), (7, 2), (8, 2)):                      # hidden supply pins of the PDF
    pin_tie(sh, u3, pin, "down", n)
note(sh, "check logic", 37, 52, size=2.0)
note(sh, "Proteus hidden pins: VDD=AD_3V3, VEE=AGND, VSS=AGND", 31, 108)

# --- U4 buffer ---------------------------------------------------------------------------------------
u4 = place_pin(sh, "U4", 3, P(66, 61))
assert u4.pin(1) == P(78, 63) and u4.pin(4) == P(66, 65) and u4.pin(5) == P(70, 57) and u4.pin(2) == P(70, 69)
YG = 82                                                       # ground line under the buffer
sh.wire(u3.pin(3), u4.pin(3))
sh.wire(u4.pin(1), P(83, 63))
sh.wire(P(83, 63), P(83, 53), P(63, 53), P(63, 65), u4.pin(4))   # follower feedback
sh.junction(*P(83, 63))
a, b = two(sh, "R12", *P(89, 63), left=net("U4", 1), text="above")
sh.wire(P(83, 63), a)

# --- AD2 ---------------------------------------------------------------------------------------------
ad2 = place_pin(sh, "AD2", 8, P(120, 61))
assert ad2.pin(7) == P(120, 63) and ad2.pin(6) == P(120, 65) and ad2.pin(5) == P(120, 67)
sh.wire(b, P(95, 63), ad2.pin(7))                             # AINP
sh.junction(*P(95, 63))
c, d = two(sh, "C5", *P(95, 76), top=net("AD2", 7))
sh.wire(c, P(95, 63))
sh.wire(d, P(95, YG))
for pin in (1, 2, 3):
    pin_tie(sh, ad2, pin, "right", 8)
sh.wire(ad2.pin(4), P(141, 67), P(141, 76))
tie(sh, net("AD2", 4), P(141, 76), "down", 2)                 # DVDD

# --- analog supply: AD_3V3 - L3 - AVDD node (U4 V+, AD2 AVDD, C6, C7) --------------------------------
avdd = net("AD2", 6)
a, b = two(sh, "L3", *P(107, 48), top="AD_3V3")
tie(sh, "AD_3V3", a, "up", 4)
sh.wire(b, P(107, 56))
sh.wire(P(107, 56), P(107, 65))
sh.wire(P(107, 65), ad2.pin(6))
sh.junction(*P(107, 56))
sh.junction(*P(107, 65))
c, d = two(sh, "C6", *P(107, 75), top=avdd)
sh.wire(P(107, 65), c)
sh.wire(P(107, 56), P(102, 56))
sh.wire(P(102, 56), P(97, 56), P(97, 50), P(70, 50))
sh.pwr_flag(*P(102, 56))                                      # the filtered analog supply starts behind L3
sh.wire(P(70, 50), u4.pin(5))
sh.junction(*P(70, 50))
e, f = two(sh, "C7", *P(58, 75), top=avdd)
sh.wire(P(70, 50), P(58, 50), e)
# ground
sh.wire(f, P(58, YG), P(70, YG))
sh.wire(P(70, YG), P(95, YG))
sh.wire(u4.pin(2), P(70, YG))
sh.junction(*P(70, YG))
tie(sh, net("U4", 2), P(70, YG), "down", 5)
sh.wire(d, P(107, 80))
sh.junction(*P(107, 80))
tie(sh, net("C6", 1), P(107, 80), "down", 4)
sh.wire(P(107, 80), P(117, 80), P(117, 67))
sh.wire(P(117, 67), ad2.pin(5))
sh.wire(P(117, 67), P(117, 61), ad2.pin(8))                   # AINM on GND
sh.junction(*P(117, 67))

# --- decoupling --------------------------------------------------------------------------------------
for ref, x, y in (("C9", 129, 101), ("C71", 154, 97), ("C10", 50, 122)):
    a, b = two(sh, ref, *P(x, y), top=net(ref, 2))
    tie(sh, net(ref, 2), a, "up", 4)
    tie(sh, net(ref, 1), b, "down", 4)
note(sh, "PDF: terminals AGND and DGND joined here (AGND = DGND = GND, one net)", 62, 124)
sh.save()
print("sheet07: written")
