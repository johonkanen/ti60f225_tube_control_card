#!/usr/bin/env python3
"""Pin-order check: the UNMOVED KiCad base footprints with the Proteus renumbering, fitted onto
the IPC pads (playbook Phase 2, step 2). A small residual confirms that the Proteus pin ids sit on
the pads the renumbering says; a residual of a pad pitch or more means the ids are on other pads
(chirality). Both mirror states are fitted: SMD parts must fit with the mirror of their IPC side
(bottom = mirrored), THT parts the mirror of their side on the Proteus assembly layers
(all on top except J3). Board-local, after tube_hv_supplies' tools/check_pin_order.py (p2k
candidate 20); U10 also checks the fitted angle (180 deg).

Limits of the geometry: two-pad and inline parts always fit (a 180 deg turn reverses the pad
order), and dual-row SMD packages are symmetric under a 180 deg turn, so the geometry confirms the
chirality but not which end is pin 1. For those the nets decide (Phase 1: every pin on its IPC net,
e.g. ADC1 A2 = GND, K1 = SCL, COM1 = SDA only with A1 on JEDEC pad 1), and the body markers are
drawn with --render over the Proteus silk / assembly layers of the part's side
(reports/pin_order/<refdes>.png) and compared by eye (STATUS.md "Phase 2 - pin order").

Usage: python3 tools/check_pin_order.py [--render]   (--render needs matplotlib)
Exit 1 when a result differs from CHECKS (so a changed footprint or renumbering is noticed).
"""
import glob
import math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools", "p2k"))
os.chdir(ROOT)
from p2k import fpgeom, sexpr  # noqa: E402
from p2k.footprints import footprint_path  # noqa: E402
sys.path.insert(0, os.path.join(ROOT, "tools"))
from gen_footprints import PROJECT, RULES  # noqa: E402

# Every footprint is taken from gen_footprints.RULES (rule()): library footprints as they are,
# project footprints with THEIR base and renumbering (gen_footprints.PROJECT), so a wrong
# renumbering there fails here even though p2k.footprints.derive moves the pads onto the IPC
# positions (and check_footprints then passes). Footprints built from the IPC pads only (blade
# terminals, IZB03, X2QFN-8 AD2) have no base to check; their pin order is the IPC's by
# construction (STATUS.md "Phase 2 - pin order").



def proj(name):
    """(base footprint, renumbering) of a project footprint spec."""
    return PROJECT[name]["base"], PROJECT[name].get("renumber", {})


def rule(symbol):
    """(KiCad footprint, renumbering) that gen_footprints.RULES assigns to a symbol (single rule):
    a library footprint as it is, a project footprint as its base + renumbering."""
    fps = [r[2] for r in RULES if r[0] == symbol]
    assert len(fps) == 1, (symbol, fps)
    nick, name = fps[0].split(":", 1)
    return proj(name) if nick == "tube_control_card" else (fps[0], {})


