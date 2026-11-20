# Next prompt

Ready-to-paste prompt for the next agent session. Replaced at the end of every session.

```
Convert the Proteus board in /home/jari/dev/ti60f225_tube_control_card to KiCad 10: Phase 4,
independent verification. You are a FRESH READER (preferably Fable, a different model / session from
the one that built the board): do not trust STATUS.md's claims, re-derive them from the sources and
the generated files. Phases 0-3 are done: 12 sheets, 146 parts, footprints, and the PCB
(tools/make_pcb.sh through tools/pcb_wrap.py; 3373 tracks, 240 vias, 20 zones; pad decision A: Proteus
pads on U1 U2 U3 U5 U6 U7 U8 U9 U11 U14 ADC1 U4 U12 J7 J11, PROTEUS_PADS in tools/gen_footprints.py).

Read, in this order: PLAN.md, STATUS.md (phase table, "Phase 3 – PCB – done", "Phase 3 – pad sizes",
"Remaining DRC items", findings 1, 2, 4, 9, 24-26, p2k candidates 1-3, 21, 24-29, Decisions incl. D1, D2,
pad sizes, J8 drill), tools/p2k/CONVERSION_PLAYBOOK.md (sections 1, 3 "Phase 4" and 5),
tools/p2k/README.md (ipc356_diff, gerber_roundtrip, DRILL_SMALLER, DRILL_EXCELLON). Reference (read
only): ~/dev/tube_psu_kicad (Phase 4 done), ~/dev/tube_pi_fxloop_kicad (tools/check_drill_smaller.py,
tools/compare.py, tools/erc.sh).

Start with tools/check_all.sh; it must print "ALL CHECKS PASSED" (compare 146/146, 0 wrong-net pins;
ERC 0 / 14; check_footprints worst 0.030 mm; make_pcb byte-identical; check_board OK; copper 307 groups
0 / 0 / 0 + 5 D1; DRC 0 shorts, only the 32 accepted courtyards and the 5 D1 unconnected items).

Then add to tools/check_all.sh (Phase 4 block), each through a board-local wrapper where this board
needs acceptances (as tools/pcb_wrap.py does for Phase 3; tools/p2k unchanged):
1. p2k ipc356_diff (KiCad IPC-D-356 export vs the Proteus IPC-D-356A) with:
   - the five D1 merges (J2, ISO5V, ISO_G, RS485A, RS485B): compare pad nets by pad sets; the merged IPC
     nets join their kept nets, exactly SPLIT_PIN_MERGES and nothing else;
   - the 4 SMD test pads TP1-TP4: IPC free_pad records with is_tht False (SMD on top, no drill),
     FREE_PAD_FOOTPRINT TestPad_SMD_D0.711mm; check how KiCad's IPC-D-356 export writes them and the U10
     BGA pads;
   - DRILL_SMALLER for J8 (1.016 -> 1.0, user decision).
2. p2k gerber_roundtrip --check (with DRILL_EXCELLON, DRILL_SMALLER for J8) with the U10 BGAPad,CuDef
   aperture function (PAD_FUNCTIONS) and the SMD test pads accepted.
3. Blind spots to check and close board-locally if real:
   - DRILL_SMALLER: is it matched per pad or only by the (Proteus, KiCad) diameter pair? The PI/FX repo
     found that ipc356_diff / gerber_roundtrip accept any pad with the same pair (its
     tools/check_drill_smaller.py closes it: exactly the decided pads may have a smaller drill). Here
     the only expected one is J8 (3 holes); every other pad's drill must be >= Proteus (J7 / J11 now
     0.558 = Proteus).
   - Joined N/C pins: would two N/C pins wired together (or an N/C pin wired to a net) pass
     tools/compare_netlists.py and tools/erc.sh? See the PI/FX tools/compare.py and tools/erc.sh, and
     this board's tools/test_no_connect.py (decision D2). U10 has 62 flagged N/C balls, J11 37 / 38 N/C.
4. An independent PDF-vs-IPC reading sample per sheet (12 sheets): pick a few nets / pins per sheet,
   read them in source/schematic_pdf yourself and compare with the IPC netlist and the KiCad schematic
   (not through the tools). Record what you sampled.

Negative-test every new check (scratch copies under build/tmp with P2K_BOARD; a wrong drill on one pad
with an existing DRILL_SMALLER pair, a wrong net on a pad, a D1 merge removed, a test pad moved, ...)
and record the results in STATUS.md.

Still open and reported only (don't change without asking): findings 1 (D1), 9 (ADC1 VA / VIN), 19,
24 (FLASH1 land pattern), 25 (J11 mirrored numbering), 26 (sub-4-mil gaps, dangling copper).

Rules (PLAN.md section 5): don't change tools/p2k or its pin (c5682dd); board-local workarounds in
tools/, noted in STATUS.md "p2k candidates"; don't touch other repos; report design findings, don't
fix them; generate, don't hand-edit; never use the no_connect pin type; temporary files in build/tmp;
never run the KiCad AppImage with --version (use tools/p2k/bin/kipy and tools/p2k/bin/kicad-cli). At
the end: tools/check_all.sh passing, STATUS.md updated (phase table, Phase 4 section, check output,
negative tests, findings, p2k candidates), README status, next_prompt.md replaced with the prompt for
the next session (Phase 5 clean-up), commit and push (git push origin main). If something needs a user
decision, stop, record it in STATUS.md, commit and push, and report it.
```
