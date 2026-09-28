#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later
"""Prefer an application's explicit new-window action when launching it."""
import os
import sys


def new_window_action(app):
    if app is None:
        return None
    return next((action for action in app.list_actions()
                 if action.lower().replace('-', '').replace('_', '') == 'newwindow'), None)


if __name__ == '__main__':
    desktop_id = sys.argv[1]
    try:
        import gi
        gi.require_version('GioUnix', '2.0')
        from gi.repository import GioUnix
        app = GioUnix.DesktopAppInfo.new(desktop_id if desktop_id.endswith('.desktop') else desktop_id + '.desktop')
        action = new_window_action(app)
    except (ImportError, ValueError, TypeError):
        action = None
    if action:
        app.launch_action(action, None)
    else:
        os.execlp('kstart', 'kstart', '--application', desktop_id)
