pragma Singleton
import QtQuick
import "."
QtObject {readonly property var barLevels:NativeState.snapshot.cava||[];function registerConsumer(){} function unregisterConsumer(){}}
