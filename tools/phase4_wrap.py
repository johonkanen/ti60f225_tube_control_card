#!/usr/bin/env python3
"""Phase 4: `p2k ipc356_diff` and `p2k gerber_roundtrip` with this board's accepted differences
(board-local, STATUS.md "p2k candidates"; tools/p2k unchanged; system python3).

  python3 tools/phase4_wrap.py ipc356_diff [--kicad FILE] [-v]
  python3 tools/phase4_wrap.py gerber_roundtrip [--check] [--kicad-dir DIR] [--keep]

ipc356_diff. The shared tool runs UNCHANGED on the unfiltered Proteus records (no record filter, unlike
tools/pcb_wrap.py: this is the independent Phase 4 check). Its result is then judged here:

  D1 (decision D1, SPLIT_PIN_MERGES): KiCad has both pads of J2, ISO5V, ISO_G, RS485A, RS485B on one
     net, Proteus on two, so the shared tool reports exactly one error per terminal,
     "KiCad net K spans Proteus nets [kept, merged]". Accepted when the reported errors are exactly
     these five, each naming exactly the (kept, merged) pair of SPLIT_PIN_MERGES; anything else (a
     sixth merge, a split, a wrong net, a missing D1 error = the merge is not on the board) fails.
     Checked in addition on the KiCad export itself: both pad records of every D1 pin are on one
     KiCad net, and every Proteus pad of the kept and of the merged net (e.g. R67-1 on RS485B's
     second net) is on that same KiCad net.
  SMD test pads (SMD_FREE_PADS): the shared tool matches the Proteus free_pad records (327, SMD)
     with KiCad's records of the board-only footprints TP<n> (position, SMD, side, net). Checked in
     addition: the export has exactly len(SMD_FREE_PADS) TP records, each a 327 record without
     drill on the top side at a listed position.
  BGA: KiCad writes the U10 balls as ordinary 327 records; required: one per Proteus U10 record.
  N/C: the shared tool accepts a Proteus N/C pad on any KiCad `unconnected-(...)` net, so two N/C
     pads joined to each other on the board (one such net with two pads) would pass. Required here:
     every `unconnected-(...)` net of the export has exactly one record.
  Counts: the summary line must be the recorded one (EXPECT below).

gerber_roundtrip. `BGAPad` is added to the shared PAD_FUNCTIONS (p2k candidate 3): without it the
225 Proteus U10 ball flashes do not count as pads, the whole of every KiCad ball then lies in the
"pad shape" mask (pad XOR) and any copper difference at a ball would be explained away. The SMD test
pads need nothing (SMDPad flashes on both sides). In practice the result is the same with and without it
(STATUS.md "Phase 4").
Counts: the round trip compares copper areas, so a short track that lies (almost) inside two pads - a
0.43 mm dog-bone stub between a U10 ball and its via - can be missing without any difference (negative
test `dogbone`; the copper check of Phase 3 finds the open). Required here in addition, from the
"coverage:" lines of the report: per layer the recorded number of KiCad track draws (RT_DRAWS = the
Proteus Conductor draws that became tracks) and as many KiCad pad / via flashes as Proteus flashes.
"""
import ast
import contextlib
import io
import math
import os
import re
import sys
import tempfile
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools", "p2k"))
os.environ.setdefault("P2K_BOARD", ROOT)

from p2k import board  # noqa: E402

CFG = board.config()
MERGES = CFG.SPLIT_PIN_MERGES
SMD_FREE = CFG.SMD_FREE_PADS
BGA_REF = "U10"
# recorded result of the shared tool (STATUS.md "Phase 4")
EXPECT = dict(proteus=1132, kicad=1132, matched=1132, pads=884, nc=76, vias=240, holes=4, free=4, nets=227)
# KiCad track draws per layer (= gerber_to_tracks: 3373 tracks, F 2152 / In1 72 / In2 221 / B 928)
RT_DRAWS = {"F.Cu": 2152, "In1.Cu": 72, "In2.Cu": 221, "B.Cu": 928}
COVER = re.compile(r"coverage: Proteus (\d+) draws / (\d+) flashes, .*; KiCad (\d+) draws / (\d+) flashes")
SUMMARY = re.compile(r"ipc356_diff: Proteus (\d+) records, KiCad (\d+); matched (\d+) \((\d+) pads incl\. (\d+) N/C, "
                     r"(\d+) vias, (\d+) holes, (\d+) free pads\)")
