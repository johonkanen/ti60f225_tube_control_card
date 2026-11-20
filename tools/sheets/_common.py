"""Helpers for the per-sheet transcription scripts (tools/sheets/sheetNN.py).

The generic helpers come from p2k.sheetkit (grid g(), sheet(), left/right/up/down,
glabel_*/label_*, power_at, bus_group, flagged_power, vert2, horiz2); board helpers below
(part-map lookups, term(), place_mirrored(), P(); the last three are the workarounds of
tube_power_amp_kicad, STATUS.md "p2k candidates"). Each sheet script starts with
    from _common import *  # noqa: F401,F403
Repeated blocks of this board are at the end (jfet_quad() / jfet_cell() of pages 9 and 12,
level_shifter() of page 4).
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


# --- repeated blocks ---------------------------------------------------------------------------------
def unit_of(ref, pin):
    """Unit number (1 = A) of `pin` in the library symbol of `ref`."""
    for sub in find_all(lib()[sym(ref)], "symbol"):
        if any(find(p, "number")[1] == str(pin) for p in find_all(sub, "pin")):
            return int(sub[1].rsplit("_", 2)[1])
    raise KeyError(f"{ref} pin {pin}")


def unit_pins(ref, unit):
    """{pin name: pin number} of one unit of the library symbol of `ref` ('' = the unnamed op-amp output)."""
    return {find(p, "name")[1]: find(p, "number")[1]
            for sub in find_all(lib()[sym(ref)], "symbol") if int(sub[1].rsplit("_", 2)[1]) == unit
            for p in find_all(sub, "pin")}


def array_r(sh, ref, x, y, left=None, right=None):
    """One resistor of the array `ref` (R_ARRAY4, units A-D = pins 1-8, 2-7, 3-6, 4-5), horizontal at
    (x, y): the unit that has a pin on the IPC net `left` (or `right`), that pin on that side. Returns
    (left point, right point, unit, net of the other pin)."""
    pin = int(pin_of(ref, left if left is not None else right))
    unit = unit_of(ref, pin)
    other = next(int(n) for n in unit_pins(ref, unit).values() if int(n) != pin)
    assert {pin, other} == {unit, 9 - unit}, (ref, pin, other)
    a, b = two(sh, ref, x, y, left=pin if left is not None else other, unit=unit)
    return a, b, unit, net(ref, other)


def jfet_cell(sh, amp, unit, x, y, r_in, r_fb):
    """JFET driver cell of pages 9 and 12: inverting amplifier with unit `unit` (1-4) of the quad
    op-amp `amp`, its + input at PDF position (x, y) on GND, the input resistor (a unit of the array
    r_in) from the input label to the - input, the feedback resistor (a unit of r_fb) from the - input
    to the output, the output label above. The array units and every net come from the IPC pins of the
    op-amp unit; returns (input net, output net, r_in unit, r_fb unit)."""
    Q = lambda dx, dy: P(x + dx, y + dy)
    pins = unit_pins(amp, unit)
    u = place_pin(sh, amp, pins["+"], Q(0, 0), unit=unit)
    assert u.pin(pins["-"]) == Q(0, 4) and u.pin(pins[""]) == Q(12, 2), u.pins
    inv, out = net(amp, pins["-"]), net(amp, pins[""])
    assert net_kind(inv) == "wire", inv
    pin_tie(sh, u, pins["+"], "left", 3, body="left")
    # input resistor: label - R - inverting node
    a, b, ui, n_in = array_r(sh, r_in, *Q(-12, 4), right=inv)
    sh.wire(a, Q(-21, 4), Q(-21, -7))
    tie(sh, n_in, Q(-21, -7), "up", 0)
    sh.wire(b, Q(-5, 4))
    sh.wire(Q(-5, 4), u.pin(pins["-"]))
    sh.junction(*Q(-5, 4))
    # feedback resistor: inverting node - R - output
    c, d, uf, n_out = array_r(sh, r_fb, *Q(5, 18), left=inv)
    assert n_out == out, (amp, unit, r_fb, n_out, out)
    sh.wire(Q(-5, 4), Q(-5, 18), c)
    sh.wire(d, Q(17, 18), Q(17, 2))
    sh.wire(u.pin(pins[""]), Q(17, 2))
    sh.junction(*Q(17, 2))
    sh.wire(Q(17, 2), Q(17, -9))
    tie(sh, out, Q(17, -9), "up", 0)
    return n_in, out, ui, uf


def jfet_quad(sh, amp, r_in, r_fb, at):
    """The four driver cells of one quad op-amp (units A-D with their + inputs at the PDF positions
    `at`) and its power unit E, laid over unit A as in the PDF (V+ and V- taken from the IPC pins 4 and
    11). Every unit of both resistor arrays must be used once. Returns [(input net, output net)] A-D."""
    cells = [jfet_cell(sh, amp, k + 1, x, y, r_in, r_fb) for k, (x, y) in enumerate(at)]
    assert sorted(c[2] for c in cells) == [1, 2, 3, 4] and sorted(c[3] for c in cells) == [1, 2, 3, 4], cells
    x, y = at[0]
    e = sh.place(sym(amp), amp, *P(x + 6, y + 2), unit=5, value=sh_value(amp),
                 ref_at=(*P(x + 9, y - 6), 0, None), value_at=(*P(x + 9, y + 10), 0, None))
    vp, vn = unit_pins(amp, 5)["V+"], unit_pins(amp, 5)["V-"]
    assert e.pin(vp) == P(x + 4, y - 4) and e.pin(vn) == P(x + 4, y + 8), e.pins
    pin_tie(sh, e, vp, "up", 5)
    sh.wire(e.pin(vn), P(x + 4, y + 12), P(x - 9, y + 12))     # crosses the feedback wire (no junction)
    tie(sh, net(amp, vn), P(x - 9, y + 12), "left", 3, body="left")
    return [c[:2] for c in cells]


def level_shifter(sh, ref, x, y, c_a, c_b):
    """SN74AXC8T245 block of page 4 with its A1 pin (3) at PDF position (x, y): VCCA (pin 1) with DIR1
    on the A-side supply line (left, capacitor c_a to the ground line of DIR2), VCCB (pins 24, 23) on
    the B-side supply line (right, capacitor c_b to the ground line of ~OE), the two GND pins below,
    A1-A8 labels left and B1-B8 labels right. Every net comes from the IPC pins; the block asserts the
    strapping it draws (DIR1 = VCCA net, DIR2 = ~OE = GND)."""
    Q = lambda dx, dy: P(x + dx, y + dy)
    u = place_pin(sh, ref, 3, Q(0, 0), ref_at=(*Q(12, -17), 0, "left"), value_at=(*Q(12, 27), 0, "left"))
    assert (u.pin(2), u.pin(11), u.pin(23), u.pin(22)) == (Q(0, -6), Q(0, -4), Q(16, -6), Q(16, -4)), u.pins
    assert (u.pin(1), u.pin(24), u.pin(12), u.pin(13)) == (Q(6, -16), Q(10, -16), Q(6, 24), Q(10, 24)), u.pins
    va, vb, gnd = net(ref, 1), net(ref, 24), net(ref, 12)
    assert net(ref, 2) == va and net(ref, 23) == vb and gnd == "GND"
    assert net(ref, 11) == net(ref, 22) == net(ref, 13) == gnd
    YS, YG = -20, -4                                          # supply lines, ground lines
    # A side: VCCA, DIR1, capacitor, DIR2
    sh.wire(u.pin(1), Q(6, YS), Q(-4, YS))
    sh.wire(u.pin(2), Q(-4, -6), Q(-4, YS))
    sh.wire(Q(-4, YS), Q(-8, YS))
    sh.junction(*Q(-4, YS))
    tie(sh, va, Q(-8, YS), "left", 4, body="left")
    sh.junction(*Q(-8, YS))
    a, b = two(sh, c_a, *Q(-8, -12), top=va, text="left")
    sh.wire(a, Q(-8, YS))
    sh.wire(b, Q(-8, YG))
    sh.wire(u.pin(11), Q(-8, YG))
    sh.junction(*Q(-8, YG))
    tie(sh, gnd, Q(-8, YG), "left", 4, body="left")
    # B side: VCCB (two pins), capacitor, ~OE
    sh.wire(u.pin(24), Q(10, YS), Q(20, YS))
    sh.wire(u.pin(23), Q(20, -6), Q(20, YS))
    sh.wire(Q(20, YS), Q(24, YS))
    sh.junction(*Q(20, YS))
    tie(sh, vb, Q(24, YS), "right", 4, body="right")
    sh.junction(*Q(24, YS))
    a, b = two(sh, c_b, *Q(24, -12), top=vb)
    sh.wire(a, Q(24, YS))
    sh.wire(b, Q(24, YG))
    sh.wire(u.pin(22), Q(24, YG))
    sh.junction(*Q(24, YG))
    tie(sh, gnd, Q(24, YG), "right", 4, body="right")
    # ground pins
    sh.wire(u.pin(13), Q(10, 26), Q(6, 26))
    sh.wire(u.pin(12), Q(6, 26))
    sh.junction(*Q(6, 26))
    tie(sh, gnd, Q(6, 26), "left", 4, body="left")
    # data pins
    for k in range(8):
        pin_tie(sh, u, 3 + k, "left", 6)
        pin_tie(sh, u, 21 - k, "right", 6)
    return u


# --- U10 (TI60F225) units: pages 2, 5, 6 ----------------------------------------------------------------
PDF = board.path("source", "schematic_pdf", "fpga_boardv2.5.PDF")
FPGA_UNIT_PAGE = {1: 2, 3: 2, 2: 5, 4: 5, 5: 5, 6: 5, 7: 6, 8: 6}     # unit number (A = 1) -> PDF page
_BALL_TEXT = None


def ball_texts():
    """{ball: (pin name, label or None)} of U10 as printed in the PDF (text layer, positions at 200 dpi):
    the ball id stands on the pin stub of its unit, the pin name 30 px away inside the body, the
    terminal label (if the pin is wired to one) up to 120 px away on the other side."""
    global _BALL_TEXT
    if _BALL_TEXT is None:
        from p2k.pdftext import pdf_words
        s = 200 / 72
        words = pdf_words(PDF)
        _BALL_TEXT = {}
        for ball in (p for (r, p) in _ipc()[0] if r == "U10"):
            page = FPGA_UNIT_PAGE[unit_of("U10", ball)]
            ws = [(x0 * s, (y0 + y1) / 2 * s, x1 * s, t) for n, x0, y0, x1, y1, t in words if n == page]
            hits = []
            for n, x0, y0, x1, y1, t in words:
                if n != page or t != ball:
                    continue
                yl = y1 * s + 2                               # the pin line runs just below the ball id
                row = [w for w in ws if abs(w[1] - yl) < 9 and w[3] != ball]
                lft = max((w for w in row if w[2] < x0 * s), key=lambda w: w[2], default=None)
                rgt = min((w for w in row if w[0] > x1 * s), key=lambda w: w[0], default=None)
                dl = x0 * s - lft[2] if lft else 1e9
                dr = rgt[0] - x1 * s if rgt else 1e9
                if min(dl, dr) <= 32:                         # a pin stub (other hits: refdes C1, J1 ... elsewhere)
                    inner, outer, d = (lft, rgt, dr) if dl < dr else (rgt, lft, dl)
                    hits.append((inner[3], outer[3] if outer and d <= 120 else None))
            assert len(hits) == 1, f"U10 ball {ball}: PDF hits {hits}"
            _BALL_TEXT[ball] = hits[0]
    return _BALL_TEXT


def fpga_unit(sh, unit, x, y, n=4, skip=(), alias=None, ref="U10"):
    """Unit `unit` (1-8 = A-H) of U10 with its symbol origin at PDF position (x, y); "U10x" above and
    the value below the left edge of the body, as in the PDF. Every ball not in `skip` gets its IPC net
    by pin_tie() on the side it points to (label n grid units out - global labels further out on a side
    that also has local labels -, sideways power symbol, no-connect
    flag on an N/C pad, nothing for an auto-named net: the sheet draws those wires).

    Every ball of the unit is compared with the PDF (ball_texts()): the pin name must be the symbol's;
    a ball without a terminal label must be N/C, on a rail or on an auto-named net (wired by the
    sheet); a label must be the IPC net (case-insensitive) or the Proteus alias given in `alias`
    {PDF label: IPC net}, and every alias must be used. Returns the placed unit."""
    alias = dict(alias or {})
    sub = next(s for s in find_all(lib()[sym(ref)], "symbol") if s[1].endswith(f"_{unit}_1"))
    rect = find(sub, "rectangle")
    xs = [float(find(rect, k)[1]) for k in ("start", "end")]
    ys = [float(find(rect, k)[2]) for k in ("start", "end")]
    ox, oy = P(x, y)
    u = sh.place(sym(ref), ref, ox, oy, unit=unit, value=sh_value(ref),
                 ref_at=(round(ox + min(xs), 4), round(oy - max(ys) - 1.27, 4), 0, "left"),
                 value_at=(round(ox + min(xs), 4), round(oy - min(ys) + 1.905, 4), 0, "left"))
    names = {num: name for name, num in ((find(p, "name")[1], find(p, "number")[1]) for p in find_all(sub, "pin"))}
    assert set(names) == set(u.pins), (unit, sorted(set(names) ^ set(u.pins)))
    used = set()
    # local labels stand n units out; the global labels of that side start beyond the longest local
    # label (at the 2.54 mm pin pitch a local label's text would lie on the global label one row up)
    kinds = {b: (net_kind(net(ref, b)) if net(ref, b) != NC else None, "left" if pt[0] < ox else "right")
             for b, pt in u.pins.items() if b not in skip}
    far = {}
    for b, (kind, side) in kinds.items():
        if kind == "local":
            far[side] = max(far.get(side, 0), n + 2 + -(-len(net(ref, b)) * 85 // 100))
    for ball, pt in u.pins.items():
        ipc = net(ref, ball)
        name, label = ball_texts()[ball]
        if ipc != NC and net_kind(ipc) == "wire":
            label = None                                      # wired to parts: the next text is not a terminal
        assert name == names[ball], f"{ref}-{ball}: PDF pin name {name}, symbol {names[ball]}"
        if label is None or ipc in RAILS:
            assert ipc == NC or ipc in RAILS or net_kind(ipc) == "wire", f"{ref}-{ball}: no PDF label, IPC net {ipc}"
            assert label is None or label.upper() == ipc, f"{ref}-{ball}: PDF label {label}, IPC net {ipc}"
        elif label in alias:
            assert alias[label] == ipc, f"{ref}-{ball}: alias {label} = {alias[label]}, IPC net {ipc}"
            used.add(label)
        else:
            assert label.upper() == ipc.upper(), f"{ref}-{ball}: PDF label {label}, IPC net {ipc} (finding?)"
        if ball in skip:
            continue
        kind, side = kinds[ball]
        pin_tie(sh, u, ball, side, far.get(side, n) if kind == "global" else n, body=side)
    assert used == set(alias), f"unit {unit}: unused aliases {sorted(set(alias) - used)}"
    return u


def rail_bus(sh, placed, pins, at, side, n=3, m=4):
    """The PDF's supply bus: the vertically stacked pins `pins` of a placed part, all on one IPC rail,
    joined by a line n grid units out on `side`; from the row of pin `at` a stub of m more units to the
    power symbol (pointing sideways). Junctions where a middle pin row meets the line."""
    rail = net(placed.ref, pins[0])
    assert rail in RAILS and all(net(placed.ref, p) == rail for p in pins), (placed.ref, pins, rail)
    pts = sorted((placed.pin(p) for p in pins), key=lambda q: q[1])
    assert len({q[0] for q in pts}) == 1, pts
    xv = _STEP[side](pts[0], n)[0]
    ya = placed.pin(at)[1]
    for q in pts:
        sh.wire(q, (xv, q[1]))
    for a, b in zip(pts, pts[1:]):
        sh.wire((xv, a[1]), (xv, b[1]))
    for q in pts[1:-1]:
        if q[1] != ya:
            sh.junction(xv, q[1])
    if len(pts) > 1:
        sh.junction(xv, ya)
    return tie(sh, rail, (xv, ya), side, m, body=side)
