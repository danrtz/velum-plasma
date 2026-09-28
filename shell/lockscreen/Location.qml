pragma Singleton
import QtQuick
import "."
QtObject {readonly property string city:NativeState.snapshot.city||""}
