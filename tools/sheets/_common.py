"""Helpers for the per-sheet transcription scripts (tools/sheets/sheetNN.py).

The generic helpers come from p2k.sheetkit (grid g(), sheet(), left/right/up/down,
glabel_*/label_*, power_at, bus_group, flagged_power, vert2, horiz2); board helpers below
(part-map lookups, term(), place_mirrored(), P(); the last three are the workarounds of
tube_power_amp_kicad, STATUS.md "p2k candidates"). Each sheet script starts with
    from _common import *  # noqa: F401,F403
Add repeated blocks of this board here (JFET driver cell of pages 9 / 12, level shifter, ...).
"""
import csv
import os
import sys

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(TOOLS, "p2k"))  # proteus2kicad
from p2k.sch_builder import Sheet  # noqa: E402,F401
from p2k.sheetkit import *  # noqa: E402,F401,F403
from p2k.sheetkit import _two_pin_rot  # noqa: E402

_PART_MAP = None


def part(ref):
    """Row of lib/part_map.csv for a KiCad refdes (keys refdes, sheet, lib_id, value, ...)."""
    global _PART_MAP
    if _PART_MAP is None:
        with open(os.path.join(os.path.dirname(TOOLS), "lib", "part_map.csv"), newline="", encoding="utf-8") as f:
            _PART_MAP = {r["refdes"]: r for r in csv.DictReader(l for l in f if not l.startswith("#"))}
    return _PART_MAP[ref]


def sh_value(ref):
    """Value of a refdes from lib/part_map.csv."""
    return part(ref)["value"]


def sym(ref):
    """Symbol name (lib_id without the library nickname) of a refdes from lib/part_map.csv."""
    return part(ref)["lib_id"].partition(":")[2]


def term(sh, ref, x, y, direction="up"):
    """Proteus TERMINAL part as sheetkit.terminal does it (connection point (x, y), circle
    pointing in `direction`, texts horizontal), but with the symbol and value of the part map
    (symbol TERMINAL, value TERMINAL). sheetkit.terminal always places PIN / "PIN"."""
    rot = {"up": 0, "left": 90, "down": 180, "right": 270}[direction]
    kw = {}
    if direction == "right":     # KiCad mirrors justification for rot 270
        kw = dict(ref_at=(x + 5.08, y - 1.27, 90, "left"), value_at=(x + 5.08, y + 1.27, 90, "left"))
    elif direction == "left":
        kw = dict(ref_at=(x - 5.08, y - 1.27, 270, "right"), value_at=(x - 5.08, y + 1.27, 270, "right"))
    return sh.place(sym(ref), ref, x, y, rot, value=sh_value(ref), **kw)


# --- PDF coordinates ---------------------------------------------------------------------------------
# The Proteus PDF pages rendered at 200 dpi (build/tmp/pdf/hi-N.png) have 0.127 mm pixels, so
# 10 px = one 1.27 mm grid unit. P(px/10, py/10) puts a point of the render on the A3 KiCad sheet
# (same scale, shifted by OX/OY grid units), which keeps the layout close to the PDF.
OX, OY = 40, 30


def P(x, y):
    """Sheet point (mm, on the 1.27 mm grid) of PDF render position (x, y) in units of 10 px."""
    return (g(x + OX), g(y + OY))


# --- mirrored symbols --------------------------------------------------------------------------------
def place_mirrored(sh, name, ref, x, y, axis="x", **kw):
    """sh.place() at rotation 0 with the symbol mirrored: axis 'x' = about the X axis (top and
    bottom swapped), 'y' = about the Y axis (left and right swapped). p2k.sch_builder.Sheet.place has
    no mirror option (p2k candidate), so the node it wrote gets a (mirror ...) entry here and the
    returned pin points are mirrored about the symbol origin. Pass ref_at / value_at for the texts
    (KiCad keeps field positions absolute)."""
    from p2k.sexpr import Sym, find
    p = sh.place(name, ref, x, y, 0, **kw)
    unit = kw.get("unit", 1)
    for node in sh.tree:
        if (isinstance(node, list) and node and str(node[0]) == "symbol" and find(node, "unit")[1] == unit
                and any(c[1:3] == ["Reference", ref] for c in node if isinstance(c, list) and str(c[0]) == "property")):
            node.insert(next(i for i, c in enumerate(node) if isinstance(c, list) and str(c[0]) == "at") + 1,
                        [Sym("mirror"), Sym(axis)])
            break
    else:
        raise KeyError(ref)
    for num, (px, py) in list(p.pins.items()):
        p.pins[num] = (px, round(2 * y - py, 4)) if axis == "x" else (round(2 * x - px, 4), py)
    return p


