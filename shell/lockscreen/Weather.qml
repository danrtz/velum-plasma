pragma Singleton
import QtQuick
import "."
QtObject {
readonly property var data:(NativeState.snapshot.weather||{}).data??{}
readonly property color currentHex:(NativeState.snapshot.weather||{}).currentHex??"#83d2e5"
readonly property string currentIcon:(NativeState.snapshot.weather||{}).currentIcon??""
readonly property string currentTemp:(NativeState.snapshot.weather||{}).currentTemp??""
readonly property string currentTempFormatted:(NativeState.snapshot.weather||{}).currentTempFormatted??""
readonly property bool isLoading:(NativeState.snapshot.weather||{}).isLoading??false
readonly property bool isReady:(NativeState.snapshot.weather||{}).isReady??false
}
