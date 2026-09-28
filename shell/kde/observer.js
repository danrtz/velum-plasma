// SPDX-License-Identifier: AGPL-3.0-or-later
// KWin publishes events; there is no polling loop inside the compositor.
function snapshot() {
    const windows = workspace.windowList().filter(w => w.normalWindow && !w.skipTaskbar && !w.skipPager && String(w.resourceClass) !== "quickshell").map(w => ({
        id: String(w.internalId), appId: String(w.desktopFileName || w.resourceClass),
        title: String(w.caption), activated: w === workspace.activeWindow,
        fullscreen: w.fullScreen, minimized: w.minimized,
        workspaces: w.desktops.map(d => d.x11DesktopNumber),
        screen: w.output ? w.output.name : "",
        geometry: {x:w.frameGeometry.x,y:w.frameGeometry.y,width:w.frameGeometry.width,height:w.frameGeometry.height}
    }));
    const state = {
        workspaces: workspace.desktops.map(d => ({id:d.x11DesktopNumber,uuid:d.id,name:d.name})),
        current: workspace.currentDesktop.x11DesktopNumber,
        active: workspace.activeWindow ? String(workspace.activeWindow.internalId) : "",
        windows: windows,
        screens: workspace.screens.map(s => ({name:s.name,x:s.geometry.x,y:s.geometry.y,width:s.geometry.width,height:s.geometry.height})),
        activeScreen: workspace.activeScreen ? workspace.activeScreen.name : ""
    };
    callDBus("io.github.danrtz.Velum", "/Bridge", "io.github.danrtz.Velum", "publish", JSON.stringify(state));
}
function watch(w) {
    for (const name of ["captionChanged", "fullScreenChanged", "minimizedChanged", "desktopsChanged", "outputChanged"])
        if (w[name]) w[name].connect(snapshot);
}
workspace.windowList().forEach(watch);
workspace.windowAdded.connect(w => {watch(w);snapshot();});
workspace.windowRemoved.connect(snapshot);
workspace.windowActivated.connect(snapshot);
workspace.currentDesktopChanged.connect(snapshot);
workspace.desktopsChanged.connect(snapshot);
workspace.screensChanged.connect(snapshot);
snapshot();

// Match Serpantinum: create desktops on demand and follow a moved window.
for (let n = 1; n <= 10; n++) {
    for (const move of [false, true]) {
        registerShortcut("Velum" + (move ? "MoveWorkspace" : "Workspace") + n,
            "Velum: " + (move ? "Move to desktop " : "Desktop ") + n, "", () => {
                const window = workspace.activeWindow;
                if (move && !window) return;
                while (workspace.desktops.length < n) workspace.createDesktop(workspace.desktops.length, String(workspace.desktops.length + 1));
                const desktop = workspace.desktops[n - 1];
                if (move) window.desktops = [desktop];
                workspace.currentDesktop = desktop;
                if (move) workspace.activeWindow = window;
            });
    }
}
