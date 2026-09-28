pragma Singleton
import QtQuick
import "."
QtObject {
readonly property var activePlayer: NativeState.snapshot.player?Object.assign({},NativeState.snapshot.player,{previous:()=>NativeState.action('previous',''),next:()=>NativeState.action('next',''),togglePlaying:()=>NativeState.action('togglePlaying','')}):null
readonly property string trackTitle:(NativeState.snapshot.media||{}).trackTitle||""
readonly property string trackArtist:(NativeState.snapshot.media||{}).trackArtist||""
readonly property string artUrl:(NativeState.snapshot.media||{}).artUrl||""
readonly property bool isPlaying:(NativeState.snapshot.media||{}).isPlaying||false
readonly property real livePosition:(NativeState.snapshot.media||{}).livePosition||0
}
