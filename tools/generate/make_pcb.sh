#!/usr/bin/env bash
# FROZEN (generation stopped 2026-11-20, STATUS.md "Decisions"): the committed
# kicad/tube_control_card.kicad_pcb is the source now and carries hand edits that this
# generator does not know, so a rebuild would silently drop them. Kept as history.
#
# Phase 3: rebuilt kicad/tube_control_card.kicad_pcb from the schematic and the Proteus gerbers
# (p2k make_pcb, default steps: build_pcb, gerber_to_tracks, assign_nets, pours_to_zones,
# place_refdes; `--check` rebuilds into build/tmp and compares byte for byte).
# Runs only with --force-regenerate (e.g. on a checkout of the freeze commit, to reproduce it).
force=0; args=()
for a in "$@"; do
    if [ "$a" = --force-regenerate ]; then force=1; else args+=("$a"); fi
done
if [ $force -ne 1 ]; then
    echo "make_pcb.sh: generation of this board stopped (STATUS.md \"Decisions\"); the board file is hand-edited." >&2
    echo "make_pcb.sh: refusing to rebuild it. Use --force-regenerate only on a checkout of the freeze commit." >&2
    exit 2
fi
cd "$(dirname "$0")/../.." && exec tools/p2k/bin/p2k make_pcb "${args[@]}"
