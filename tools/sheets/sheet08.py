#!/usr/bin/env python3
"""Sheet 8 - Power stage connector J11 (PDF page 8): the 40-pin header to the HV supplies (ADC mux
bus ADB0-7, isolated PWM / ADC signals, 3V3, 12V, GND = PDF DGND) with the decoupling capacitors C53
(12V) and C54 (3V3). Pins 37 and 38 are N/C. The unconnected terminal lists of the page are text notes."""
from _common import *  # noqa: F401,F403

sh = sheet("08_power_stage_connector.kicad_sch")

header(sh, "J11", 39, P(51, 32), n=10)     # pin 39 top left, 1 bottom left

a, b = two(sh, "C53", *P(18, 34), top="12V")
tie(sh, "12V", a, "up", 2)
tie(sh, "GND", b, "down", 2)
a, b = two(sh, "C54", *P(100, 34), top="3V3")
tie(sh, "3V3", a, "up", 2)
tie(sh, "GND", b, "down", 2)

# PDF note "Possible choises are 2x8 ... 2x25" dropped (obsolete: J11 is the 2x20; user decision 2026-11-20,
# STATUS.md "Design fixes 2026-11-20")
note(sh, "Unconnected terminals in the PDF (no net):", 120, 33)
note(sh, "T_IRQ, T_DO, T_DIN, T_CS, T_CK, MOSI, LED, SCK, MISO, DATA/COMMAND, LCD_RESET, LCD_CS, ISOGND, 3V3", 120, 35)
note(sh, "Unconnected terminals in the PDF (no net): ADB2, ADB1, ADB0, ADB3, ADB4, AGND, ADB5, ADB6", 64, 84)
note(sh, "PDF DGND = GND (one net with AGND, gnd, ISOGND).", 20, 78)
sh.save()
print("sheet08: written")
