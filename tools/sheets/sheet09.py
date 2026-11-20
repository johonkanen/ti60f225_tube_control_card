#!/usr/bin/env python3
"""Sheet 9 - JFET drivers 1-12 (PDF page 9): twelve inverting amplifiers (gain -47k / 10k) on the quad
op-amps U5, U6, U11 (TLV9304, supplies 3V3 and OPAMP_-15V), input resistors = the arrays R14, R22,
R24 (10k), feedback resistors = R15, R23, R25 (47k). Each cell: FPGA pin - 10k - inverting input,
+ input on GND, output JFET_n (the output of U5:C is the IPC net A = PDF JFET_1, alias of page 10).

Differences from the PDF drawing (same nets): the power pins 4 / 11, which Proteus draws on every
unit, are the power unit E laid over unit A; the inputs carry the IPC net name (the PDF writes
JFET_GPIO_n on most of them: alias pairs of the table at the bottom of the page, here a text note)."""
from _common import *  # noqa: F401,F403

sh = sheet("09_jfet_drivers_1_12.kicad_sch")

cells = []
cells += jfet_quad(sh, "U5", "R14", "R15", [(36, 23), (88, 25), (133, 23), (178, 23)])
cells += jfet_quad(sh, "U6", "R22", "R23", [(33, 65), (84, 67), (131, 65), (174, 65)])
cells += jfet_quad(sh, "U11", "R24", "R25", [(33, 101), (84, 103), (131, 101), (175, 101)])
# PDF labels of the 12 cells in drawing order (input, output); None = the PDF label is the IPC name
PDF = [("JFET_GPIO_4", None), (None, None), (None, "JFET_1"), (None, None),
       ("JFET_GPIO_7", None), ("JFET_GPIO_8", None), ("JFET_GPIO_6", None), ("JFET_GPIO_5", None),
       ("JFET_GPIO_11", None), ("JFET_GPIO_12", None), ("JFET_GPIO_9", None), ("JFET_GPIO_10", None)]
# the alias table at the bottom of the page: IPC name = PDF name
ALIAS = [("GPIOR_19", "JFET_GPIO_11"), ("GPIOR_12", "JFET_GPIO_12"), ("GPIOR_15", "JFET_GPIO_9"),
         ("GPIOR_13", "JFET_GPIO_10"), ("GPIOT_N_17", "JFET_GPIO_7"), ("GPIOT_P_17", "JFET_GPIO_8"),
         ("GPIOT_N_14", "JFET_GPIO_6"), ("GPIOT_P_14", "JFET_GPIO_5"), ("GPIOL_10", "JFET_GPIO_3"),
         ("GPIOT_P_03", "JFET_GPIO_4"), ("GPIOL_11", "JFET_GPIO_1"), ("GPIOL_9", "JFET_GPIO_2")]
alias = {b: a for a, b in ALIAS}
alias["JFET_1"] = "A"                                         # page 10 pair
for (n_in, n_out), (p_in, p_out) in zip(cells, PDF):          # every PDF label = the IPC net or its alias
    assert n_in == alias.get(p_in, p_in or n_in), (n_in, p_in)
    assert n_out == alias.get(p_out, p_out or n_out), (n_out, p_out)

note(sh, "Proteus alias pairs of this page (the IPC name, left, is used on the pins):", 8, 127)
for i, (a, b) in enumerate(ALIAS):
    note(sh, f"{a} = {b}", 10 + 45 * (i // 6), 130 + 2 * (i % 6))
note(sh, "U5:C output: PDF JFET_1 = IPC net A (alias pair of page 10)", 100, 130)
note(sh, "PDF: a terminal JFET_GPIO_1 (= GPIOL_11) with an open wire stub stands above U5:C: no connection.", 100, 132)
note(sh, "JFET_GPIO_1, _2, _3 (GPIOL_11, GPIOL_9, GPIOL_10) feed no driver on this page: the cells of JFET_1, JFET_2", 100, 134)
note(sh, "and JFET_4 take GPIOL_N_14, GPIOL_P_14 and GPIOL_P_15 (STATUS.md findings).", 100, 136)
note(sh, "JFET_3 and JFET_4 reach no other part; JFET_5 and JFET_6 only an SMD test pad each (STATUS.md findings).", 100, 138)
sh.save()
print("sheet09: written")
