// SPDX-License-Identifier: AGPL-3.0-or-later
pragma Singleton
import QtQuick
import "../../"
QtObject {
 readonly property string appClass: KdeBackend.activeToplevel ? KdeBackend.activeToplevel.appId : ""
 readonly property string appTitle: KdeBackend.activeToplevel ? KdeBackend.activeToplevel.title : ""
 readonly property string displayText: appTitle || appClass
 readonly property bool isFocused: displayText !== ""
}
