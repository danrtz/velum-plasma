#!/usr/bin/env bash
# SPDX-License-Identifier: AGPL-3.0-or-later
set -u
root="$(cd -- "$(dirname -- "$0")/.." && pwd)"
[[ "${XDG_CURRENT_DESKTOP:-}" == *KDE* ]] || exit 0
cleanup() { "$root/kde/recover.sh" || true; }
trap cleanup EXIT
systemctl --user mask --runtime --now plasma-plasmashell.service plasma-polkit-agent.service || exit 1
"$root/run.sh" &
shell_pid=$!
trap 'kill -TERM "$shell_pid" 2>/dev/null; wait "$shell_pid"; exit 0' TERM INT
wait "$shell_pid"
exit $?
