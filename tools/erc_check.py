#!/usr/bin/env python3
"""Judge a kicad-cli ERC report (called by tools/erc.sh).

Fails on
- every ERC error, except the ones listed in tools/erc_pending.txt (errors that are expected
  while the transcription is in progress, e.g. an input pin whose driver is a U10 ball on a
  sheet that is not drawn yet). A pending entry that no longer occurs also fails (remove it),
  so the list cannot go stale and must be empty when Phase 1 is done;
- the warning types in FATAL_WARNINGS. no_connect_connected (decision D2): a no-connect flag
  on a pin that is wired to something is always a drawing mistake here, and with a pin of
  type no_connect the KiCad 10 netlist would hide it from compare_netlists (the pin stays in
  its own unconnected-(...) net).
Other warnings are counted by type (explained in STATUS.md).

  tools/erc_check.py [--no-pending] reports/erc.rpt
"""
import os
import re
import sys
from collections import Counter

FATAL_WARNINGS = {"no_connect_connected"}
PENDING = os.path.join(os.path.dirname(os.path.abspath(__file__)), "erc_pending.txt")


def violations(path):
    """[(type, severity, [item lines])]"""
    out = []
    for line in open(path, encoding="utf-8"):
        m = re.match(r"\[(\w+)\]:", line)
        if m:
            out.append([m.group(1), "?", []])
        elif out and line.strip().startswith(";"):
            out[-1][1] = line.strip("; \n").split()[0]
        elif out and line.strip().startswith("@("):
            out[-1][2].append(line.strip())
    return out


def key(v):
    """'type REF PIN' of a violation whose first item is a symbol pin, else None."""
    m = re.search(r"Symbol (\S+) Pin (\S+)", v[2][0]) if v[2] else None
    return f"{v[0]} {m.group(1)} {m.group(2)}" if m else None


def main():
    args = sys.argv[1:]
    use_pending = "--no-pending" not in args
    rpt = [a for a in args if not a.startswith("--")][0]
    pending = {}
    if use_pending and os.path.exists(PENDING):
        for line in open(PENDING, encoding="utf-8"):
            entry, _, why = line.partition("#")
            if entry.strip():
                pending[" ".join(entry.split())] = why.strip()
    vs = violations(rpt)
    errors = [v for v in vs if v[1] == "error"]
    warns = [v for v in vs if v[1] == "warning"]
    real = [v for v in errors if key(v) not in pending]
    seen = {key(v) for v in errors}
    stale = sorted(k for k in pending if k not in seen)
    fatal = [v for v in warns if v[0] in FATAL_WARNINGS]
    for v in real:
        print(f"erc: ERROR {v[0]}: " + " | ".join(v[2]))
    for v in fatal:
        print(f"erc: FATAL WARNING {v[0]} (decision D2): " + " | ".join(v[2]))
    for k in stale:
        print(f"erc: stale entry in tools/erc_pending.txt (no longer reported, remove it): {k}")
    by_type = Counter(v[0] for v in warns)
    print(f"erc: {len(real)} errors, {len(warns)} warnings"
          + (" (" + ", ".join(f"{n} {t}" for t, n in sorted(by_type.items())) + ")" if warns else "")
          + (f", {len(errors) - len(real)} pending errors (tools/erc_pending.txt)" if pending else "")
          + f" ({os.path.relpath(rpt)})")
    return 1 if real or fatal or stale else 0


if __name__ == "__main__":
    sys.exit(main())
