#!/usr/bin/env bash
set -e
umask 077
export SERPANTINUM_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/src" && pwd)"
export PATH="$(dirname -- "$SERPANTINUM_DIR")/kde/bin:$PATH"
source "$SERPANTINUM_DIR/scripts/caching.sh"
exec /usr/bin/quickshell --no-duplicate --path "$MAIN_QML" "$@"
