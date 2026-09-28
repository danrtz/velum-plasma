pragma Singleton
import QtQuick
import "."
QtObject {
readonly property string stateDir:NativeState.snapshot.state||""
readonly property string serpantinumDir:NativeState.snapshot.source||""
function getCacheDir(name){return (NativeState.snapshot.cache||"")+"/"+name}
function getRunDir(name){return (NativeState.snapshot.run||"")+"/"+name}
}
