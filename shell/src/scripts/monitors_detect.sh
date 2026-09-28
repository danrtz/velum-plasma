#!/usr/bin/env bash
mode=names
[[ "$1" == "-v" || "$1" == "--verbose" ]] && mode=verbose
exec python3 "$(dirname -- "${BASH_SOURCE[0]}")/../../kde/displays.py" "$mode"
