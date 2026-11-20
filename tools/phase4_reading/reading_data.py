# ---- my reading of source/schematic_pdf (300 dpi renders, by eye). "NC" = open stub, "~x" = unlabelled local node
ALIAS = """
p1: L1=PWM_TRANS5 N1=PWM_Q8 P1=PWM_Q6 T3=DAB_PWM_LO_SEC T4=DAB_PWM_HI_SEC RGB1_R=PWM_TRANS4 P8=DAB_PWM_PRI_LO_ISO
p1: R10=PWM_G3_ISO R12=PWM_TRANS3_ISO R13=PWM_TRANS1_ISO R14=CS1_ISO T15=ADASEL0_ISO ADB1=ISOADA2 ADB2=ISOADA3
p1: rx=T6 tx=R6 rx=GPIOL_2 tx=GPIOL_1 RLY3_ENABLE=GPIOR_21 MOS_GATE_1=GPIOR_24 T_IRQ=GPIOR_22
p1: GPIOR_28=MDATA_INU R3=PWM_Q5 R4=PWM_TRANS6 GPIOR_27=MDATA_DAB T7=ADCLK_DAB N8=DAB_PWM_PRI_HI_ISO
p1: PWM_G4_ISO=T11 PWM_TRANS2_ISO=T12 CLK1_ISO=T13 SDATA1_ISO=GPIOR_29 ADASEL1_ISO=R16 MOS_GATE_3=GPIOR_25 ISOADA1=ADB0 gnd=ISOGND
p2: TXD=GPIOL_N_09 RXD=GPIOL_P_10 clk32Mhz=GPIOR_P_19_PLLIN0
p7: AGND=DGND
p9: GPIOR_19=JFET_GPIO_11 GPIOR_12=JFET_GPIO_12 GPIOR_15=JFET_GPIO_9 GPIOR_13=JFET_GPIO_10 GPIOT_N_17=JFET_GPIO_7 GPIOT_P_17=JFET_GPIO_8
p9: GPIOT_N_14=JFET_GPIO_6 GPIOT_P_14=JFET_GPIO_5 GPIOL_10=JFET_GPIO_3 GPIOT_P_03=JFET_GPIO_4 GPIOL_11=JFET_GPIO_1 GPIOL_9=JFET_GPIO_2
p10: GPIOL_6=LOOP_BYPASS_RLY JFET_1=A JFET_13=C' JFET_15=D' POWERSDA=GPIOL_N_17 POWERSCL=GPIOL_N_16
p11: GPIOR_18=dac_clock GPIOR_16=dac_data bias_feedback=biasref
power rails (not drawn as a tie in the PDF; Proteus power rail configuration, IPC net GND=POWER): GND=DGND
"""
def two(page, ref, a, b): READ[(page, ref, "*")] = (a, b)      # two-pin part: the two nets, pin order not read
# page 1
R(1, "J8", {1: "rx", 2: "tx", 3: "ISOGND"}); R(1, "J4", {1: "GND"}); R(1, "J2", {1: "5V"}); R(1, "J5", {1: "12V"}); R(1, "J9", {1: "opamp_-15V"})
two(1, "R16", "3V3", "tx")
# page 2
R(2, "U10", dict(L3="~cdone", J5="~creset", N4="TCK", P3="TDI", M4="TDO", N3="TMS"))
R(2, "U10", dict(P2="GPIOL_P_00_PLLIN0", R2="GPIOL_N_00", P1="FLASH_nCE", N1="DCLK", N2="GPIOL_P_02", M2="GPIOL_N_02", M1="DATA0", L1="DATA1",
     H5="DATA2", H4="DATA3", K4="NC", J3="GPIOL_N_05", K3="NC", K2="GPIOL_N_06", K1="GPIOL_P_07", J1="GPIOL_N_07", J2="GPIOL_P_08", H3="NC",
     H1="GPIOL_P_09", G1="GPIOL_N_09", H2="GPIOL_P_10", G2="GPIOL_N_10", G5="NC", F5="NC", G3="NC", G4="NC", F3="NC", E3="NC",
     F1="GPIOL_P_14", F2="GPIOL_N_14", E2="GPIOL_N_15", E1="GPIOL_P_15", C1="GPIOL_N_16", D1="GPIOL_P_16", B1="GPIOL_P_17", C2="GPIOL_N_17",
     A2="GPIOL_N_18", B2="GPIOL_P_18"))
