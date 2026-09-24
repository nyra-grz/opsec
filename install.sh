#!/bin/bash
# Installs the `opsec` command (macOS / Linux).
#
#   curl -fsSL https://raw.githubusercontent.com/nyra-grz/opsec/main/install.sh | bash
#
# Uninstall:
#   curl -fsSL https://raw.githubusercontent.com/nyra-grz/opsec/main/install.sh | bash -s -- --uninstall
#
# Environment overrides:
#   OPSEC_BASE_URL   raw base URL to download opsec.py from
#                    (default: https://raw.githubusercontent.com/nyra-grz/opsec/main)
#   OPSEC_DEST       full path to install the `opsec` command to
#                    (default: /usr/local/bin/opsec, which is on the global PATH)
#   OPSEC_PYTHON     path to the Python 3.8+ interpreter to use
#                    (skip detection and Python auto-install)
set -e

REPO="nyra-grz/opsec"
BASE_URL="${OPSEC_BASE_URL:-https://raw.githubusercontent.com/$REPO/main}"
DEST="${OPSEC_DEST:-/usr/local/bin/opsec}"

# ---------------------------------------------------------------------------
# Python detection
# ---------------------------------------------------------------------------

# Prints the path of a usable Python (>= 3.8) or nothing. Never fails, so it is
# safe to use under `set -e`.
find_python() {
  local cand
  for cand in "${OPSEC_PYTHON:-}" python3 python \
    /usr/local/bin/python3 /opt/homebrew/bin/python3 \
    /usr/bin/python3 "$HOME/.local/bin/python3"; do
    [ -n "$cand" ] || continue
    if command -v "$cand" >/dev/null 2>&1 &&
      "$cand" -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 8) else 1)' >/dev/null 2>&1; then
      command -v "$cand"
      return 0
    fi
  done
  return 0
}

# Installs Python 3 with the first package manager it finds (non-interactive).
install_python_linux() {
  local SUDO
  if [ "$(id -u)" -eq 0 ]; then
    SUDO=""
  else
    SUDO="sudo"
  fi

  if command -v apt-get >/dev/null 2>&1; then
    echo "Installing Python 3 with apt-get..." >&2
    $SUDO apt-get update || true
    $SUDO apt-get install -y python3 || true
    return 0
  fi
  if command -v dnf >/dev/null 2>&1; then
    echo "Installing Python 3 with dnf..." >&2
    $SUDO dnf install -y python3 || true
    return 0
  fi
  if command -v yum >/dev/null 2>&1; then
    echo "Installing Python 3 with yum..." >&2
    $SUDO yum install -y python3 || true
    return 0
  fi
  if command -v pacman >/dev/null 2>&1; then
    echo "Installing Python 3 with pacman..." >&2
    $SUDO pacman -Sy --noconfirm python || true
    return 0
  fi
  if command -v apk >/dev/null 2>&1; then
    echo "Installing Python 3 with apk..." >&2
    $SUDO apk add --no-cache python3 || true
    return 0
  fi
  if command -v zypper >/dev/null 2>&1; then
    echo "Installing Python 3 with zypper..." >&2
    $SUDO zypper --non-interactive install python3 || true
    return 0
  fi

  echo "Could not find a package manager to install Python 3." >&2
  echo "Install Python 3.8 or newer from https://www.python.org/downloads/ and re-run the installer." >&2
  exit 1
}

