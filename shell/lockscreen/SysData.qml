pragma Singleton
import QtQuick
import "."
QtObject {
readonly property real cpu:(NativeState.snapshot.stats||{}).cpu||0
readonly property real diskGb:(NativeState.snapshot.stats||{}).diskGb||0
readonly property real diskPercent:(NativeState.snapshot.stats||{}).diskPercent||0
readonly property real diskTotalGb:(NativeState.snapshot.stats||{}).diskTotalGb||0
readonly property real netRx:(NativeState.snapshot.stats||{}).netRx||0
readonly property real netTx:(NativeState.snapshot.stats||{}).netTx||0
readonly property real ramGb:(NativeState.snapshot.stats||{}).ramGb||0
readonly property real ramPercent:(NativeState.snapshot.stats||{}).ramPercent||0
readonly property real temp:(NativeState.snapshot.stats||{}).temp||0
readonly property bool isScanningNet:(NativeState.snapshot.stats||{}).isScanningNet||false
function subscribe(){} function unsubscribe(){} function scanNetwork(){NativeState.action('scanNetwork','')}
}
