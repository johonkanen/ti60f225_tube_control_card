#!/usr/bin/env python3
"""`p2k check_sources` with the two Gerber X2 features of this board the shared check rejects.

Board-local workaround (STATUS.md "p2k candidates"); the shared check runs unchanged on
adapted inputs:

  * BGAPad flashes: Proteus writes the 225 balls of U10 with the aperture function
    `BGAPad,CuDef`, which the shared check does not know ("flashes of unexpected function").
    They are matched as SMD pads of their side (function renamed to `SMDPad,CuDef,BGAPad`
    for the shared check), and this script checks in addition that the BGAPad flashes are
    exactly the 225 IPC pads of U10 (within 0.01 mm).
  * SMD pads without a part (SMD_FREE_PADS, test pads): `p2k ipc356` records them as
    `free_pad`, which the shared check expects as OtherPad flashes on every copper layer
    and as plated OtherDrill flashes. The shared check reads a copy of
    reference/ipc356_pads.json (build/tmp/) in which these records have the kind
    `smd_test_pad`, so they are matched with the SMDPad flashes of their side only.

  python3 tools/check_sources.py
"""
import json
import os
import sys
import types

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools", "p2k"))
os.environ.setdefault("P2K_BOARD", ROOT)

from p2k import board, check_sources, gerber  # noqa: E402

CFG = board.config()
SMD_FREE = getattr(CFG, "SMD_FREE_PADS", {})
BGA_REF = "U10"
TOL = check_sources.TOL
TMP = os.path.join(ROOT, "build", "tmp", "check_sources")


def parse_bga_as_smd(path):
    g = gerber.parse(path)
    for ap in g.apertures.values():
        if ap.function.startswith("BGAPad"):
            ap.function = "SMDPad," + ap.function.replace("BGAPad,", "") + ",BGAPad"
    return g


def main():
    with open(board.path("reference", "ipc356_pads.json")) as f:
        doc = json.load(f)
    errors = []

    # BGAPad flashes = the balls of U10
    g = gerber.parse(check_sources.path(CFG.COPPER[0][0]))
    bga = [o for o in g.objects if isinstance(o, gerber.Flash) and o.ap.function.startswith("BGAPad")]
    balls = [p for p in doc["pads"] if p["refdes"] == BGA_REF]
    left = list(balls)
    for fl in bga:
        hit = [p for p in left if abs(p["x_mm"] - fl.x) <= TOL and abs(p["y_mm"] - fl.y) <= TOL]
        if hit:
            left.remove(hit[0])
        else:
            errors.append(f"BGAPad flash at ({fl.x:.3f}, {fl.y:.3f}) is not a {BGA_REF} ball")
    for p in left:
        errors.append(f"{BGA_REF}-{p['pin']} has no BGAPad flash")

    # SMD test pads: own kind in a copy of the reference table
    n = 0
    for p in doc["pads"]:
        if p["kind"] == "free_pad" and (p["x_mm"], p["y_mm"]) in SMD_FREE and not p["is_tht"]:
            p["kind"] = "smd_test_pad"
            n += 1
    if n != len(SMD_FREE):
        errors.append(f"SMD_FREE_PADS: {n} of {len(SMD_FREE)} found as SMD free pads in the IPC table")
    os.makedirs(TMP, exist_ok=True)
    tmp_json = os.path.join(TMP, "ipc356_pads.json")
    with open(tmp_json, "w") as f:
        json.dump(doc, f)

    def path(*parts):
        return tmp_json if parts == ("reference", "ipc356_pads.json") else board.path(*parts)

    check_sources.board = types.SimpleNamespace(path=path)
    check_sources.gerber = types.SimpleNamespace(parse=parse_bga_as_smd, Flash=gerber.Flash)
    rc = check_sources.main()

    print(f"  board-local: {len(bga)} BGAPad flashes = {len(balls)} {BGA_REF} balls; "
          f"{n} SMD test pads matched as SMD pads only")
    for e in errors:
        print("  FAIL " + e)
    ok = rc == 0 and not errors
    print("check_sources (board wrapper): " + ("OK" if ok else "FAIL"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