# (name, refdes group, KiCad base footprint, renumbering of the base pads, expected best mirror,
#  residual upper bound mm, note[, expected angle deg])
CHECKS = [
    ("U10 BGA", "U10", *rule("TI60F225"), False, 0.001,
     "ball ids = KiCad pad names, A1-top-left footprint at 180 deg", 180.0),
    ("ADC1", "ADC1", *rule("ADC121C027"), False, 0.19,
     "A1 A2 COM2 K2 K1 COM1 = JEDEC 1-6: fits (rows 2.65 vs KiCad 2.275 -> 0.1875)"),
    ("ADC1 datasheet", "ADC1", "Package_TO_SOT_SMD:SOT-23-6",
     {"1": "COM2", "2": "A2", "3": "A1", "4": "COM1", "5": "K1", "6": "K2"}, None, None,
     "VA / VIN exchanged (COM2 on pad 1, A1 on pad 3, the datasheet wiring): fits only mirrored, "
     "i.e. not on a top-side part"),
    ("SOT-23-5", "U4 V4", *rule("TLV316IDBVR"), True, 0.07, "bottom side, rows 2.39 vs 2.30"),
    ("SC-70-6", "U12", *rule("AD5622"), False, 0.07, "rows 1.80 vs 1.675"),
    ("SOT-563", "PWR1 PWR2 PWR3", *rule("AP61202"), True, 0.08, "bottom side, rows 1.27 vs 1.425"),
    ("TSSOP-14", "U5 U6 U11 U14", *rule("TLV9304PWR"), False, 0.07, "rows 5.85 vs 5.725"),
    ("TSSOP-24", "U1 U2 U7 U8 U9", *rule("SN74AXC8T245"), False, 0.02, "KiCad footprint unchanged"),
    ("TSSOP-16", "U3", *rule("SN74LV4051"), True, 0.02, "bottom side, KiCad footprint unchanged"),
    ("R array", "R14 R15 R17 R18 R22 R23 R24 R25", *rule("R_ARRAY4"), False, 0.06,
     "rows 0.95 vs 1.0"),
    ("OSC1", "OSC1", *rule("MC2016K_OSC"), False, 0.16, "pads 1.8 x 1.2 vs KiCad 1.5 x 1.1"),
    ("SO8W RS1", "RS1", *rule("MAX22025"), False, 0.76, "rows 9.14 vs KiCad 10.65"),
    ("SO8W FLASH1", "FLASH1", *rule("W25Q64JWSSIQ"), False, 0.99, "rows 9.14 vs KiCad 7.175"),
    ("J11 rows swapped", "J11", *rule("HEADER_2X20_50MIL"), False, 0.01,
     "odd / even swapped: fits on top"),
    ("J11 KiCad", "J11", "Connector_PinHeader_1.27mm:PinHeader_2x20_P1.27mm_Vertical", {}, True, 0.01,
     "standard numbering fits only MIRRORED (bottom), but J11 is on top (as tube_hv_supplies J1)"),
    ("J3", "J3", *rule("HEADER_2X8_50MIL"), True, 0.01,
     "standard numbering, fits mirrored: J3 is a bottom-side part (Proteus bottom assembly)"),
    ("J6", "J6", *rule("HEADER_2X8_50MIL"), False, 0.01,
     "standard numbering fits on top"),
    ("J7", "J7", *rule("HEADER_2X15_50MIL"), False, 0.01,
     "standard numbering fits on top"),
    ("J1", "J1", *rule("TBLOCK-I5"), False, 0.01,
     "inline: body side by render"),
    ("J8", "J8", *rule("CONN_01X03"), False, 0.01, "inline"),
]
RENDER = "U10 ADC1 PWR2 U4 V4 U12 U5 U1 U3 R14 OSC1 RS1 FLASH1 J11 J3 J6 J7 J1 J8".split()


# parts sharing a footprint with a checked symbol
assert rule("TL084HIDYYR") == rule("TLV9304PWR") and rule("TPS73030") == rule("TLV316IDBVR")


def base_pads(fpid, ren):
    out = []
    for p in fpgeom.load_footprint(footprint_path(fpid)):
        if p["num"] == "":
            continue
        q = dict(p)
        q["num"] = ren.get(p["num"], p["num"])
        out.append(q)
    return out


def graphics(fpid):
    """F.SilkS / F.Fab polylines of a footprint (footprint frame, Y up)."""
    node = sexpr.load(footprint_path(fpid))
    lines = []

    def xy(n):
        return float(n[1]), -float(n[2])
    for g in node:
        if not isinstance(g, list) or not g or str(g[0]) not in ("fp_line", "fp_rect", "fp_circle", "fp_poly"):
            continue
        layer = sexpr.find(g, "layer")
        if layer is None or layer[1] not in ("F.SilkS", "F.Fab"):
            continue
        kind = str(g[0])
        if kind == "fp_line":
            lines.append([xy(sexpr.find(g, "start")), xy(sexpr.find(g, "end"))])
        elif kind == "fp_rect":
            (x0, y0), (x1, y1) = xy(sexpr.find(g, "start")), xy(sexpr.find(g, "end"))
            lines.append([(x0, y0), (x1, y0), (x1, y1), (x0, y1), (x0, y0)])
        elif kind == "fp_circle":
            (cx, cy), (ex, ey) = xy(sexpr.find(g, "center")), xy(sexpr.find(g, "end"))
            r = math.hypot(ex - cx, ey - cy)
            lines.append([(cx + r * math.cos(t / 20 * math.pi), cy + r * math.sin(t / 20 * math.pi)) for t in range(41)])
        else:
            pts = [xy(p) for p in sexpr.find(g, "pts")[1:]]
            lines.append(pts + pts[:1])
    return lines


def to_board(fr, x, y):
    a = math.radians(fr["angle"])
    x = -x if fr["mirror"] else x
    return fr["tx"] + math.cos(a) * x - math.sin(a) * y, fr["ty"] + math.sin(a) * x + math.cos(a) * y