SPANS = re.compile(r"ipc356_diff: ERROR KiCad net (.+) spans Proteus nets (\[.*\])$")


def ipc356_diff(argv):
    from p2k import ipc356_diff as d
    from p2k import pcb
    if "--kicad" in argv:
        kpath, tmp = argv[argv.index("--kicad") + 1], None
    else:
        tmp = tempfile.TemporaryDirectory()
        kpath = os.path.join(tmp.name, f"{CFG.PROJECT}.d356")
        d.export(kpath)
        argv = argv + ["--kicad", kpath]
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = d.main(argv)
    lines = buf.getvalue().splitlines()
    errors = []      # board-local judgement
    shared_errors = [ln for ln in lines if ln.startswith("ipc356_diff: ERROR") or ln.startswith("ipc356_diff: ...")]
    want = {frozenset(v): k for k, v in MERGES.items()}
    seen = {}
    for ln in shared_errors:
        m = SPANS.match(ln)
        pair = frozenset(ast.literal_eval(m[2])) if m else None
        if m and pair in want and pair not in seen:
            seen[pair] = m[1]
        else:
            errors.append("not accepted: " + ln[len("ipc356_diff: "):])
    for pair in want:
        if pair not in seen:
            errors.append(f"D1: no merge reported for {want[pair][0]}-{want[pair][1]} {sorted(pair)}: "
                          "the board does not join these two Proteus nets")

    # the KiCad export itself
    kic = d.parse_kicad(kpath, len(CFG.COPPER), getattr(CFG, "FREE_PAD_PREFIX", "FP"))
    prot = pcb.ipc_records()      # unfiltered
    by_pin = defaultdict(list)
    for r in kic:
        if r["kind"] == "pad":
            by_pin[(r["refdes"], r["pin"])].append(r)
    for (ref, pin), (kept, merged) in sorted(MERGES.items()):
        knets = {r["net"] for r in by_pin[(ref, pin)]}
        if len(by_pin[(ref, pin)]) != 2 or len(knets) != 1:
            errors.append(f"D1: {ref}-{pin}: {len(by_pin[(ref, pin)])} KiCad pad records on nets {sorted(knets)} (want 2 on one net)")
            continue
        k = next(iter(knets))
        if seen.get(frozenset((kept, merged)), k) != k:
            errors.append(f"D1: {ref}-{pin} is on KiCad net {k}, the merge was reported for {seen[frozenset((kept, merged))]}")
        for p in prot:
            if p["kind"] == "pad" and p["net"] in (kept, merged):
                near = [r for r in by_pin[(p["refdes"][:6], p["pin"])]
                        if math.hypot(r["x_mm"] - p["x_mm"], r["y_mm"] - p["y_mm"]) < d.TOL]
                if len(near) != 1 or near[0]["net"] != k:
                    errors.append(f"D1: {p['refdes']}-{p['pin']} (Proteus {p['net']}): KiCad "
                                  f"{[r['net'] for r in near]}, want {k}")
    tps = [r for r in kic if r["kind"] == "free_pad"]
    for r in tps:
        at = [xy for xy in SMD_FREE if math.hypot(xy[0] - r["x_mm"], xy[1] - r["y_mm"]) < d.TOL]
        if r["is_tht"] or r["drill"] or r["side"] != "top" or len(at) != 1:
            errors.append(f"test pad {r['refdes']} at ({r['x_mm']:.3f}, {r['y_mm']:.3f}): THT {r['is_tht']}, drill "
                          f"{r['drill']}, side {r['side']}, {len(at)} SMD_FREE_PADS positions (want SMD, no drill, top, 1)")
    if len(tps) != len(SMD_FREE):
        errors.append(f"{len(tps)} KiCad test pad records, SMD_FREE_PADS has {len(SMD_FREE)}")
    kb = [r for r in kic if r["refdes"] == BGA_REF]
    pb = [p for p in prot if p["refdes"] == BGA_REF]
    if len(kb) != len(pb) or any(r["is_tht"] or r["side"] != "top" for r in kb) \
            or {r["pin"] for r in kb} != {p["pin"] for p in pb}:
        errors.append(f"{BGA_REF}: {len(kb)} KiCad records, Proteus {len(pb)}; all must be top SMD with the same ball ids")
    unc = defaultdict(list)
    for r in kic:
        if r["net"].startswith("unconnected-("):
            unc[r["net"]].append(f"{r['refdes']}-{r['pin']}")
    for net, pads in sorted(unc.items()):
        if len(pads) != 1:
            errors.append(f"KiCad net {net} joins {len(pads)} pads ({' '.join(pads)}): N/C pads wired together")
    got = None
    for ln in lines:
        m = SUMMARY.match(ln)
        if m:
            got = dict(zip(("proteus", "kicad", "matched", "pads", "nc", "vias", "holes", "free"), map(int, m.groups())))
        m = re.match(r"ipc356_diff: (\d+) Proteus nets mapped 1:1", ln)
        if m and got is not None:
            got["nets"] = int(m[1])
    if got != EXPECT:
        errors.append(f"summary {got} != recorded {EXPECT}")

    for ln in lines:
        m = SPANS.match(ln)
        if ln in ("ipc356_diff: OK", "ipc356_diff: FAILED"):
            continue
        if m and seen.get(frozenset(ast.literal_eval(m[2]))) == m[1] and not any(ln[len("ipc356_diff: "):] in e for e in errors):
            print("ipc356_diff: accepted (D1, board-local): " + ln[len("ipc356_diff: ERROR "):])
        else:
            print(ln)
    print(f"ipc356_diff (board-local): {len(seen)} of {len(MERGES)} D1 merges reported and accepted, both pads of each "
          f"terminal and every pad of its two Proteus nets on one KiCad net; {len(tps)} SMD test pads "
          f"(327, top, no drill); {len(kb)} {BGA_REF} balls; {len(unc)} unconnected-(...) nets, one pad each")
    for e in errors:
        print("ipc356_diff (board-local): ERROR " + e)
    print("ipc356_diff: " + ("OK" if not errors else "FAILED") + f" (shared tool alone: {'OK' if rc == 0 else 'FAILED'})")
    return 1 if errors else 0


