#!/usr/bin/env python3
"""Run a Phase 3 p2k PCB tool with this board's three accepted differences (board-local,
STATUS.md "p2k candidates" 1, 2/21, 3; the shared tools run unchanged on adapted inputs).

  tools/p2k/bin/kipy tools/pcb_wrap.py TOOL [ARGS...]     TOOL = build_pcb, gerber_to_tracks,
        assign_nets, pours_to_zones, check_board (p2k.<TOOL>.main() after the patches)

1. Decision D1 (split terminal nets): the five split terminals J2, ISO5V, ISO_G, RS485A, RS485B
   have both pads (pin 1) on one KiCad net, the IPC two nets per pin. The IPC records are
   filtered (`p2k.pcb.configure(records=...)`): the wrapper first checks that the IPC pins with
   pads on two nets are exactly SPLIT_PIN_MERGES (with exactly those nets), then renames each
   merged IPC net to its kept net in every record (pads incl. R67-1, vias, free pads), as
   tools/compare_netlists.py does for the schematic. Any other merge or split still fails
   (`ipc_to_kicad_nets` reports it). The second pad of each terminal has no copper connection
   to the first, so every D1 net is open in the copper: `assign_nets` accepts an open exactly
   when its net is the KiCad net of a D1 pin, it has two groups and the two pads of that pin
   lie in different groups (listed as "accepted open (D1)" in the report); any other open
   still fails --check.
2. U10 balls: Proteus writes them with the aperture function `BGAPad,CuDef`, which
   gerber_to_tracks rejects; `p2k.gerber.parse` renames it to `SMDPad,CuDef` (the board-local
   check_sources.py checks that these 225 flashes are the U10 balls).
3. SMD test pads (SMD_FREE_PADS, board-only FREE_PAD_FOOTPRINT = an SMD pad on F.Cu): their
   Top Copper flashes are SMDPad flashes, which gerber_to_tracks wants on a part pad; the four
   flashes at SMD_FREE_PADS (exactly four, top only, 0.711 mm round) are moved to the OtherPad
   list, so they must land on a board-only pad. check_board expects free pads plated THT;
   for the SMD_FREE_PADS records it checks instead: exactly one board-only pad there, SMD,
   on F.Cu only (copper), the IPC size, on the IPC net.
4. Net names of unconnected pins with a "/" in the pin name (PWR4 pin 3 "On/Off"): the kicadxml
   netlist writes `unconnected-(PWR4-On/Off-Pad3)`, the schematic (DRC parity) knows the net as
   `unconnected-(PWR4-On{slash}Off-Pad3)`, so build_pcb's pad net fails the parity check. The
   wrapper escapes "/" inside the parentheses of `unconnected-(...)` names of the exported
   netlist (KiCad's own escaping; hierarchical "/" separators of other nets are untouched).
"""
import math
import os
import importlib
import sys
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools", "p2k"))
os.environ.setdefault("P2K_BOARD", ROOT)

from p2k import board, gerber, pcb  # noqa: E402

CFG = board.config()
MERGES = CFG.SPLIT_PIN_MERGES
SMD_FREE = CFG.SMD_FREE_PADS
D1_REFS = {ref for ref, _ in MERGES}


# ---------------------------------------------------------------- 1. D1

def d1_records(recs):
    nets = defaultdict(set)
    for p in recs:
        if p["kind"] == "pad":
            nets[(p["refdes"], p["pin"])].add(p["net"])
    split = {k: v for k, v in nets.items() if len(v) > 1}
    errors = []
    for k in sorted(set(split) | set(MERGES)):
        if k not in MERGES:
            errors.append(f"IPC pin {k[0]}-{k[1]} has pads on {sorted(split[k])}, not in SPLIT_PIN_MERGES")
        elif split.get(k) != set(MERGES[k]):
            errors.append(f"SPLIT_PIN_MERGES {k[0]}-{k[1]} {MERGES[k]} != IPC pad nets {sorted(split.get(k, []))}")
    if errors:
        raise SystemExit("pcb_wrap (D1): " + "; ".join(errors))
    rename = {merged: kept for kept, merged in MERGES.values()}
    out = []
    for p in recs:
        if p["net"] in rename:
            p = dict(p, net=rename[p["net"]])
        out.append(p)
    return out


def patch_assign_nets():
    from p2k import assign_nets as an
    shared_analyse, shared_describe = an.analyse, an.describe

    def analyse(items, uf):
        res = shared_analyse(items, uf)
        group_of = {}
        for g, members in res["groups"].items():
            for i in members:
                group_of[i] = g
        d1 = defaultdict(list)   # KiCad net -> [(label, group)] of the D1 pin pads
        for i, it in enumerate(items):
            if it.kind == "pad" and it.obj.GetParentFootprint().GetReference() in D1_REFS \
                    and (it.obj.GetParentFootprint().GetReference(), it.obj.GetNumber()) in MERGES:
                d1[it.net].append((it.label, group_of[i]))
        keep, acc = [], []
        for net, gs in res["opens"]:
            pads = d1.get(net, [])
            if len(gs) == 2 and len(pads) == 2 and {g for _, g in pads} == set(gs):
                acc.append(f"{net}: {pads[0][0]} pads in two groups")
            else:
                keep.append((net, gs))
        res["opens"] = keep
        res["d1_accepted"] = acc
        return res

    def describe(name, items, res, out):
        shared_describe(name, items, res, out)
        for a in res.get("d1_accepted", []):
            out.append("  accepted open (D1, board-local): " + a)

    an.analyse, an.describe = analyse, describe
    shared_summary = an.summary

    def summary(name, res):
        s = shared_summary(name, res)
        n = len(res.get("d1_accepted", []))
        return s + (f" (+{n} accepted D1 opens)" if n else "")

    an.summary = summary