# --- IPC nets ----------------------------------------------------------------------------------------
# The sheet scripts take every net name from the IPC netlist (reference/ipc356_pads.json, after the
# D1 merges of p2k_config.SPLIT_PIN_MERGES), never from the PDF label: tie() / pin_tie() look up the
# pin and attach what the transcription rules ask for (power symbol, global or local label,
# no-connect flag), two() orients a two-pin part by the net of its top / left pin.
import json  # noqa: E402

from p2k import board  # noqa: E402
from p2k.sch_builder import lib  # noqa: E402
from p2k.sexpr import find, find_all  # noqa: E402

RAILS_GND = ("GND", "RS485_GND")
RAILS = RAILS_GND + ("1V", "1V8", "3V3", "5V", "12V", "AD_3V3", "ISO5V", "OPAMP_-15V")
NC = "N/C"
_IPC = None


def _ipc():
    """({(refdes, pin): net}, {net: set of PDF pages}); N/C pads have the net NC."""
    global _IPC
    if _IPC is None:
        merges = getattr(board.config(), "SPLIT_PIN_MERGES", {})
        rename = {merged: kept for kept, merged in merges.values()}
        pin_net = {}
        for p in json.load(open(board.path("reference", "ipc356_pads.json")))["pads"]:
            if p["kind"] != "pad":
                continue
            n = NC if p["net_raw"] == "N/C" else rename.get(p["net"], p["net"])
            k = (p["refdes"], p["pin"])
            assert pin_net.get(k, n) == n, f"{k}: pads on {pin_net[k]} and {n} (not in SPLIT_PIN_MERGES)"
            pin_net[k] = n
        ball_unit = {}                      # U10: ball -> unit number, from the library symbol
        for sub in find_all(lib()["TI60F225"], "symbol"):
            for p in find_all(sub, "pin"):
                ball_unit[find(p, "number")[1]] = int(sub[1].rsplit("_", 2)[1])
        pages = {}
        for (ref, pin), n in pin_net.items():
            row = part(ref)
            if row.get("units"):
                unit_page = dict(u.split(":") for u in row["units"].split())
                page = int(unit_page["ABCDEFGH"[ball_unit[pin] - 1]])
            else:
                page = int(row["sheet"])
            pages.setdefault(n, set()).add(page)
        _IPC = (pin_net, pages)
    return _IPC


def net(ref, pin):
    """IPC net of a pin (NC for an N/C pad)."""
    return _ipc()[0][(ref, str(pin))]


def pin_of(ref, name):
    """The one pin of `ref` on IPC net `name`."""
    pins = [p for (r, p), n in _ipc()[0].items() if r == ref and n == name]
    assert len(pins) == 1, f"{ref}: pins on {name}: {pins}"
    return pins[0]


def net_kind(name):
    """'power' (one of the 10 rails), 'wire' (auto-named #00xxx: plain wires), 'global' (named net
    with pins on several PDF pages) or 'local'."""
    pages = _ipc()[1]
    assert name in pages and name != NC, f"{name!r} is not an IPC net"
    if name in RAILS:
        return "power"
    if name.startswith("#"):
        return "wire"
    return "global" if len(pages[name]) > 1 else "local"


_STEP = {"left": left, "right": right, "up": up, "down": down}
_ANGLE = {"right": 0, "up": 90, "left": 180, "down": 270}


def tie(sh, name, p, side="right", n=2, body=None):
    """Attach IPC net `name` at point p: a stub wire of n grid units towards `side` (n = 0: none),
    then a power symbol for a rail (body down for grounds, up for supplies, or `body`), a global
    label for a net on several pages, a local label otherwise. Returns the end of the stub."""
    kind = net_kind(name)
    assert kind != "wire", f"{name}: auto-named nets are plain wires"
    q = _STEP[side](p, n) if n else p
    if n:
        sh.wire(p, q)
    if kind == "power":
        power_at(sh, name, q, body or (side if side in ("up", "down") else "down" if name in RAILS_GND else "up"))
    elif kind == "global":
        sh.glabel(name, q[0], q[1], _ANGLE[side])
    else:
        sh.label(name, q[0], q[1], _ANGLE[side])
    return q