R(2, "FLASH1", {1: "FLASH_nCE", 2: "DATA1", 3: "DATA2", 4: "DGND", 5: "DATA0", 6: "DCLK", 7: "DATA3", 8: "1V8"})
R(2, "J1", {1: "TDI", 2: "TCK", 3: "TMS", 4: "TDO", 5: "DGND"})
R(2, "OSC1", {1: "1V8", 4: "1V8", 2: "DGND", 3: "clk32Mhz"})
for r, n in (("R4", "TDI"), ("R5", "TMS"), ("R6", "TDO"), ("R7", "TCK")): two(2, r, "3V3", n)
for r, n in (("R27", "~cdone"), ("R21", "~creset"), ("R3", "GPIOL_N_15"), ("R28", "GPIOL_P_02"), ("R41", "DATA0"), ("R42", "DCLK"), ("R43", "FLASH_nCE"), ("R44", "DATA1")): two(2, r, "1V8", n)
two(2, "C17", "~creset", "DGND"); two(2, "C2", "1V8", "DGND"); two(2, "C1", "1V8", "DGND")
# page 3
R(3, "V4", {1: "5V", 3: "5V", 2: "DGND", 5: "AD_3V3", 4: "~v4nr"}); two(3, "C19", "5V", "DGND"); two(3, "C20", "~v4nr", "DGND")
R(3, "PWR1", {3: "5V", 5: "1V_enable", 6: "NC", 4: "L1sw", 1: "~fb1", 2: "DGND"})
two(3, "L1", "L1sw", "1V8"); two(3, "R8", "~fb1", "1V8"); two(3, "C57", "~fb1", "1V8"); two(3, "R9", "~fb1", "DGND"); two(3, "C15", "5V", "DGND"); two(3, "C16", "1V8", "DGND")
R(3, "PWR2", {3: "5V", 5: "5V", 6: "1V_enable", 4: "L4sw", 1: "~fb2", 2: "DGND"})
two(3, "R1", "5V", "1V_enable"); two(3, "L4", "L4sw", "1V"); two(3, "R10", "~fb2", "1V"); two(3, "C70", "~fb2", "1V"); two(3, "R20", "~fb2", "DGND"); two(3, "R2", "~fb2", "DGND")
two(3, "C13", "5V", "DGND"); two(3, "C14", "1V", "DGND"); two(3, "C18", "1V", "DGND")
R(3, "PWR3", {3: "5V", 5: "1V_enable", 6: "NC", 4: "L5sw", 1: "~fb3", 2: "DGND"})
two(3, "L5", "L5sw", "3V3"); two(3, "R29", "~fb3", "3V3"); two(3, "C56", "~fb3", "3V3"); two(3, "R30", "~fb3", "DGND"); two(3, "R13", "~fb3", "DGND"); two(3, "C11", "5V", "DGND"); two(3, "C12", "3V3", "DGND")
# page 4
shifter(4, "U1", "GPIOL_P_09 GPIOL_P_08 GPIOL_N_07 GPIOL_N_05 GPIOL_P_07 GPIOL_P_02 GPIOL_N_02 GPIOL_N_06",
        "PWM_Q7 GPIO_BYPASS_RLY_ISO PWM_TRANS5 PWM_Q8 INU_ADCLK PWM_Q6 PWM_Q5 DAB_PWM_LO_SEC")
shifter(4, "U2", "GPIOB_P_00 GPIOB_N_01 GPIOB_P_01 GPIOB_N_02 GPIOB_P_02 GPIOB_N_07 GPIOB_N12 GPIOB_P_07",
        "DAB_PWM_HI_SEC PWM_TRANS6 PWM_TRANS4 ADCLK_DAB DAB_PWM_PRI_LO_ISO DAB_PWM_PRI_HI_ISO PWM_G3_ISO PWM_G1_ISO")
shifter(4, "U7", "GPIOB_P_12 GPIOB_N_14 GPIOB_P_14 GPIOB_P_17 GPIOB_N_15 GPIOB_N_17 GPIOB_P_15 GPIOB_P_13",
        "ADASEL1_ISO ADASEL0_ISO CS1_ISO CLK1_ISO PWM_TRANS1_ISO PWM_TRANS2_ISO PWM_TRANS3_ISO PWM_G4_ISO")
