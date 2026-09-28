// SPDX-License-Identifier: AGPL-3.0-or-later
pragma Singleton
import QtQuick
import Quickshell
import Quickshell.Io

Item {
    id: root
    property var state: ({windows: [], workspaces: [], screens: [], current: 1, active: "", activeScreen: ""})
    readonly property var activeToplevel: {
        const w = state.windows.find(w => w.id === state.active);
        return w ? Object.assign({}, w, {screens: Quickshell.screens.filter(s => s.name === w.screen)}) : null;
    }
    readonly property var workspaces: ({values: state.workspaces.map(d => Object.assign({}, d, {
        toplevels: {values: state.windows.filter(w => w.workspaces.length === 0 || w.workspaces.includes(d.id))},
        hasFullscreen: state.windows.some(w => w.fullscreen && w.workspaces.includes(d.id)),
        monitor: {name: state.activeScreen}
    }))})
    readonly property var focusedWorkspace: workspaces.values.find(w => w.id === state.current) || null
    readonly property var focusedMonitor: ({name:state.activeScreen, activeWorkspace:focusedWorkspace})
    readonly property var monitors: ({values:state.screens.map(s => Object.assign({},s,{activeWorkspace:focusedWorkspace}))})
    function command(action, value) {
        Quickshell.execDetached(["qdbus6","io.github.danrtz.Velum","/Bridge","io.github.danrtz.Velum.command",action,String(value)]);
    }
    function dispatch(value) {
        const match = value.match(/workspace\s*=\s*(\d+)/);
        if (match) command("workspace",match[1]);
    }
    FileView {
        path: Quickshell.env("XDG_RUNTIME_DIR") + "/velum/kwin.json"
        watchChanges: true
        onFileChanged: reload()
        onLoaded: { try { root.state = JSON.parse(text()); } catch (error) { console.warn("KWin state:",error); } }
    }
}
