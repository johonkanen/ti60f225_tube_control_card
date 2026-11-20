"""Phase 4 (independent verification, 2026-11-20): my own reading of source/schematic_pdf (by eye from 300 dpi renders,
reading_data.py: every pin of every part, the alias pairs of pages 1, 2, 7, 9, 10, 11) vs the raw IPC (own parser) and the KiCad netlist (kicadxml).
Partition check: labels are joined into classes by the alias pairs I read; pins read on one class must share one IPC net
and one KiCad net, different classes must be on different nets; NC = N/C in the IPC and unconnected-(...) in KiCad.
Hand edits after generation stopped (tools/hand_edits.py PIN_LABELS, exactly those pins): the IPC side keeps the
label read in the PDF, the KiCad net must belong to the recorded new label's class instead."""
import sys, re, collections
import os
D = os.path.dirname(os.path.abspath(__file__)) + "/"
sys.path.insert(0, D)
import ind
sys.path.insert(0, os.path.dirname(os.path.dirname(D)))   # tools/ (hand_edits.py: data only, no p2k code)
from hand_edits import PIN_LABELS
hand_seen = set()
names, pins, recs = ind.ipc(); pn, comps = ind.kicad()
READ = {}
def R(page, ref, d):
    for pin, lab in d.items():
        assert (page, ref, str(pin)) not in READ and not any(k[1] == ref and k[2] == str(pin) for k in READ), (ref, pin)
        READ[(page, ref, str(pin))] = lab
def shifter(page, ref, a, b):
    d = {1: "1V8", 2: "1V8", 11: "GND", 12: "GND", 13: "GND", 22: "GND", 23: "3V3", 24: "3V3"}
    d.update({3 + i: n for i, n in enumerate(a.split())}); d.update({21 - i: n for i, n in enumerate(b.split())})
    R(page, ref, d)
exec(open(D + "reading_data.py").read())
par = {}
def find(a):
    a = a if a.startswith("~") else a.upper()
    par.setdefault(a, a)
    while par[a] != a: a = par[a]
    return a
for tok in re.findall(r"(\S+)=(\S+)", "\n".join(l.split(":", 1)[1] for l in ALIAS.strip().splitlines())):
    par[find(tok[0])] = find(tok[1])
# D1: as the PDF draws them, one node per terminal (the IPC has two nets per split terminal): IPC nets of a split pin are unioned
ipar = {}
def ifind(a):
    ipar.setdefault(a, a)
    while ipar[a] != a: a = ipar[a]
    return a
for k, v in pins.items():
    for n in v[1:]: ipar[ifind(n)] = ifind(v[0])
errs = []; cls_i = collections.defaultdict(set); cls_k = collections.defaultdict(set); per = collections.defaultdict(lambda: [0, set()])
def see(page, ref, pin, lab):
    i = pins.get((ref, pin)); k = pn.get((ref, pin))
    per[page][0] += 1; per[page][1].add(ref)
    if i is None or k is None: errs.append(f"p{page} {ref}-{pin}: not in IPC / KiCad"); return
    if lab == "NC":
        if i != ["N/C"] or not k[0].startswith("unconnected-("): errs.append(f"p{page} {ref}-{pin}: read NC, IPC {i}, KiCad {k[0]}")
        return
    if i == ["N/C"] or k[0].startswith("unconnected-("): errs.append(f"p{page} {ref}-{pin}: read {lab}, IPC {i}, KiCad {k[0]}"); return
    kl = lab
    if (ref, pin) in PIN_LABELS:
        old, new = PIN_LABELS[(ref, pin)]
        if lab != old: errs.append(f"p{page} {ref}-{pin}: read {lab}, hand edit recorded for {old}")
        kl = new; hand_seen.add((ref, pin))
    c = find(lab); cls_i[c].add(ifind(i[0])); cls_k[find(kl)].add(k[0])
    cls_members[c].append(f"{ref}-{pin}")
cls_members = collections.defaultdict(list)
arr = collections.defaultdict(list)
for (page, ref, pin), lab in READ.items():
    if pin == "*" or pin.startswith("u"): arr[(page, ref)].append((pin, lab))
    else: see(page, ref, pin, lab)