shifter(4, "U8", "GPIOR_P_11 GPIOR_P_13 GPIOR_N_13 GPIOR_P_16 GPIOR_N_16 GPIOR_P_18 GPIOR_N_18 GPIOR_N_19",
        "MOS_GATE_4 RLY1_ENABLE MOS_GATE_5 RLY4_ENABLE RLY2_ENABLE MOS_GATE_2 RLY5_ENABLE RLY6_ENABLE")
shifter(4, "U9", "GPIOR_N_02 GPIOR_N_05 GPIOR_P_07 GPIOR_N_09 GPIOR_P_05 GPIOR_N_07 GPIOR_P_09 GPIOR_N_06",
        "GPIO_BYPASS_RLY_ISOLATED ADCLK_ISO ADASEL2_ISO PWM_G2_ISO ADBSEL0 ADBSEL1 ADBSEL2 RLY7_ENABLE")
for c, a in (("C32", "1V8"), ("C34", "3V3"), ("C28", "1V8"), ("C31", "3V3"), ("C35", "1V8"), ("C37", "3V3"), ("C39", "1V8"), ("C38", "3V3"), ("C26", "1V8"), ("C27", "3V3")): two(4, c, a, "GND")
# page 5
R(5, "U10", dict(L11="NC", K11="NC", L12="NC", L13="NC", M14="NC", M15="GPIOR_N_02", K10="NC", J10="NC", K12="NC", J12="NC", L15="GPIOR_P_05", K15="GPIOR_N_05",
     K13="NC", J13="GPIOR_N_06", K14="GPIOR_P_07", J14="GPIOR_N_07", H10="NC", H11="NC", J15="GPIOR_P_09", H15="GPIOR_N_09",
     H13="NC", H12="NC", H14="GPIOR_P_11", G14="GPIOR_N_11", G13="NC", F13="NC", G15="GPIOR_P_13", F15="GPIOR_N_13", G11="NC", F11="NC", F12="NC", E12="NC",
     E15="GPIOR_P_16", E14="GPIOR_N_16", C13="NC", D13="NC", D15="GPIOR_P_18", D14="GPIOR_N_18", C14="GPIOR_P_19_PLLIN0", C15="GPIOR_N_19"))
R(5, "U10", dict(E6="NC", D5="NC", B6="GPIOT_P_01", C6="GPIOT_N_01", A5="GPIOT_P_03", A6="GPIOT_N_03", F7="NC", F8="NC", E7="NC", D7="NC", B7="GPIOT_P_06", A7="GPIOT_N_06",
     B8="GPIOT_P_07", A8="GPIOT_N_07", E8="NC", D8="NC", C8="NC", C9="NC", B9="GPIOT_P_11", A9="GPIOT_N_11", F9="NC", E9="NC", C10="NC", D10="NC",
     A10="GPIOT_P_14", B10="GPIOT_N_14", E10="NC", F10="NC", A11="GPIOT_P_17", B11="GPIOT_N_17"))
R(5, "U10", dict(R5="GPIOB_P_00", P5="GPIOB_N_00", R6="GPIOB_P_01", P6="GPIOB_N_01", R7="GPIOB_P_02", P7="GPIOB_N_02", N6="NC", M6="NC", L6="NC", K6="NC", M7="NC", L7="NC",
     R8="GPIOB_P_07", P8="GPIOB_N_07", N8="NC", M8="NC", K7="NC", L8="NC", M9="NC", L9="NC", K8="NC", K9="NC", R9="GPIOB_P_12", P9="GPIOB_N12", N10="GPIOB_P_13", M10="NC",
     R10="GPIOB_P_14", P10="GPIOB_N_14", R12="GPIOB_P_15", R11="GPIOB_N_15", P11="GPIOB_P_17", P12="GPIOB_N_17"))
R(5, "U10", dict(R3="GPIOL_1", R4="GPIOL_2", A3="GPIOL_3", B3="GPIOL_4", C3="GPIOL_6", C4="GPIOL_7", A4="GPIOL_9", B5="GPIOL_10", C5="GPIOL_11",
     A13="GPIOR_12", A12="GPIOR_13", B12="GPIOR_15", C12="GPIOR_16", B14="GPIOR_18", A14="GPIOR_19", D12="GPIOR_20", N14="GPIOR_21", P14="GPIOR_22", N13="GPIOR_24",
     P15="GPIOR_25", P13="GPIOR_27", R14="GPIOR_28", R13="GPIOR_29"))
