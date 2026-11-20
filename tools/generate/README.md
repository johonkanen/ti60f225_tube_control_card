# tools/generate – frozen generators (history, do not run)

Generation of this board **stopped on 2026-11-20** (user decision, STATUS.md "Decisions"). Since then
the committed KiCad files are the source: `lib/part_map.csv`, `lib/tube_control_card.kicad_sym`,
`kicad/*.kicad_sch`, `lib/tube_control_card.pretty/`, `lib/footprint_map.csv`, `kicad/fp-lib-table` and
`kicad/tube_control_card.kicad_pcb` are edited directly (STATUS.md "Hand edits after generation stopped").

The scripts here wrote those files from the Proteus sources up to the freeze. Running them now would
overwrite the hand edits, so they are kept only as a record of how rev A was built:

| Script | Wrote |
|---|---|
| `make_part_map.py` | `lib/part_map.csv` (p2k `part_map.run`) |
| `gen_symbols.py` | `lib/tube_control_card.kicad_sym` |
| `sheets/sheetNN.py`, `sheets/_common.py` | `kicad/NN_*.kicad_sch` (one per Proteus PDF page) |
| `gen_footprints.py` | `lib/tube_control_card.pretty/`, `lib/footprint_map.csv`, `kicad/fp-lib-table` |
| `make_pcb.sh` | `kicad/tube_control_card.kicad_pcb` (`p2k make_pcb`; refuses to run without `--force-regenerate`) |

To reproduce the freeze point, check out the freeze commit (STATUS.md "Decisions") and run them there.

Still read by a check: `p2k check_pin_order` imports the footprint `RULES` of `gen_footprints.py`
(`FOOTPRINT_SCRIPT` in p2k_config.py; read only), and `tools/test_no_connect.py` draws its scratch
sheets with `sheets/_common.py` in a scratch copy of the board.
