#!/usr/bin/env python3
"""`p2k compare_netlists` with the split terminal nets of decision D1 accepted.

Board-local workaround (STATUS.md "Decisions" D1 and "p2k candidates"). Five two-pad
terminals (J2, ISO5V, ISO_G, RS485A, RS485B) have their two pads (both pin 1) on different
IPC nets. The user decided (D1, 2026-11-20) to draw each as one pin as in the PDF, so KiCad
puts both pads on one net. The shared compare keys IPC pins by (refdes, pin) - the later pad
record wins - and would report each of these as a merge of two IPC nets.

This wrapper checks that the IPC split pins are exactly `SPLIT_PIN_MERGES` of p2k_config.py
(pin -> (kept net, merged net)), joins each merged IPC net into its kept net (all its pins,
e.g. R67-1 on RS485B's second net), and then runs the shared comparison unchanged on that
IPC side. Any other merge, split or wrong-net pin still fails.

Phase 4 addition (joined N/C pins): the shared compare treats every pin of a KiCad net named
`unconnected-(...)` as a singleton, so two N/C pins wired to each other with a no-connect flag
on the wire (KiCad then puts both in ONE such net) pass as two N/C pins (tools/test_no_connect.py
variant `joined_flag`: "compare: OK"; only the fatal ERC warning no_connect_connected caught it).
Here the netlist must also have exactly one pin in every `unconnected-(...)` net.

  python3 tools/compare_netlists.py [p2k compare_netlists options, e.g. --allow-missing --sheet 11]
"""
import json
import os
import sys
import xml.etree.ElementTree as ET
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools", "p2k"))
os.environ.setdefault("P2K_BOARD", ROOT)

from p2k import board, compare_netlists  # noqa: E402

MERGES = getattr(board.config(), "SPLIT_PIN_MERGES", {})
_shared_load_ipc = compare_netlists.load_ipc


def split_pins():
    """{(refdes, pin): {IPC nets of its pads}} for pins whose pads are on several nets."""
    ipc = json.load(open(board.path("reference", "ipc356_pads.json")))
    nets = defaultdict(set)
    for p in ipc["pads"]:
        if p["kind"] == "pad":
            nets[(p["refdes"], p["pin"])].add(p["net"])
    return {k: v for k, v in nets.items() if len(v) > 1}


def load_ipc_d1():
    pin_net = _shared_load_ipc()
    split = split_pins()
    errors = []
    for k in sorted(set(split) | set(MERGES)):
        if k not in MERGES:
            errors.append(f"IPC pin {k[0]}-{k[1]} has pads on {sorted(split[k])}, not in SPLIT_PIN_MERGES")
        elif k not in split or split[k] != set(MERGES[k]):
            errors.append(f"SPLIT_PIN_MERGES {k[0]}-{k[1]} {MERGES[k]} != IPC pad nets {sorted(split.get(k, []))}")
    if errors:
        sys.exit("compare_netlists (D1): " + "; ".join(errors))
    rename = {merged: kept for kept, merged in MERGES.values()}
    notes = []
    for (ref, pin), (kept, merged) in sorted(MERGES.items()):
        others = sorted(f"{r}-{p}" for (r, p), n in pin_net.items() if n == merged and (r, p) != (ref, pin))
        notes.append(f"{ref}-{pin} {kept} + {merged}" + (f" (with {' '.join(others)})" if others else ""))
    print(f"accepted (D1, board-local): {len(MERGES)} merged IPC net pairs: " + "; ".join(notes))
    out = {rp: rename.get(n, n) for rp, n in pin_net.items()}
    for rp, (kept, _) in MERGES.items():
        out[rp] = kept
    return out


_shared_load_kicad, _joined = compare_netlists.load_kicad, []


def load_kicad_nc(path):
    for net in ET.parse(path).getroot().iter("net"):
        nodes = sorted((n.get("ref"), n.get("pin")) for n in net.findall("node"))
        if net.get("name", "").startswith("unconnected-(") and len(nodes) != 1:
            _joined.append((net.get("name"), nodes))
    return _shared_load_kicad(path)


def main():
    rc = compare_netlists.main()
    for name, nodes in _joined:
        print(f"ERROR: KiCad net {name} joins {len(nodes)} pins: " + " ".join(f"{r}-{p}" for r, p in nodes)
              + " (N/C pins wired together)")
    if _joined:
        print(f"compare: FAILED ({len(_joined)} unconnected-(...) nets with more than one pin)")
    return 1 if _joined else rc


compare_netlists.load_ipc = load_ipc_d1
compare_netlists.load_kicad = load_kicad_nc

if __name__ == "__main__":
    sys.exit(main())