# page 6
for b in "E13 G7 G9 H6 H8 J7 J9 M3 L5 L10 E5 G10".split(): R(6, "U10", {b: "1V"})
for b in "P4 N15 B4 B13".split(): R(6, "U10", {b: "3v3"})
for b in "J4 L2 D2 F4 C7 D6 C11 D9 F14 G12 J11 L14 N9 N11 N5 N7 D4 E11 L4 M11".split(): R(6, "U10", {b: "1V8"})
for b in "A1 A15 D3 G6 G8 H7 H9 J6 J8 M13 R1 R15".split(): R(6, "U10", {b: "DGND"})
for b, r in (("K5", "R40"), ("E4", "R39"), ("F6", "R38"), ("D11", "R37"), ("B15", "R36"), ("M12", "R35"), ("N12", "R32"), ("M5", "R11")):
    R(6, "U10", {b: "~ref" + r}); two(6, r, "~ref" + r, "DGND")
for c in "C36 C29 C30 C33".split(): two(6, c, "3v3", "DGND")
for c in "C21 C22 C23 C24 C25 C40".split(): two(6, c, "1v", "DGND")
# page 7
R(7, "U3", {13: "ADB2", 14: "ADB1", 15: "ADB0", 12: "ADB3", 1: "ADB4", 5: "ADB7", 2: "ADB5", 4: "ADB6", 11: "ADBSEL0", 10: "ADBSEL1", 9: "ADBSEL2", 6: "DGND", 3: "~mux",
            16: "AD_3V3", 7: "AGND", 8: "AGND"})
R(7, "U4", {3: "~mux", 4: "~u4out", 1: "~u4out", 5: "~avdd", 2: "AGND"})
R(7, "AD2", {8: "AGND", 7: "~ainp", 6: "~avdd", 5: "AGND", 1: "GPIOL_P_00_PLLIN0", 2: "GPIOL_N_00", 3: "GPIOB_N_00", 4: "1V8"})
two(7, "R12", "~u4out", "~ainp"); two(7, "C5", "~ainp", "AGND"); two(7, "C7", "~avdd", "AGND"); two(7, "C6", "~avdd", "AGND"); two(7, "L3", "AD_3V3", "~avdd")
two(7, "C9", "AD_3V3", "DGND"); two(7, "C10", "AD_3V3", "DGND"); two(7, "C71", "1V8", "DGND")
# page 8
R(8, "J11", {39: "12V", 40: "12V", 37: "NC", 38: "NC", 35: "3V3", 36: "3V3", 33: "DGND", 34: "DGND", 31: "INU_ADCLK", 32: "PWM_Q6", 29: "PWM_Q5", 30: "DAB_PWM_LO_SEC",
     27: "PWM_TRANS6", 28: "DAB_PWM_HI_SEC", 25: "MDATA_DAB", 26: "PWM_TRANS4", 23: "ADCLK_DAB", 24: "DAB_PWM_PRI_LO_ISO", 21: "DAB_PWM_PRI_HI_ISO", 22: "PWM_G3_ISO",
     19: "PWM_G1_ISO", 20: "PWM_G2_ISO", 17: "PWM_G4_ISO", 18: "PWM_TRANS3_ISO", 15: "PWM_TRANS2_ISO", 16: "PWM_TRANS1_ISO", 13: "CLK1_ISO", 14: "CS1_ISO",
     11: "SDATA1_ISO", 12: "ADASEL0_ISO", 9: "ADASEL1_ISO", 10: "ADASEL2_ISO", 7: "ADB3", 8: "ADB4", 5: "ADB2", 6: "ADB5", 3: "ADB1", 4: "ADB6", 1: "ADB0", 2: "ADB7"})
two(8, "C53", "12V", "DGND"); two(8, "C54", "3V3", "DGND")
# page 9
def opamp(page, ref, units, rin, rfb):
    R(page, ref, {4: "3V3", 11: "OPAMP_-15V"})
    for (plus, minus, out), (inp, outn), u in zip(((3, 2, 1), (5, 6, 7), (10, 9, 8), (12, 13, 14)), units, "ABCD"):
        R(page, ref, {plus: "gnd", minus: f"~{ref}{u}-", out: outn})
        READ[(page, rin, "u" + u)] = (inp, f"~{ref}{u}-"); READ[(page, rfb, "u" + u)] = (f"~{ref}{u}-", outn)
