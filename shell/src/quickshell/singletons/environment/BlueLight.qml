pragma Singleton
import QtQuick
import Quickshell
import Quickshell.Io
import "../../"

// KWin owns one persisted Night Light schedule for the whole session.
Item {
    id: root
    signal settingsChanged()
    readonly property var nativeState: KdeBackend.state.nightLight || ({})
    readonly property var saved: Config.getSetting("display", {})
    readonly property bool enabled: nativeState.enabled !== undefined ? nativeState.enabled : !!saved.enabled
    readonly property bool automatic: nativeState.mode !== undefined ? nativeState.mode !== 0 : !!saved.auto
    readonly property real temperature: saved.temperature !== undefined ? saved.temperature : 50
    property var pending: null
    onNativeStateChanged: settingsChanged()

    function isAnyEnabled() { return enabled; }
    function getSavedTemperature(monName) { return temperature; }
    function kelvinFromTemp(value) {
        return Math.round(Math.max(1000, Math.min(6500, value >= 1000 ? value : 6500 - value * 40)));
    }
    function change(key, value) {
        let next = pending || { enabled: enabled, auto: automatic, temperature: temperature };
        next[key] = value;
        pending = next;
        let settings = Object.assign({}, saved, next);
        // Keep old per-display preferences consistent for preset readers.
        for (let name in settings.monitors || {})
            settings.monitors[name] = Object.assign({}, settings.monitors[name], next);
        Config.setSetting("display", settings);
        debounce.restart();
        settingsChanged();
    }
    function setEnabled(monName, value) { change("enabled", value === undefined ? monName : value); }
    function setAuto(monName, value) { change("auto", value === undefined ? monName : value); }
    function setTemperature(monName, value) { change("temperature", Number(value === undefined ? monName : value)); }
    function applyPending() {
        if (!pending || runner.running) return;
        let next = pending;
        pending = null;
        runner.command = ["python3", Caching.serpantinumDir + "/../kde/nightlight.py"].concat(next.enabled
            ? ["set", String(kelvinFromTemp(next.temperature)), "all", next.auto ? "auto" : "manual"] : ["reset"]);
        runner.running = true;
    }
    Timer { id: debounce; interval: 120; onTriggered: root.applyPending() }
    Process {
        id: runner
        stderr: StdioCollector {}
        onExited: function(code) {
            if (code !== 0) Quickshell.execDetached(["notify-send", "Night Light", "KDE could not apply the setting."]);
            root.applyPending();
        }
    }
}
