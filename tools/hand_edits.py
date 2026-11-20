#!/usr/bin/env python3
"""Hand edits after generation stopped (STATUS.md "Hand edits after generation stopped"): the recorded
deviations of the committed KiCad files from the Proteus design, and a wrapper that runs a shared p2k check
with exactly these deviations accepted.

    tools/p2k/bin/kipy tools/hand_edits.py check_board          (pcbnew tools: check_board, assign_nets)
    python3 tools/hand_edits.py compare_netlists               (compare_netlists, ipc356_diff, gerber_roundtrip)

What the wrapper changes, and nothing else (every other failure of the tool stays a failure):
  * PIN_NETS: the IPC records of exactly these pins are read with the new net (net, net_raw, net_id copied
    from another pad record of that net), through the p2k record filter `pcb.configure(records=)` (used by
    check_board, assign_nets, ipc356_diff, gerber_roundtrip) and by wrapping `compare_netlists.load_ipc`. Each
    listed pin must be in the IPC exactly once, on its recorded old net, else the wrapper fails. So the board /
    schematic must carry exactly the new nets on these pins (a reverted edit fails like any wrong net).
  * AREAS (gerber_roundtrip only, `main(in_area=)`): copper differences whose cluster box lies inside the area
    of that layer are classed "deviation" instead of "other", and coverage misses inside it are accepted.
  * TRACK_DELTA (gerber_roundtrip strict roundtrip_counts): the KiCad track draws of that layer must be the
    Proteus count plus exactly this number (flash counts unchanged).
The PDF reading check (tools/phase4_reading/reading.py) imports PIN_LABELS from here.
Coordinates: IPC frame (mm, Y up; KiCad y = -IPC y).
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# --- the recorded hand edits ---------------------------------------------------------------------------

# Finding 9 (user decision 2026-11-20): ADC1 = ADC121C027, datasheet SOT-23-6 pin 1 = VA (supply), pin 3 = VIN
# (input). Proteus wired VA (pad A1) to the filtered BIASFEEDBACK node #00660 (R34 / C68) and VIN (pad COM2) to
# 3V3; fixed: A1 on 3V3, COM2 on #00660. {(refdes, pin): (Proteus IPC net, net now)}, IPC net names.
PIN_NETS = {
    ("ADC1", "A1"): ("#00660", "3V3"),
    ("ADC1", "COM2"): ("3V3", "#00660"),
}
# The same for the PDF reading (labels of tools/phase4_reading/reading_data.py): pin -> label read in the PDF
# (Proteus) and the label class the KiCad net must now belong to.
PIN_LABELS = {
    ("ADC1", "A1"): ("~adcva", "3V3"),
    ("ADC1", "COM2"): ("3V3", "~adcva"),
}
# The rerouted copper around ADC1 (F.Cu only): x 97.6 .. 101.4, KiCad y 19.3 .. 23.1 (ADC1 at (97.975, 21.15),
# its pads, C67 / C68 and the R34 pad 2 end). (xmin, ymin, xmax, ymax) in the IPC frame.
AREAS = {"F.Cu": (97.6, -23.1, 101.4, -19.3)}
# KiCad track segments added minus removed per layer (finding 9: 5 removed, 8 added, 5 moved on F.Cu).
TRACK_DELTA = {"F.Cu": 3}

# --------------------------------------------------------------------------------------------------------

PCB_TOOLS = ("check_board", "assign_nets")
TOOLS = ("compare_netlists", "ipc356_diff", "gerber_roundtrip") + PCB_TOOLS


def in_area(layer, x, y):
    a = AREAS.get(layer)
    return bool(a) and a[0] <= x <= a[2] and a[1] <= y <= a[3]


def amend_records(recs):
    """IPC records with the PIN_NETS applied (a new list; the originals untouched). Exits on any mismatch."""
    errors = []
    template = {}
    for net in {new for _, new in PIN_NETS.values()}:
        t = [p for p in recs if p["kind"] == "pad" and p["net"] == net and (p["refdes"], p["pin"]) not in PIN_NETS]
        if not t:
            errors.append(f"no IPC pad record on net {net}")
        else:
            template[net] = {k: t[0][k] for k in ("net", "net_raw", "net_id")}
    out, seen = [], {}
    for p in recs:
        key = (p["refdes"], p["pin"]) if p["kind"] == "pad" else None
        if key in PIN_NETS:
            old, new = PIN_NETS[key]
            seen[key] = seen.get(key, 0) + 1
            if p["net"] != old:
                errors.append(f"{key[0]}-{key[1]}: IPC net {p['net']}, recorded {old}")
            elif new in template:
                p = dict(p, **template[new])
        out.append(p)
    for key in PIN_NETS:
        if seen.get(key) != 1:
            errors.append(f"{key[0]}-{key[1]}: {seen.get(key, 0)} IPC pad records, expected 1")
    if errors:
        sys.exit("hand_edits: " + "; ".join(errors))
    return out


def note():
    print("hand_edits: accepted pin-net changes (STATUS.md \"Hand edits after generation stopped\"): "
          + "; ".join(f"{r}-{p} {o} -> {n}" for (r, p), (o, n) in PIN_NETS.items()))


def run(tool, argv):
    sys.path.insert(0, os.path.join(ROOT, "tools", "p2k"))
    from p2k import pcb
    pcb.configure(records=amend_records)
    note()
    sys.argv = [f"p2k {tool}"] + argv
    if tool == "compare_netlists":
        from p2k import compare_netlists as cn

        def load_ipc():
            pin_net = cn._LOAD_IPC()          # under this wrapper it leaves SPLIT_PIN_MERGES to us
            with open(os.path.join(ROOT, "reference", "ipc356_pads.json")) as f:
                pads = json.load(f)["pads"]
            pin_net = cn.split_pin_merges(pads, pin_net)
            for key, (old, new) in PIN_NETS.items():
                if pin_net.get(key) != old:
                    sys.exit(f"hand_edits: {key[0]}-{key[1]}: IPC net {pin_net.get(key)}, recorded {old}")
                pin_net[key] = new
            return pin_net
        cn.load_ipc = load_ipc
        return cn.main()
    if tool == "ipc356_diff":
        from p2k import ipc356_diff
        return ipc356_diff.main(argv)
    if tool == "gerber_roundtrip":
        from p2k import gerber_roundtrip as gr
        orig = gr.count_check

        def count_check(pname, klayer, user, gp, gk):
            errors, (want, kd, pf, kf) = orig(pname, klayer, user, gp, gk)
            d = TRACK_DELTA.get(klayer, 0)
            if not d:
                return errors, (want, kd, pf, kf)
            errors = [e for e in errors if not e.startswith(f"counts: {klayer}: {kd} KiCad track draws")]
            if kd != want + d:
                errors.append(f"counts: {klayer}: {kd} KiCad track draws, gerber_to_tracks builds {want} from the "
                              f"Proteus draws, hand edits {d:+d} (TRACK_DELTA) -> expected {want + d}")
            else:
                print(f"hand_edits: {klayer}: {kd} KiCad track draws = {want} Proteus + {d} (TRACK_DELTA)")
            return errors, (want + d, kd, pf, kf)
        gr.count_check = count_check
        print("hand_edits: copper differences accepted only inside "
              + ", ".join(f"{l} x {a[0]}..{a[2]} y {a[1]}..{a[3]}" for l, a in AREAS.items()) + " (AREAS)")
        return gr.main(argv, in_area=in_area)
    if tool == "check_board":
        from p2k import check_board
        return check_board.main(argv)
    if tool == "assign_nets":
        from p2k import assign_nets
        return assign_nets.main()
    sys.exit(f"hand_edits: unknown tool {tool!r} (one of {', '.join(TOOLS)})")


if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in TOOLS:
        sys.exit(__doc__)
    sys.exit(run(sys.argv[1], sys.argv[2:]))
