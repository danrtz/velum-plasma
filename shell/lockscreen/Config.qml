pragma Singleton
import QtQuick
import "."
QtObject {
readonly property var rawSettings:NativeState.snapshot.config||{}
signal settingsLoaded()
onRawSettingsChanged: settingsLoaded()
function setSetting(key,value){if(key==="notifications" && typeof value.dnd === "boolean") NativeState.action("setDnd",String(value.dnd))}
function getSetting(key,fallback){return rawSettings[key]??fallback}
}
