#!/usr/bin/env python3
"""`p2k ipc356 --check` with the two IPC features of this board the shared self-check rejects.

Board-local workaround (STATUS.md "p2k candidates"); everything else is the shared check
(counts, aliases, KiCad refdes, via / hole drills, reference/ up to date). Accepted exactly,
from p2k_config.py:

  SPLIT_PIN_NETS  two-pad terminals (both pads pin 1) whose pads carry different IPC nets
                  (Proteus names them <net>.<id>): the shared check reports them as
                  "same refdes-pin on different nets"; accepted when the set of such pins and
                  their nets (IPC file order) equal the table.
  SMD_FREE_PADS   SMD pads with a blank refdes (test pads): `p2k ipc356` makes them
                  `free_pad` records and the shared check wants a plated drill; accepted when
                  each is an unplated top SMD record without drill at the table position with
                  the table's raw net, and every table entry is found.

  python3 tools/ipc356_check.py      exit 1 on any other self-check error
"""
import os
import sys
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools", "p2k"))
os.environ.setdefault("P2K_BOARD", ROOT)

from p2k import ipc356  # noqa: E402

CFG = ipc356.CFG
SPLIT = getattr(CFG, "SPLIT_PIN_NETS", {})
SMD_FREE = getattr(CFG, "SMD_FREE_PADS", {})


def main():
    net_names, pads = ipc356.parse(ipc356.DEFAULT_IPC)
    st, errors = ipc356.self_check(net_names, pads, ipc356.REF_DIR)
    accepted, extra = [], []

    # split pin nets
    pin_nets = defaultdict(list)
    for p in pads:
        if p["kind"] == "pad" and p["net_raw"] not in pin_nets[(p["refdes"], p["pin"])]:
            pin_nets[(p["refdes"], p["pin"])].append(p["net_raw"])
    conflicts = {k: tuple(v) for k, v in pin_nets.items() if len(v) > 1}
    msg = f"same refdes-pin on different nets: {sorted(conflicts)}"
    if conflicts:
        if conflicts == SPLIT:
            if msg in errors:
                errors.remove(msg)
            accepted.append(f"{len(conflicts)} two-pad pins on split nets (SPLIT_PIN_NETS): "
                            + ", ".join(f"{r}-{p}" for r, p in sorted(conflicts)))
        else:
            for k in sorted(set(conflicts) | set(SPLIT)):
                if conflicts.get(k) != SPLIT.get(k):
                    extra.append(f"split pin {k}: IPC {conflicts.get(k)}, SPLIT_PIN_NETS {SPLIT.get(k)}")
    elif SPLIT:
        extra.append(f"SPLIT_PIN_NETS lists {sorted(SPLIT)} but the IPC has no split pins")

    # SMD pads without a part
    found = set()
    for p in pads:
        if p["kind"] != "free_pad":
            continue
        key = (p["x_mm"], p["y_mm"])
        if (key in SMD_FREE and not p["is_tht"] and p["side"] == "top" and not p["plated"]
                and p["drill"] == 0 and p["net_raw"] == SMD_FREE[key]):
            m = f"free pad at ({p['x_mm']}, {p['y_mm']}): drill {p['drill']}"
            if m in errors:
                errors.remove(m)
            found.add(key)
    if found:
        accepted.append(f"{len(found)} SMD test pads without refdes (SMD_FREE_PADS)")
    for key in sorted(set(SMD_FREE) - found):
        extra.append(f"SMD_FREE_PADS entry {key} {SMD_FREE[key]}: no matching IPC record")

    errors += extra
    print("ipc356: " + ", ".join(f"{k}={v}" for k, v in st.items()))
    for a in accepted:
        print("  accepted (board-local): " + a)
    for e in errors:
        print("  FAIL " + e)
    print("ipc356: " + ("FAIL" if errors else "OK"))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
