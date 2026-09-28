#!/usr/bin/env bash
set -e
umask 077
mkdir -p "${XDG_CACHE_HOME:-$HOME/.cache}/velum"
exec wl-paste --watch "$(dirname -- "$0")/bin/cliphist" store