def gerber_roundtrip(argv):
    from p2k import gerber_roundtrip as rt
    assert "BGAPad" not in rt.PAD_FUNCTIONS, "p2k knows BGAPad now: remove this wrapper"
    rt.PAD_FUNCTIONS = rt.PAD_FUNCTIONS + ("BGAPad",)
    print("roundtrip (board-local): BGAPad flashes count as pads (PAD_FUNCTIONS)")
    try:
        rc = rt.main(argv) or 0
    except SystemExit as e:      # the shared main() ends with sys.exit
        rc = e.code or 0
        if not isinstance(rc, int):
            raise
    errors, layer, seen = [], None, {}
    for ln in open(os.path.join(rt.S.out, "roundtrip.txt")):
        m = re.match(r"== (\S+): Proteus copper", ln)
        if m:
            layer = m[1]
        m = COVER.search(ln)
        if m and layer:
            pd, pf, kd, kf = map(int, m.groups())
            seen[layer] = (kd, kf)
            if kd != RT_DRAWS.get(layer):
                errors.append(f"{layer}: {kd} KiCad track draws, recorded {RT_DRAWS.get(layer)}")
            if kf != pf:
                errors.append(f"{layer}: {kf} KiCad flashes, Proteus {pf}")
    if set(seen) != set(RT_DRAWS):
        errors.append(f"layers in the report {sorted(seen)} != {sorted(RT_DRAWS)}")
    for e in errors:
        print("roundtrip (board-local): ERROR " + e)
    print("roundtrip (board-local): KiCad track draws / flashes per layer "
          + ", ".join(f"{k} {seen[k][0]} / {seen[k][1]}" for k in RT_DRAWS if k in seen)
          + (": as recorded, flashes = Proteus" if not errors else ": FAILED"))
    return 1 if errors else rc


def main():
    tools = {"ipc356_diff": ipc356_diff, "gerber_roundtrip": gerber_roundtrip}
    if len(sys.argv) < 2 or sys.argv[1] not in tools:
        sys.exit(__doc__)
    return tools[sys.argv[1]](sys.argv[2:])


if __name__ == "__main__":
    sys.exit(main())