def pin_tie(sh, placed, pin, side="right", n=2, body=None):
    """tie() for the IPC net of `pin` of a placed part; a no-connect flag for an N/C pad; nothing
    for an auto-named net (returns the pin point: draw the wires)."""
    name = net(placed.ref, pin)
    p = placed.pin(pin)
    if name == NC:
        sh.no_connect(*p)
        return p
    if net_kind(name) == "wire":
        return p
    return tie(sh, name, p, side, n, body)


def two(sh, ref, x, y, top=None, left=None, **kw):
    """Two-pin part `ref` (symbol and value from the part map) at (x, y): vertical with `top` at the
    top, or horizontal with `left` on the left; top / left = a pin number (int) or the IPC net of
    that pin. Returns (top point, bottom point) or (left point, right point)."""
    want = top if top is not None else left
    pin = want if isinstance(want, int) else int(pin_of(ref, want))
    f = vert2 if top is not None else horiz2
    _, a, b = f(sh, sym(ref), ref, x, y, sh_value(ref), **{"top" if top is not None else "left": pin}, **kw)
    return a, b


def place_pin(sh, ref, pin, pt, rot=0, unit=1, **kw):
    """Place `ref` (symbol and value from the part map) so that `pin` lands on point pt."""
    from p2k.sch_builder import _rot
    for sub in find_all(lib()[sym(ref)], "symbol"):
        for p in find_all(sub, "pin"):
            if find(p, "number")[1] == str(pin):
                at = find(p, "at")
                dx, dy = _rot(float(at[1]), float(at[2]), rot)
                return sh.place(sym(ref), ref, round(pt[0] - dx, 4), round(pt[1] + dy, 4), rot, unit=unit,
                                value=sh_value(ref), **kw)
    raise KeyError(f"{ref} pin {pin}")


def note(sh, s, x, y, size=1.27):
    """Text note at PDF render position (x, y)."""
    sh.text(s, *P(x, y), size=size)


def header(sh, ref, top_left, pt, n=8, n_power=3, skip=()):
    """Dual-row header `ref` (HEADER_2Xn_50MIL: odd pins left, pin 1 top) placed so that pin `top_left`
    is the top left pin at point pt: pin 1 = as the symbol, the last pin = rotated by 180 deg (odd pins
    right, pin 1 bottom), the last odd pin = mirrored about the X axis (odd pins left, pin 1 bottom).
    Every pin not in `skip` gets its IPC net by pin_tie(): labels n grid units out, rail symbols n_power
    units out pointing sideways, no-connect flags on N/C pads. Reference above, value below the body."""
    npins = sum(len(find_all(sub, "pin")) for sub in find_all(lib()[sym(ref)], "symbol"))
    rows = npins // 2
    if top_left == 1:
        rot, mirror = 0, False
    elif top_left == npins:
        rot, mirror = 180, False
    elif top_left == npins - 1:
        rot, mirror = 0, True
    else:
        raise ValueError(f"{ref}: top left pin {top_left}?")
    # symbol origin from the library position of the top-left pin
    for sub in find_all(lib()[sym(ref)], "symbol"):
        for p in find_all(sub, "pin"):
            if find(p, "number")[1] == str(top_left):
                at = find(p, "at")
                lx, ly = float(at[1]), float(at[2])
    if rot == 180:
        ox, oy = pt[0] + lx, pt[1] - ly
    elif mirror:
        ox, oy = pt[0] - lx, pt[1] - ly
    else:
        ox, oy = pt[0] - lx, pt[1] + ly
    ox, oy = round(ox, 4), round(oy, 4)
    xmid = round(pt[0] + g(6), 4)
    kw = dict(value=sh_value(ref), ref_at=(xmid, round(pt[1] - g(3), 4), 0, None),
              value_at=(xmid, round(pt[1] + g(2 * rows + 1), 4), 0, None))
    p = place_mirrored(sh, sym(ref), ref, ox, oy, "x", **kw) if mirror else sh.place(sym(ref), ref, ox, oy, rot, **kw)
    assert p.pin(top_left) == (round(pt[0], 4), round(pt[1], 4)), (ref, p.pin(top_left), pt)
    assert all(q[0] >= pt[0] - 1e-6 and q[1] >= pt[1] - 1e-6 for q in p.pins.values()), f"{ref}: {top_left} is not top left"
    for pin in range(1, npins + 1):
        if pin in skip:
            continue
        side = "left" if abs(p.pin(pin)[0] - pt[0]) < 1e-6 else "right"
        if net(ref, pin) in RAILS:
            pin_tie(sh, p, pin, side, n_power, body=side)
        else:
            pin_tie(sh, p, pin, side, n)
    return p
