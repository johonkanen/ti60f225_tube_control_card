#!/usr/bin/env python3
"""DRC and the copper check after the zone fill, with this board's accepted differences
(board-local; stdlib only, runs under the system python3).

  python3 tools/drc_check.py drc      runs `p2k drc`; it passes as it does, or when its only
        failures are
          (D1, permanent until p2k handles split pins, p2k candidate 1) exactly one
              unconnected item per decision-D1 terminal net (SPLIT_PIN_MERGES: the KiCad net
              of J2-1, ISO5V-1, ISO_G-1, RS485A-1, RS485B-1 from the schematic netlist), every
              item of it on that net: the second pad of each terminal has no copper to the
              first (finding 1);
          (pad sizes, while PENDING is not empty) exactly the recorded DRC errors per type
              (PENDING_DRC), each naming a pad of a PENDING part -> PENDING USER DECISION.
  python3 tools/drc_check.py copper   runs `tools/pcb_wrap.py assign_nets --check` (D1 opens are
        accepted there); it passes as it does, or (while PENDING is not empty) when its only
        failure is short groups whose touching pairs (reports/assign_nets.txt) all have a pad of
        a PENDING part, exactly PENDING_TOUCH of them, 0 orphans / opens / foreign nets
        -> PENDING USER DECISION.

Anything else fails. Once the pad-size decision is applied, PENDING becomes empty (then any
pad conflict fails) and only the D1 acceptance remains.
"""
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BOARD = os.environ.get("P2K_BOARD", ROOT)
BIN = os.path.join(ROOT, "tools", "p2k", "bin")
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, os.path.join(ROOT, "tools", "p2k"))
os.environ.setdefault("P2K_BOARD", ROOT)

import drc_pads  # noqa: E402

# Pad-size decision (STATUS.md "Phase 3 - pad sizes"): the parts whose KiCad pads collide with
# Proteus copper, and the DRC / copper-check items they cause with FOOTPRINT_PAD_SIZES = "kicad".
PENDING = ("ADC1", "J7", "J11", "U1", "U2", "U3", "U4", "U5", "U6", "U7", "U8", "U9", "U11", "U12", "U14")
PENDING_DRC = {"clearance": 85, "hole_clearance": 2, "shorting_items": 13, "solder_mask_bridge": 17}
PENDING_TOUCH = 17

NET = re.compile(r"\[([^]]*)\]")


def run(cmd):
    r = subprocess.run(cmd, cwd=BOARD, capture_output=True, text=True)
    sys.stdout.write(r.stdout + r.stderr)
    return r.returncode, r.stdout


def d1_nets():
    from p2k import board, pcb
    merges = board.config().SPLIT_PIN_MERGES
    _, nets = pcb.export_netlist()
    out = {}
    for name, nodes in nets.items():
        for rp in nodes:
            if rp in merges:
                out[name] = f"{rp[0]}-{rp[1]}"
    if len(out) != len(merges):
        raise SystemExit(f"drc_check: D1 pins {sorted(merges)} found on {len(out)} nets")
    return out


def drc():
    rc, _ = run([os.path.join(BIN, "p2k"), "drc"])
    if rc == 0:
        return 0
    report = os.path.join(BOARD, "reports", "drc.json")
    with open(report) as f:
        d = json.load(f)
    bad = []
    want = d1_nets()
    seen = []
    for u in d.get("unconnected_items", []):
        nets = {m.group(1) for i in u["items"] for m in [NET.search(i["description"])] if m}
        if len(nets) == 1 and next(iter(nets)) in want:
            seen.append(next(iter(nets)))
        else:
            bad.append("unconnected: " + " / ".join(i["description"] for i in u["items"]))
    if sorted(seen) != sorted(want):
        bad.append(f"D1 unconnected items on {sorted(seen)}, expected one on each of {sorted(want)}")
    if d.get("schematic_parity"):
        bad.append(f"{len(d['schematic_parity'])} parity issues")
    per, other, _ = drc_pads.classify(report)
    bad += other
    got = {}
    for ref, e in per.items():
        if ref not in PENDING:
            bad += [f"{ref}: {x}" for x in e["items"]]
    # count each violation once (a violation can name pads of two parts)
    acc = drc_pads.accepted_types()
    for v in d["violations"]:
        if v["severity"] == "error" and v["type"] not in acc:
            got[v["type"]] = got.get(v["type"], 0) + 1
    if got and got != PENDING_DRC:
        bad.append(f"pad-size items {got}, recorded {PENDING_DRC}")
    if bad:
        for b in bad[:20]:
            print("drc_check: " + b)
        print("drc_check: FAILED")
        return 1
    print(f"drc_check: accepted (D1, board-local): {len(seen)} unconnected items, one per split terminal net: "
          + ", ".join(f"{want[n]} {n}" for n in sorted(seen)))
    if got:
        print("drc_check: PENDING USER DECISION: " + ", ".join(f"{n} {t}" for t, n in sorted(got.items()))
              + " between KiCad pads of " + " ".join(PENDING) + " and Proteus copper (STATUS.md Phase 3 - pad sizes)")
    else:
        print("drc_check: OK")
    return 0


def copper():
    rc, out = run([os.path.join(BIN, "kipy"), os.path.join(ROOT, "tools", "pcb_wrap.py"), "assign_nets", "--check"])
    if rc == 0:
        return 0
    m = re.search(r"after zone fill: \d+ groups, (\d+) shorts, (\d+) orphans, (\d+) opens.*?, (\d+) items with a foreign net", out)
    with open(os.path.join(BOARD, "reports", "assign_nets.txt")) as f:
        rep = f.read().split("== after zone fill")[-1]
    lines = [l for l in rep.splitlines() if l.startswith("  touching on")]
    pend = [l for l in lines if any(re.search(r"(^|[\s:])%s-\S+ \[" % r, l) for r in PENDING)]
    ok = (PENDING and m and int(m.group(1)) >= 1 and m.group(2) == m.group(3) == m.group(4) == "0"
          and len(lines) == PENDING_TOUCH and len(pend) == len(lines))
    if not ok:
        print(f"drc_check: FAILED (copper: {len(pend)}/{len(lines)} touching pairs at pending pads, "
              f"recorded {PENDING_TOUCH}; summary {m.groups() if m else None})")
        return 1
    print(f"drc_check: PENDING USER DECISION: {len(lines)} KiCad pads touching Proteus copper in {m.group(1)} short groups "
          "(STATUS.md Phase 3 - pad sizes)")
    return 0


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    if mode not in ("drc", "copper"):
        sys.exit(__doc__)
    sys.exit(drc() if mode == "drc" else copper())
