#!/usr/bin/env bash
# Restore KDE if Velum stops. A brief deferred check avoids starting and killing
# plasmashell during a normal Velum restart (which can race Qt icon loading).
set -e
if [[ "${1:-}" != --now ]]; then
    systemctl --user unmask --runtime plasma-plasmashell.service plasma-polkit-agent.service
    systemctl --user stop velum-recover.timer 2>/dev/null || true
    exec systemd-run --user --quiet --collect --unit=velum-recover --on-active=2 --timer-property=AccuracySec=100ms "$(readlink -f "$0")" --now
fi
case "$(systemctl --user show velum-shell.service -p ActiveState --value)" in
    active|activating|reloading) exit 0 ;;
esac
if systemctl --user is-active --quiet plasma-workspace.target; then
    systemctl --user unmask --runtime plasma-plasmashell.service plasma-polkit-agent.service
    systemctl --user start --no-block plasma-plasmashell.service plasma-polkit-agent.service
fi
