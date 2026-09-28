// SPDX-License-Identifier: AGPL-3.0-or-later
pragma Singleton
import QtQuick
QtObject {
    readonly property string localVersion: "2.1.10 · KDE local port"
    readonly property string remoteVersion: ""
    readonly property bool updateAvailable: false
    readonly property bool isChecking: false
    function checkUpdate() {} // No release endpoint until the owner publishes this port.
}