# two-pin parts and resistor-array units: the part must have a pin pair (for arrays: pins n and 9-n) on the two nets read
for (page, ref), units in arr.items():
    ps = sorted(p for (r, p) in pins if r == ref)
    pairs = [("1", "2")] if len(ps) == 2 else [(str(n), str(9 - n)) for n in range(1, 5)]
    assert sorted(sum(map(list, pairs), [])) == ps, (ref, ps)
    used = set()
    for pin, (a, b) in units:
        per[page][0] += 2; per[page][1].add(ref)
        hit = None
        for p, q in pairs:
            if (p, q) in used: continue
            for x, y in ((p, q), (q, p)):
                ia, ib = ifind(pins[(ref, x)][0]), ifind(pins[(ref, y)][0])
                # tentative: accept if consistent with classes seen so far, resolved in the second pass
                hit = hit or []
                hit.append((x, y))
        cand = []
        for x, y in hit:
            ia, ib = ifind(pins[(ref, x)][0]), ifind(pins[(ref, y)][0])
            ok = all((not cls_i[find(l)] or cls_i[find(l)] == {n}) for l, n in ((a, ia), (b, ib)))
            known = sum(bool(cls_i[find(l)]) for l in (a, b))
            if ok: cand.append((known, x, y))
        cand.sort(reverse=True)
        if not cand: errs.append(f"p{page} {ref} {pin}: no pin pair on nets read ({a}, {b})"); continue
        _, x, y = cand[0]; used.add(tuple(sorted((x, y), key=int)) if True else None)
        see(page, ref, x, a); see(page, ref, y, b); per[page][0] -= 2
for rp in sorted(set(PIN_LABELS) - hand_seen): errs.append(f"hand edit {rp[0]}-{rp[1]}: pin not read")
inv_i = collections.defaultdict(set); inv_k = collections.defaultdict(set)
for c, ns in cls_i.items():
    if len(ns) != 1: errs.append(f"label class {c}: pins {cls_members[c][:8]} on {len(ns)} IPC nets {sorted(ns)}")
    for n in ns: inv_i[n].add(c)
for c, ns in cls_k.items():
    if len(ns) != 1: errs.append(f"label class {c}: pins {cls_members[c][:8]} on {len(ns)} KiCad nets {sorted(ns)}")
    for n in ns: inv_k[n].add(c)
for n, cs in inv_i.items():
    if len(cs) != 1: errs.append(f"IPC net {n} carries {len(cs)} label classes I read as separate: {sorted(cs)}")
for n, cs in inv_k.items():
    if len(cs) != 1: errs.append(f"KiCad net {n} carries {len(cs)} label classes I read as separate: {sorted(cs)}")
# names: the IPC net name (unless auto-named #...) must be one of the labels of its class
labels_of = collections.defaultdict(set)
for a in list(par): labels_of[find(a)].add(a)
namediff = []
for c, ns in cls_i.items():
    for n in ns:
        raw = {"GND=POWER": "GND", "VCC/VDD=POWER": "AD_3V3"}.get(n, n)
        raw = re.sub(r"\.\d{5}$", "", raw)
        if not raw.startswith("#") and raw.upper() not in labels_of[c] and not c.startswith("~"): namediff.append((c, raw))
        if c.startswith("~") and not raw.startswith("#"): namediff.append((c, raw))
# completeness of the IPC nets I touched: every IPC pin of a net I read must have been read
readpins = set()
for c, m in cls_members.items(): readpins |= set(m)
touched = {n for ns in cls_i.values() for n in ns}
unread = collections.defaultdict(list)
for (r, p), v in pins.items():
    if v != ["N/C"] and ifind(v[0]) in touched and f"{r}-{p}" not in readpins: unread[ifind(v[0])].append(f"{r}-{p}")
total = sum(n for n, _ in per.values())
for p, (n, refs) in sorted(per.items()): print(f"page {p:2d}: {n:3d} pins read on {len(refs):2d} parts")
allread = {(k[1], k[2]) for k in READ if k[2] != "*" and not k[2].startswith("u")}
print(f"total {total} pins read of {len(pins)} IPC pins on {len({k[1] for k in READ})} of 146 parts; {len(cls_i)} nets (label classes) "
      f"of {len(set(map(ifind, (v[0] for v in pins.values() if v != ['N/C']))))} IPC nets (after the D1 union); NC read {sum(1 for v in READ.values() if v == 'NC')}")
print("IPC nets touched with pins I did not read:", dict(unread) or "none")
print("IPC name not among the labels of its class:", namediff or "none")
print("parts not read:", sorted({r for r, _ in pins} - {k[1] for k in READ}))
print("hand edits (KiCad net in the class of the new label):", "; ".join(f"{r}-{p} {o} -> {n}" for (r, p), (o, n) in PIN_LABELS.items()) or "none")
for e in errs: print("DIFF", e)
print("reading:", "no difference" if not errs else f"{len(errs)} differences")
sys.exit(1 if errs or unread or namediff else 0)
