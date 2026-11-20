#!/usr/bin/env python3
"""Phase 4: the board drills smaller than the Proteus drill are exactly the three decided J8 holes.

p2k ipc356_diff and p2k gerber_roundtrip accept a smaller KiCad drill by the *pair* of diameters in
p2k_config.py DRILL_SMALLER ((Proteus mm, KiCad mm)), not by pad: any other 1.016 mm Proteus hole
whose footprint drill became 1.0 mm (J1 has five such holes) would pass and only change the count
"3x 1.016->1.0" in their output (STATUS.md "p2k candidates"; found by the PI/FX conversion). This
board-local check closes that. It reads the Proteus IPC-D-356A file with its own small parser (no
p2k code), finds the board hole (pad or via, pcbnew) at every 317 record position (0.05 mm) and requires

  - exactly one plated board hole at every Proteus drilled record, and no other board hole,
  - the holes whose board drill is smaller than the Proteus drill (by more than 0.005 mm) to be
    exactly EXPECTED (user decision 2026-11-20: J8 pins 1-3, 1.016 -> 1.0), with those diameters,
  - the pairs of DRILL_SMALLER to be exactly the pairs of EXPECTED.

Larger board drills are listed per part (KiCad library footprints kept; information only).

Usage: tools/p2k/bin/kipy tools/check_drill_smaller.py [board.kicad_pcb]
"""
import math
import os
import re
import sys
from collections import Counter

import pcbnew

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BOARD = os.environ.get("P2K_BOARD", ROOT)
sys.dont_write_bytecode = True
sys.path.insert(0, BOARD)
import p2k_config as cfg  # noqa: E402

# (Proteus drill, KiCad drill) -> pads, as decided (STATUS.md "Decisions", J8 drill)
EXPECTED = {
    (1.016, 1.0): {("J8", "1"), ("J8", "2"), ("J8", "3")},
}
POS_TOL, DRILL_TOL = 0.05, 0.005
REC = re.compile(r"^317.{17}(.{6})-(.{4}).*?D(\d{4})([PU])A\d\dX([+-]\d+)Y([+-]\d+)X\d+")


def ipc_records(path):
    """(x, y, drill mm, plated, refdes, pin) of every 317 record (UNITS SI: 0.001 mm), IPC frame (Y up)."""
    out = []
    text = open(path, encoding="latin-1").read()
    if not re.search(r"^P  UNITS SI\s*$", text, re.M):
        raise SystemExit("check_drill_smaller: the IPC file is not in SI units")
    for line in text.splitlines():
        if not line.startswith("317"):
            continue
        m = REC.match(line)
        if not m:
            raise SystemExit(f"check_drill_smaller: cannot read the IPC record {line.rstrip()!r}")
        out.append((int(m[5]) / 1000, int(m[6]) / 1000, int(m[3]) / 1000, m[4] == "P", m[1].strip(), m[2].strip()))
    return out


def main():
    board_path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(BOARD, "kicad", f"{cfg.PROJECT}.kicad_pcb")
    board = pcbnew.LoadBoard(board_path)
    mm = pcbnew.ToMM
    holes = []    # (x, y, drill, plated, name)
    for fp in board.GetFootprints():
        for pad in fp.Pads():
            ds = pad.GetDrillSize()
            if ds.x > 0:
                p = pad.GetPosition()
                holes.append((mm(p.x), -mm(p.y), min(mm(ds.x), mm(ds.y)),
                              pad.GetAttribute() == pcbnew.PAD_ATTRIB_PTH, (fp.GetReference(), pad.GetNumber())))
    for t in board.GetTracks():
        if t.GetClass() == "PCB_VIA":
            p = t.GetPosition()
            holes.append((mm(p.x), -mm(p.y), mm(t.GetDrill()), True, ("via", f"{mm(p.x):.3f},{-mm(p.y):.3f}")))
    recs = ipc_records(os.path.join(BOARD, cfg.IPC))
    errors, smaller, larger, used = [], {}, Counter(), set()
    for x, y, d, plated, ref, pin in recs:
        near = [i for i, h in enumerate(holes) if math.hypot(h[0] - x, h[1] - y) <= POS_TOL]
        if len(near) != 1:
            errors.append(f"IPC record {ref}-{pin} at ({x}, {y}): {len(near)} board holes within {POS_TOL} mm")
            continue
        if near[0] in used:
            errors.append(f"IPC record {ref}-{pin} at ({x}, {y}): its board hole already belongs to another record")
        used.add(near[0])
        h = holes[near[0]]
        if ref and h[4] != (ref, pin):
            errors.append(f"IPC record {ref}-{pin} at ({x}, {y}): the board hole there is {h[4][0]}-{h[4][1]}")
        if h[3] != plated:
            errors.append(f"{h[4][0]}-{h[4][1]}: plated {plated} in Proteus, {h[3]} on the board")
        if h[2] < d - DRILL_TOL:
            smaller[h[4]] = (d, round(h[2], 4))
        elif h[2] > d + DRILL_TOL:
            larger[(h[4][0], d, round(h[2], 4))] += 1
    for i, h in enumerate(holes):
        if i not in used:
            errors.append(f"board hole {h[4][0]}-{h[4][1]} at ({h[0]:.3f}, {h[1]:.3f}): no IPC record")
    want = {pad: pair for pair, pads in EXPECTED.items() for pad in pads}
    for pad in sorted(set(smaller) - set(want)):
        errors.append(f"{pad[0]}-{pad[1]}: board drill {smaller[pad][1]} < Proteus {smaller[pad][0]}, not a decided hole")
    for pad in sorted(set(want) - set(smaller)):
        errors.append(f"{pad[0]}-{pad[1]}: expected a board drill smaller than Proteus {want[pad]}, it is not")
    for pad in sorted(set(want) & set(smaller)):
        if any(abs(a - b) > DRILL_TOL for a, b in zip(want[pad], smaller[pad])):
            errors.append(f"{pad[0]}-{pad[1]}: drills Proteus / board {smaller[pad]}, decided {want[pad]}")
    conf = set(getattr(cfg, "DRILL_SMALLER", {}))
    if conf != set(EXPECTED):
        errors.append(f"p2k_config.DRILL_SMALLER pairs {sorted(conf)} != the decided pairs {sorted(EXPECTED)}")
    for e in errors:
        print("check_drill_smaller:", e)
    counts = ", ".join(f"{len(pads)}x {a}->{b} ({' '.join(sorted({r for r, _ in pads}))})" for (a, b), pads in sorted(EXPECTED.items()))
    print(f"check_drill_smaller: {len(recs)} IPC drilled records, {len(holes)} board holes; smaller board drills: "
          f"{len(smaller)} (decided: {counts}); larger (KiCad footprint kept): "
          + (", ".join(f"{ref} {n}x {a}->{b}" for (ref, a, b), n in sorted(larger.items())) or "none"))
    print("check_drill_smaller: " + ("OK" if not errors else f"FAILED ({len(errors)} errors)"))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
