#!/bin/bash
# Headless end-to-end smoke test for opsec.py.
#
# opsec.py is validated after it is assembled, so it may not exist yet while
# this file is being written. When it does exist, this script pipes the full
# menu key sequence into it and checks for a handful of markers.
#
# No root needed: OPSEC_ALLOW_NONROOT=1 skips the root check, and because stdin
# is not a tty, opsec.py reads single keypresses straight from the pipe.
set -e

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

tmp="$(mktemp)"
trap 'rm -f "$tmp"' EXIT

fail=0
check() {
  if grep -qF -- "$1" "$tmp"; then
    echo "PASS: found \"$1\""
  else
    echo "FAIL: missing \"$1\""
    fail=1
  fi
}

# Single spaces between the keys satisfy the "press any key" prompts.
rc=0
printf '%s\n' '1 2 3 4 5 6 7 8 9 s b i q' \
  | OPSEC_ALLOW_NONROOT=1 python3 opsec.py --fast >"$tmp" 2>&1 || rc=$?

if [ "$rc" -eq 0 ]; then
  echo "PASS: exit code 0"
else
  echo "FAIL: exit code $rc"
  fail=1
fi

check "Firewall evaded"
check "ACCESS  GRANTED"
check "Implant live"
check "You were never here"

exit "$fail"
