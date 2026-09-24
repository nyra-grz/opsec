#!/bin/bash
# Installs opsec to /usr/local/bin (macOS and Linux).
#   curl -fsSL https://raw.githubusercontent.com/nyra-grz/opsec/main/install.sh | bash
# Uninstall:
#   curl -fsSL https://raw.githubusercontent.com/nyra-grz/opsec/main/install.sh | bash -s -- --uninstall
set -e

REPO="nyra-grz/opsec"
DEST="/usr/local/bin/opsec"
URL="https://raw.githubusercontent.com/$REPO/main/opsec"

if [ "$1" = "--uninstall" ]; then
  sudo rm -f "$DEST"
  echo "opsec removed."
  exit 0
fi

tmp=$(mktemp)
trap 'rm -f "$tmp"' EXIT

# a local checkout installs its own copy, otherwise download it
if [ -f "$(dirname "$0")/opsec" ] && [ "$0" != "bash" ]; then
  cp "$(dirname "$0")/opsec" "$tmp"
else
  curl -fsSL "$URL" -o "$tmp"
fi

echo "Installing opsec to $DEST (needs your password)..."
sudo mkdir -p "$(dirname "$DEST")"
sudo install -m 755 "$tmp" "$DEST"

echo
echo "Done. Run it with:  sudo opsec"
echo "Quit with Ctrl+C."
