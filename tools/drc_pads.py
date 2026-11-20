#!/usr/bin/env python3
"""Per-refdes table of the DRC errors caused by footprint pads (read-only; stdlib only).

Reads <reports>/drc.json (written by `p2k drc`) and attributes every error-severity violation
whose type is not in DRC_ACCEPTED to the parts whose pads it names (shorting_items, clearance,
solder_mask_bridge, hole_clearance, ...). Violations that name no footprint pad are listed as
"other" (they are not a pad-size question). Used for STATUS.md "Phase 3 - pad sizes" and by
tools/drc_pending.py.

  python3 tools/drc_pads.py [drc.json]
"""
import json
import os
import re
import sys
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAD = re.compile(r"^(?:PTH |NPTH )?[Pp]ad (\S+) \[([^]]*)\] of (\S+)")
ACTUAL = re.compile(r"actual (-?[0-9.]+) mm")


def accepted_types():
    sys.path.insert(0, os.environ.get("P2K_BOARD", ROOT))
    import p2k_config
    return getattr(p2k_config, "DRC_ACCEPTED", {})


def classify(report):
    """-> (per_refdes {ref: {"types": {type: n}, "min": mm, "items": [str]}}, other [str], d)"""
    with open(report) as f:
        d = json.load(f)
    acc = accepted_types()
    per = defaultdict(lambda: {"types": defaultdict(int), "min": None, "items": []})
    other = []
    for v in d["violations"]:
        if v["severity"] != "error" or v["type"] in acc:
            continue
        descs = [i["description"] for i in v["items"]]
        pads = [PAD.match(x) for x in descs]
        refs = sorted({m.group(3) for m in pads if m})
        m = ACTUAL.search(v["description"])
        act = float(m.group(1)) if m else (0.0 if v["type"] in ("shorting_items", "solder_mask_bridge") else None)
        if not refs:
            other.append(f"{v['type']}: {v['description']}: " + " / ".join(descs))
            continue
        for r in refs:
            e = per[r]
            e["types"][v["type"]] += 1
            if act is not None and (e["min"] is None or act < e["min"]):
                e["min"] = act
            e["items"].append(f"{v['type']} {act if act is not None else ''}: " + " / ".join(descs))
    return per, other, d


def main():
    report = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "reports", "drc.json")
    per, other, d = classify(report)
    tot = defaultdict(int)
    for r in sorted(per, key=lambda r: (re.sub(r"\d+", "", r), int(re.sub(r"\D", "", r) or 0))):
        e = per[r]
        for t, n in e["types"].items():
            tot[t] += n
        ts = ", ".join(f"{n} {t}" for t, n in sorted(e["types"].items()))
        print(f"drc_pads: {r:7s} {ts}; smallest {e['min']:.4f} mm" if e["min"] is not None else f"drc_pads: {r:7s} {ts}")
    for o in other:
        print("drc_pads: other: " + o)
    print(f"drc_pads: {len(per)} parts with pad conflicts ({', '.join(f'{n} {t}' for t, n in sorted(tot.items()))} "
          f"attributions), {len(other)} other errors, {len(d.get('unconnected_items', []))} unconnected, "
          f"{len(d.get('schematic_parity', []))} parity")


if __name__ == "__main__":
    main()