opamp(9, "U5", (("JFET_GPIO_4", "JFET_3"), ("GPIOL_P_15", "JFET_4"), ("GPIOL_N_14", "JFET_1"), ("GPIOL_P_14", "JFET_2")), "R14", "R15")
opamp(9, "U6", (("JFET_GPIO_7", "JFET_7"), ("JFET_GPIO_8", "JFET_8"), ("JFET_GPIO_6", "JFET_6"), ("JFET_GPIO_5", "JFET_5")), "R22", "R23")
opamp(9, "U11", (("JFET_GPIO_11", "JFET_11"), ("JFET_GPIO_12", "JFET_12"), ("JFET_GPIO_9", "JFET_9"), ("JFET_GPIO_10", "JFET_10")), "R24", "R25")
# page 10
R(10, "J7", {30: "3V3", 29: "3V3", 28: "GND", 27: "GND", 26: "MOS_GATE_4", 25: "MOS_GATE_1", 24: "MOS_GATE_5", 23: "RLY1_ENABLE", 22: "RLY2_ENABLE", 21: "RLY4_ENABLE",
     20: "RLY3_ENABLE", 19: "MOS_GATE_2", 18: "MOS_GATE_3", 17: "RLY5_enable", 16: "RLY7_ENABLE", 15: "RLY6_ENABLE", 14: "JFET_11", 13: "JFET_12", 12: "JFET_9", 11: "JFET_10",
     10: "JFET_7", 9: "JFET_8", 8: "GPIOT_P_11", 7: "GPIOT_N_11", 6: "GPIOT_P_07", 5: "GPIOT_N_07", 4: "GPIOT_P_06", 3: "GPIOT_N_06", 2: "GPIOT_N_03", 1: "GPIOT_P_01"})
R(10, "J6", {1: "3V3", 2: "3V3", 3: "GND", 4: "GND", 5: "biasfeedback", 7: "GPIOL_P_16", 9: "POWERSDA", 11: "POWERSCL", 13: "NC", 15: "BIASREF", 16: "BIASREF",
     6: "NC", 8: "NC", 10: "NC", 12: "NC", 14: "NC"})
R(10, "J3", {15: "LOOP_BYPASS_RLY", 13: "GPIOL_P_17", 11: "JFET_16", 9: "D'", 7: "C'", 5: "JFET_14", 3: "JFET_2", 1: "A", 2: "GND", 4: "GND", 6: "GND", 8: "GND", 10: "GND", 12: "GND", 14: "GND", 16: "GND"})
R(10, "ADC1", {"K1": "GPIOR_22", "COM1": "GPIOR_28", "K2": "NC", "COM2": "3V3", "A1": "~adcva", "A2": "gnd"})
two(10, "R31", "3V3", "GPIOR_28"); two(10, "R33", "3V3", "GPIOR_22"); two(10, "R34", "~adcva", "biasfeedback"); two(10, "C68", "~adcva", "gnd"); two(10, "C67", "3V3", "gnd")
# page 11
R(11, "U12", {2: "dac_clock", 3: "dac_data", 1: "gnd", 4: "3V3", 5: "gnd", 6: "biasref"})
two(11, "R19", "3V3", "dac_clock"); two(11, "R26", "3V3", "dac_data"); two(11, "R59", "biasref", "gnd"); two(11, "C4", "biasref", "gnd")
R(11, "PWR4", {2: "5V", 1: "GND", 3: "NC", 4: "NC", 7: "NC", 5: "ISO5V", 6: "rs485_gnd"}); two(11, "C55", "5V", "GND"); two(11, "C58", "ISO5V", "rs485_gnd")
R(11, "RS1", {1: "RXD", 2: "TXD", 3: "1V8", 4: "gnd", 5: "rs485_gnd", 6: "~rsA", 7: "~rsB", 8: "ISO5V"})
two(11, "R68", "ISO5V", "~rsB"); two(11, "R67", "~rsB", "~rsA"); two(11, "R69", "~rsA", "rs485_gnd")
R(11, "RS485B", {1: "~rsB"}); R(11, "RS485A", {1: "~rsA"}); R(11, "ISO5V", {1: "ISO5V"}); R(11, "ISO_G", {1: "rs485_gnd"}); two(11, "C51", "1V8", "gnd")
# page 12
opamp(12, "U14", (("GPIOL_9", "JFET_14"), ("GPIOL_3", "JFET_13"), ("GPIOL_4", "JFET_15"), ("GPIOL_7", "JFET_16")), "R17", "R18")
for c in "C60 C62 C64 C66".split(): two(12, c, "3V3", "GND")
for c in "C59 C61 C63 C65".split(): two(12, c, "GND", "OPAMP_-15V")
