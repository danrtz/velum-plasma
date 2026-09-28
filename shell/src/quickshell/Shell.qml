import QtQuick
import Quickshell

ShellRoot {
    readonly property bool performanceMode: !!(Config.getSetting("general", {}).performance)
    readonly property bool quickactionsEnabled: Config.getSetting("general", {}).quickactions !== false
    readonly property bool dockEnabled: Config.getSetting("dock", {}).enabled !== false

    Connections {
        target: Quickshell
        function onReloadCompleted() { Quickshell.inhibitReloadPopup() }
        function onReloadFailed(errorString) { Quickshell.inhibitReloadPopup() }
    }

    ScreenshotOverlay {}
    Main {}
    LockState {}
    Bar {}
    // KDE screen locking is provided by the native, separately themed locker.

    Launcher {}
    Clipboard {}    

    Loader { active: Quickshell.env("VELUM_PREVIEW") !== "1"; sourceComponent: Polkit {} }
    PopoutManager {}

    Loader {
        active: dockEnabled
        sourceComponent: Dock {}
    }

    Loader {
        active: !performanceMode && Quickshell.env("VELUM_PREVIEW") !== "1"
        sourceComponent: Idle {}
    }
    Variants {
        model: performanceMode ? [] : Quickshell.screens
        delegate: WidgetLoader {
            required property var modelData
            screen: modelData
            monitorName: modelData.name
        }
    }
    Loader {
        active: !performanceMode
        sourceComponent: WallpaperEngine {}
    }
    Loader {
        active: !performanceMode && quickactionsEnabled
        sourceComponent: Floating {}
    }

    Component.onCompleted: {
        if (Quickshell.env("VELUM_PREVIEW") !== "1") FirstLaunch.checkFirstLaunch();
    }
}