def render(ref, fpid, fr, ipc_pads, out):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Circle
    from p2k import gerber
    side = "Bottom" if fr["mirror"] else "Top"
    xs = [p["x_mm"] for p in ipc_pads]
    ys = [p["y_mm"] for p in ipc_pads]
    m = 4
    box = (min(xs) - m, max(xs) + m, min(ys) - m, max(ys) + m)
    fig, axs = plt.subplots(1, 2, figsize=(11, 5.5))
    for ax, layer in zip(axs, (f"{side} Silk Screen", f"{side} Assembly")):
        g = gerber.parse(glob.glob(f"source/cadcam/*{layer}.GBR")[0])
        for d in g.of(gerber.Draw):
            if box[0] <= d.x1 <= box[1] and box[2] <= d.y1 <= box[3]:
                ax.plot([d.x1, d.x2], [d.y1, d.y2], color="k", lw=1.0)
        for p in ipc_pads:
            ax.add_patch(Circle((p["x_mm"], p["y_mm"]), min(p["pad_w"], p["pad_h"]) / 2, color="orange", alpha=0.5))
            ax.text(p["x_mm"], p["y_mm"], p["pin"], ha="center", va="center", fontsize=7, color="b")
        for line in graphics(fpid):
            pts = [to_board(fr, x, y) for x, y in line]
            ax.plot([p[0] for p in pts], [p[1] for p in pts], color="r", lw=0.8)
        ax.set_title(f"{ref} {layer}: black = Proteus, orange = IPC pads (ids)\nred = unmoved "
                     f"{fpid.split(':')[1]} ({'mirrored, ' if fr['mirror'] else ''}{fr['angle']:g} deg, "
                     f"res {fr['max_res']:.3f})", fontsize=7)
        ax.set_aspect("equal")
        ax.set_xlim(box[0], box[1])
        ax.set_ylim(box[2], box[3])
    fig.savefig(out, dpi=110, bbox_inches="tight")
    plt.close(fig)


def main():
    do_render = "--render" in sys.argv[1:]
    ipc = fpgeom.ipc_pads_by_refdes()
    bad = []
    print(f"{'check':16s} {'KiCad base (unmoved)':40s} {'unmirrored':>16s} {'mirrored':>16s}  result")
    rendered = set()
    for name, refs, fpid, ren, want_mir, lim, note, *opt in CHECKS:
        want_ang = opt[0] if opt else None
        fp = base_pads(fpid, ren)
        worst = {False: None, True: None}
        for ref in refs.split():
            for mir in (False, True):
                r = fpgeom.fit(fp, ipc[ref], mir)
                if r["missing"] or r["extra"] or r["count_diff"]:
                    bad.append(f"{name} {ref}: pad numbers differ from {fpid}: {r['missing']} {r['extra']} {r['count_diff']}")
                if worst[mir] is None or r["max_res"] > worst[mir]["max_res"]:
                    worst[mir] = r
            if do_render and ref in RENDER and ref not in rendered and want_mir is not None:
                rendered.add(ref)
                os.makedirs("reports/pin_order", exist_ok=True)
                render(ref, fpid, fpgeom.fit(fp, ipc[ref], want_mir), ipc[ref], f"reports/pin_order/{ref}.png")
        u, m = worst[False], worst[True]
        cell = lambda w: f"{w['max_res']:7.3f} @{w['angle']:6.4g}"  # noqa: E731
        if want_mir is None:
            # a "does not fit" check: the unmirrored (top) fit must fail
            ok = u["max_res"] > 0.1
            result = "no fit on its side" if ok else "FITS (unexpected)"
        else:
            # symmetric patterns (two-pad, inline) fit both ways: take the mirror of the part's side
            tie = abs(m["max_res"] - u["max_res"]) < 1e-3
            best_mir = want_mir if tie else m["max_res"] < u["max_res"]
            res = m["max_res"] if best_mir else u["max_res"]
            ok = best_mir == want_mir and res <= lim
            result = f"{'mirrored' if best_mir else 'unmirrored'} {res:.3f}"
            if want_ang is not None:
                ang = (m if best_mir else u)["angle"]
                ok = ok and abs((ang - want_ang + 180) % 360 - 180) < 0.01
                result += f" @{ang:g} deg"
        print(f"{name:16s} {fpid.split(':')[1]:40s} {cell(u):>16s} {cell(m):>16s}  {result}  ({note})")
        if not ok:
            bad.append(f"{name}: {result}, expected "
                       + ("no unmirrored fit" if want_mir is None else
                          f"{'mirrored' if want_mir else 'unmirrored'} <= {lim}")
                       + ("" if want_ang is None else f" @{want_ang:g} deg"))
    for b in bad:
        print("check_pin_order: ERROR " + b)
    print("check_pin_order: " + ("FAILED" if bad else "OK (results as recorded in STATUS.md)"))
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