# ---------------------------------------------------------------- 4. "/" in unconnected net names

def patch_export_netlist():
    shared = pcb.export_netlist

    def export_netlist():
        comps, nets = shared()
        out = {}
        for name, nodes in nets.items():
            if name.startswith("unconnected-(") and name.endswith(")") and "/" in name:
                name = "unconnected-(" + name[len("unconnected-("):-1].replace("/", "{slash}") + ")"
            out[name] = nodes
        return comps, out

    pcb.export_netlist = export_netlist


# ---------------------------------------------------------------- 2. BGAPad

def patch_gerber():
    shared_parse = gerber.parse

    def parse(path):
        g = shared_parse(path)
        for ap in g.apertures.values():
            if ap.function == "BGAPad,CuDef":
                ap.function = "SMDPad,CuDef"
        return g

    gerber.parse = parse


# ---------------------------------------------------------------- 3. SMD test pads

def smd_free_records(recs):
    out = [p for p in recs if p["kind"] == "free_pad" and not p["is_tht"]
           and (p["x_mm"], p["y_mm"]) in SMD_FREE and SMD_FREE[(p["x_mm"], p["y_mm"])] == p["net_raw"]]
    if len(out) != len(SMD_FREE):
        raise SystemExit(f"pcb_wrap: {len(out)} of {len(SMD_FREE)} SMD_FREE_PADS found as SMD free pads in the IPC")
    return out


def at_test_pad(x, y):
    return any(abs(x - a) <= 0.01 and abs(y - b) <= 0.01 for a, b in SMD_FREE)


def patch_gerber_to_tracks():
    from p2k import gerber_to_tracks as g2t
    shared_load_layer = g2t.load_layer

    def load_layer(gname, layer, user):
        cl = shared_load_layer(gname, layer, user)
        moved = [f for f in cl.pads if at_test_pad(f.x, f.y)]
        want = len(SMD_FREE) if layer == "F.Cu" else 0
        bad = [f for f in moved if f.ap.shape != "C" or abs(f.ap.params[0] - 0.711) > 0.001
               or not f.ap.function.startswith("SMDPad")]
        if len(moved) != want or bad:
            raise SystemExit(f"pcb_wrap: {layer}: {len(moved)} SMD test-pad flashes (want {want}), {len(bad)} not 0.711 mm SMD pads")
        cl.pads = [f for f in cl.pads if not at_test_pad(f.x, f.y)]
        cl.other_pads += moved
        return cl

    g2t.load_layer = load_layer


def patch_check_board():
    import pcbnew
    from p2k import check_board as cb
    shared = cb.check_board_only

    def check_board_only(brd, recs, mapping, kind, errors):
        if kind != "free_pad":
            return shared(brd, recs, mapping, kind, errors)
        smd = smd_free_records(recs)
        n, found = shared(brd, [p for p in recs if p not in smd], mapping, kind, errors)
        for h in smd:
            hit = [(fp, pad) for fp in brd.GetFootprints() if fp.IsBoardOnly() for pad in fp.Pads()
                   if math.hypot(pcbnew.ToMM(pad.GetPosition().x) - h["x_mm"],
                                 -pcbnew.ToMM(pad.GetPosition().y) - h["y_mm"]) < 0.01]
            if len(hit) != 1:
                errors.append(f"SMD test pad at ({h['x_mm']}, {h['y_mm']}): {len(hit)} board pads")
                continue
            fp, pad = hit[0]
            net = mapping.get(h["net"])
            cu = [l for l in (pcbnew.F_Cu, pcbnew.In1_Cu, pcbnew.In2_Cu, pcbnew.B_Cu) if pad.IsOnLayer(l)]
            if pad.GetAttribute() != pcbnew.PAD_ATTRIB_SMD or cu != [pcbnew.F_Cu] \
                    or abs(pcbnew.ToMM(pad.GetSizeX()) - h["pad_w"]) > 1e-3 \
                    or abs(pcbnew.ToMM(pad.GetSizeY()) - h["pad_h"]) > 1e-3 or pad.GetNetname() != (net or "?"):
                errors.append(f"{fp.GetReference()}: SMD test pad attribute {pad.GetAttribute()}, copper layers {cu}, "
                              f"{pcbnew.ToMM(pad.GetSizeX())} mm, net {pad.GetNetname()!r} "
                              f"(want SMD on F.Cu only, {h['pad_w']} mm, net {net!r})")
            else:
                found += 1
        print(f"check_board (board-local): {len(smd)} SMD test pads (SMD_FREE_PADS) checked as SMD pads on F.Cu "
              "(size, net)")
        return n + len(smd), found

    cb.check_board_only = check_board_only


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    tool = sys.argv[1]
    if tool not in ("build_pcb", "gerber_to_tracks", "assign_nets", "pours_to_zones", "check_board"):
        sys.exit(f"pcb_wrap: unknown tool {tool}")
    pcb.configure(records=d1_records)
    patch_gerber()
    patch_gerber_to_tracks()
    patch_assign_nets()
    patch_export_netlist()
    if tool == "check_board":
        patch_check_board()
    sys.argv = [f"p2k.{tool}"] + sys.argv[2:]
    importlib.import_module(f"p2k.{tool}").main()   # the patched modules (not a fresh __main__ copy)


if __name__ == "__main__":
    main()
