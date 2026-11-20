#!/usr/bin/env python3
"""Sheet 5 - FPGA IO banks (PDF page 5): U10 units D (bank R pairs), F (bank T pairs), E (bank B pairs)
and B (single-ended GPIOL / GPIOR balls). No other part on the page. Every connected ball carries the
label of its IPC net, the 53 N/C balls of the four units a no-connect flag (the PDF draws them without
a wire).

Proteus aliases (pages 1 and 10; the PDF labels the balls with the GPIO name, the IPC keeps the other
name): GPIOL_6 = LOOP_BYPASS_RLY (C3), GPIOR_21 = RLY3_ENABLE (N14), GPIOR_24 = MOS_GATE_1 (N13),
GPIOR_25 = MOS_GATE_3 (P15), GPIOR_27 = MDATA_DAB (P13), GPIOR_29 = SDATA1_ISO (R13). Single-ball
nets (STATUS.md finding 2): GPIOL_10 (B5), GPIOL_11 (C5), GPIOR_20 (D12), GPIOR_N_11 (G14),
GPIOT_N_01 (C6).

Differences from the PDF drawing (same nets): uniform 2.54 mm pin pitch (the PDF spaces the pairs);
the unit B labels are GPIOL_1 ... as in the IPC (pin names GPIOL_01 ...)."""
from _common import *  # noqa: F401,F403

sh = sheet("05_fpga_io_banks.kicad_sch")

fpga_unit(sh, 4, 46, 31)                                      # D: bank R
fpga_unit(sh, 6, 148, 30)                                     # F: bank T
fpga_unit(sh, 5, 47, 105)                                     # E: bank B
fpga_unit(sh, 2, 151, 92, alias={"GPIOL_6": "LOOP_BYPASS_RLY", "GPIOR_21": "RLY3_ENABLE",
                                 "GPIOR_24": "MOS_GATE_1", "GPIOR_25": "MOS_GATE_3",
                                 "GPIOR_27": "MDATA_DAB", "GPIOR_29": "SDATA1_ISO"})
for i, s in enumerate(["Proteus aliases (pages 1 and 10): the PDF labels these unit B balls with the GPIO name,",
                       "the IPC net keeps the other name:",
                       "GPIOL_6 = LOOP_BYPASS_RLY (C3)    GPIOR_21 = RLY3_ENABLE (N14)",
                       "GPIOR_24 = MOS_GATE_1 (N13)       GPIOR_25 = MOS_GATE_3 (P15)",
                       "GPIOR_27 = MDATA_DAB (P13)        GPIOR_29 = SDATA1_ISO (R13)"]):
    note(sh, s, 131, 116 + 2 * i)
sh.save()
print("sheet05: written")
