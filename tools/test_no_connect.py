#!/usr/bin/env python3
"""Negative test of decision D2 (no pin of type no_connect; ERC no_connect_connected is fatal).

Builds a scratch copy of the board in build/tmp/nctest (kicad/, lib/, reference/,
p2k_config.py), redraws sheet 11 there with only PWR4 (IZB03; pin 4 "NC" is N/C in the IPC)
in six variants and runs the real checks (p2k erc, p2k compare_netlists) on it:

  ok           pin 4 open with a no-connect flag                     -> ERC and compare pass
  wired_flag   pin 4 wired to pin 5 (ISO5V), flag kept               -> ERC fails, compare fails
  wired        pin 4 wired to pin 5, no flag                         -> compare fails
  old_lib      as wired_flag, but pin 4 of type no_connect (the      -> compare PASSES (the blind
               library before D2)                                       spot), ERC fails (fatal warning)
  joined_flag  pins 4 and 7 (both N/C) wired to each other, a flag   -> ERC fails (fatal warning); compare
               on pin 4 (KiCad: one unconnected-(...) net, 2 pins)      fails through the strict check
                                                                        nc_joined (on by default)
  joined       pins 4 and 7 wired to each other, no flag             -> compare fails (Net-(PWR4-NC))

Exit status 0 when every variant behaves as listed. Not part of check_all.sh (slow, needs the
scratch copy); run it after a change of ERC_FATAL_WARNINGS, tools/gen_symbols.py or the p2k pin.
"""
import os
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRATCH = os.path.join(ROOT, "build", "tmp", "nctest")
SHEET = "11_bias_dac_rs485.kicad_sch"
#           variant        ERC ok  compare ok
EXPECT = {"ok":         (True, True),
          "wired_flag": (False, False),
          "wired":      (None, False),
          "old_lib":    (False, True),
          "joined_flag": (False, False),
          "joined":     (None, False)}


def draw(variant):
    """Runs in a subprocess with P2K_BOARD = the scratch board."""
    sys.path.insert(0, os.path.join(ROOT, "tools", "sheets"))
    from _common import sheet, flagged_power, power_at, g, sym, sh_value
    from p2k import board
    for _, _, fname in board.config().SHEETS:      # the test does not depend on what is drawn so far
        sheet(fname).save()
    sh = sheet(SHEET)
    p = sh.place(sym("PWR4"), "PWR4", g(80), g(60), value=sh_value("PWR4"))
    for pin, net, dx in ((1, "GND", -6), (2, "5V", -10)):
        x, y = p.pin(pin)
        q = (round(x + g(dx), 4), y)
        sh.wire((x, y), q)
        flagged_power(sh, net, *q)
    power_at(sh, "ISO5V", p.pin(5), "right")
    power_at(sh, "RS485_GND", p.pin(6), "right")
    joined = variant in ("joined_flag", "joined")
    for pin in (3,) if joined else (3, 7):
        sh.no_connect(*p.pin(pin))
    if variant not in ("wired", "joined"):
        sh.no_connect(*p.pin(4))
    if joined:
        x4, y4 = p.pin(4)
        x7, y7 = p.pin(7)
        xx = round(x4 + g(8), 4)
        sh.wire((x4, y4), (xx, y4), (xx, y7), (x7, y7))
    elif variant != "ok":
        x4, y4 = p.pin(4)
        x5, y5 = p.pin(5)
        sh.wire((x4, y4), (round(x4 + g(2), 4), y4), (round(x4 + g(2), 4), y5))
        sh.wire((x5, y5), (round(x5 + g(2), 4), y5))
    sh.save()


def run(variant):
    shutil.rmtree(SCRATCH, ignore_errors=True)
    os.makedirs(SCRATCH)
    for d in ("kicad", "lib", "reference"):
        shutil.copytree(os.path.join(ROOT, d), os.path.join(SCRATCH, d))
    shutil.copy(os.path.join(ROOT, "p2k_config.py"), SCRATCH)
    if variant == "old_lib":
        path = os.path.join(SCRATCH, "lib", "tube_control_card.kicad_sym")
        s = open(path).read()
        i = s.index('(symbol "IZB03"')
        j = s.index('(name "NC"', i)
        k = s.rindex("(pin passive line", i, j)
        s = s[:k] + "(pin no_connect line" + s[k + len("(pin passive line"):]
        open(path, "w").write(s)
    env = dict(os.environ, P2K_BOARD=SCRATCH)
    subprocess.run([sys.executable, __file__, "--draw", variant], env=env, check=True)
    p2k = os.path.join(ROOT, "tools", "p2k", "bin", "p2k")
    erc = subprocess.run([p2k, "erc", "--no-pending", os.path.join(SCRATCH, "kicad", "tube_control_card.kicad_sch"),
                          os.path.join(SCRATCH, "erc.rpt")], env=env, capture_output=True, text=True)
    cmp_ = subprocess.run([p2k, "compare_netlists", "--allow-missing", "--sheet", "11"],
                          env=env, capture_output=True, text=True)
    return erc, cmp_


def main():
    if sys.argv[1:2] == ["--draw"]:
        return draw(sys.argv[2])
    bad = 0
    for variant, (erc_ok, cmp_ok) in EXPECT.items():
        erc, cmp_ = run(variant)
        got = (erc.returncode == 0, cmp_.returncode == 0)
        ok = (erc_ok is None or got[0] == erc_ok) and got[1] == cmp_ok
        bad += not ok
        word = lambda b: "pass" if b else "FAIL"
        print(f"{variant:12s} ERC {word(got[0])}, compare {word(got[1])}   -> {'as expected' if ok else 'UNEXPECTED'}")
        for line in (erc.stdout + cmp_.stdout).splitlines():
            if "no_connect" in line or "N/C mismatch" in line or "joins" in line or line.startswith(("ERROR", "erc:")) or "@(" in line:
                print("     " + line.strip())
    print("test_no_connect: " + ("OK" if not bad else f"{bad} variant(s) unexpected"))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
