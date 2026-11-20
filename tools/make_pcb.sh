#!/usr/bin/env bash
# Phase 3: rebuild kicad/tube_control_card.kicad_pcb from the schematic and the Proteus gerbers
# (p2k make_pcb, default steps: build_pcb, gerber_to_tracks, assign_nets, pours_to_zones,
# place_refdes; `--check` rebuilds into build/tmp and compares byte for byte).
cd "$(dirname "$0")/.." && exec tools/p2k/bin/p2k make_pcb "$@"