# Prints the path of a usable Python, installing one first if it is missing.
ensure_python() {
  local py uv
  py="$(find_python)"
  if [ -n "$py" ]; then
    printf '%s\n' "$py"
    return 0
  fi

  echo "python3 not found - installing it now..." >&2

  if [ "$(uname -s)" = "Darwin" ]; then
    if command -v brew >/dev/null 2>&1; then
      echo "Installing Python with Homebrew..." >&2
      brew install python || true
    else
      uv="$(command -v uv 2>/dev/null || true)"
      if [ -z "$uv" ]; then
        echo "Installing uv (a Python toolchain manager)..." >&2
        curl -LsSf https://astral.sh/uv/install.sh | sh || true
        uv="$HOME/.local/bin/uv"
      fi
      if [ -x "$uv" ]; then
        echo "Installing Python 3.12 with uv..." >&2
        "$uv" python install 3.12 || true
        # `uv python find` prints the concrete interpreter path.
        py="$("$uv" python find 3.12 2>/dev/null || true)"
        if [ -n "$py" ] && [ -x "$py" ]; then
          printf '%s\n' "$py"
          return 0
        fi
      fi
    fi
  else
    install_python_linux
  fi

  # Re-check after the install attempt.
  py="$(find_python)"
  if [ -n "$py" ]; then
    printf '%s\n' "$py"
    return 0
  fi

  echo "Python could not be installed automatically." >&2
  echo "Install Python 3.8 or newer from https://www.python.org/downloads/ and re-run the installer." >&2
  echo "Tip: set OPSEC_PYTHON=/path/to/python3 to point the installer at a specific interpreter." >&2
  exit 1
}

# ---------------------------------------------------------------------------
# Uninstall
# ---------------------------------------------------------------------------

if [ "${1:-}" = "--uninstall" ]; then
  if [ -w "$(dirname "$DEST")" ] || [ ! -e "$DEST" ]; then
    rm -f "$DEST"
  else
    echo "Removing opsec from $DEST (needs your password)..."
    sudo rm -f "$DEST"
  fi
  echo "opsec removed."
  exit 0
fi

# Make sure a Python 3.8+ interpreter exists before we touch anything.
PY="$(ensure_python)"

tmp=""
tmp2=""
opsec_file=""
cleanup() {
  if [ -n "$tmp" ]; then rm -f "$tmp"; fi
  if [ -n "$tmp2" ]; then rm -f "$tmp2"; fi
  return 0
}
trap cleanup EXIT

tmp="$(mktemp)"

# A local checkout installs its own copy; a piped one-liner downloads it.
if [ -f "$0" ] && [ -f "$(dirname "$0")/opsec.py" ]; then
  cp "$(dirname "$0")/opsec.py" "$tmp"
else
  curl -fsSL "$BASE_URL/opsec.py" -o "$tmp"
fi

# opsec.py normally ships with `#!/usr/bin/env python3`. If `python3` is not on
# PATH but we found/installed a concrete interpreter, point the shebang at it.
# Avoid GNU-only `sed -i`: rebuild the file by hand instead.
opsec_file="$tmp"
if ! command -v python3 >/dev/null 2>&1; then
  tmp2="$(mktemp)"
  {
    printf '#!%s\n' "$PY"
    tail -n +2 "$tmp"
  } >"$tmp2"
  opsec_file="$tmp2"
fi

# ---------------------------------------------------------------------------
# Install
# ---------------------------------------------------------------------------

# Use sudo only when the destination directory is not writable. If it does not
# exist yet, fall back to the nearest existing parent to decide.
dest_dir="$(dirname "$DEST")"
probe="$dest_dir"
while [ ! -d "$probe" ] && [ "$probe" != "/" ]; do
  probe="$(dirname "$probe")"
done

if [ -w "$probe" ]; then
  mkdir -p "$dest_dir"
  install -m 755 "$opsec_file" "$DEST"
else
  echo "Installing opsec to $DEST (needs your password)..."
  sudo mkdir -p "$dest_dir"
  sudo install -m 755 "$opsec_file" "$DEST"
fi

case ":$PATH:" in
  *":$dest_dir:"*) ;;
  *)
    echo
    echo "Note: $dest_dir is not on your PATH."
    echo "Add it to PATH (e.g. export PATH=\"$dest_dir:\$PATH\") to run 'opsec' from anywhere."
    ;;
esac

echo
echo "Done. Run it with:  sudo opsec"
echo "Quit with Ctrl+C."
