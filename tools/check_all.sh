#!/usr/bin/env bash
# Run every verification step. Exit status is non-zero if any step fails.
# Each phase adds its steps here (playbook principle 5). The tools are the proteus2kicad
# submodule in tools/p2k; board values in p2k_config.py.
set -u
cd "$(dirname "$0")/.."
[ -x tools/p2k/bin/p2k ] || { echo "tools/p2k missing: git submodule update --init"; exit 1; }
fail=0
step() { echo "== $1"; shift; "$@" || { echo "!! FAILED: $*"; fail=1; }; }

step "KiCad environment" tools/p2k/bin/kipy -c "import pcbnew; v = pcbnew.GetBuildVersion(); print('pcbnew', v); assert v.startswith('10.0.7'), v"
# p2k ipc356 --check / p2k check_sources plus the board-local acceptance of the split terminal
# nets, the SMD test pads and the BGAPad flashes (STATUS.md "p2k candidates")
step "IPC-D-356A parser self-check (p2k ipc356 --check + board exceptions)" python3 tools/ipc356_check.py
step "Gerber X2 export vs IPC (p2k check_sources + board exceptions)" python3 tools/check_sources.py

echo
[ $fail -eq 0 ] && echo "ALL CHECKS PASSED" || echo "SOME CHECKS FAILED"
exit $fail
