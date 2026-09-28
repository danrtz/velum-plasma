pragma Singleton
import QtQuick
import QtMultimedia
import "."
Item {
    id: root
    property var activeHandles: ({})
    property int nextId: 0
    readonly property var settings: Config.getSetting("general", {})
    Component {
        id: voice
        Item {
            id: holder
            property int handle
            property alias source: effect.source
            property alias volume: effect.volume
            property alias loops: effect.loops
            property int duration: 0
            SoundEffect {
                id: effect
                onStatusChanged: {
                    if (status === SoundEffect.Ready) play();
                    else if (status === SoundEffect.Error) root.stopSfx(holder.handle);
                }
                onPlayingChanged: if (!playing && status === SoundEffect.Ready) root.stopSfx(holder.handle)
            }
            Timer { running: holder.duration > 0; interval: holder.duration * 1000; onTriggered: root.stopSfx(holder.handle) }
        }
    }
    function play(path, volume, duration, loop) {
        if (!path || settings.muteSfx === true) return -1;
        let master=(settings.sfxVolume === undefined ? 100 : settings.sfxVolume)/100;
        let id=++nextId;
        let sound=voice.createObject(root,{handle:id,volume:Math.max(0,Math.min(1,(volume===undefined?1:volume)*master)),duration:duration||0,loops:loop?SoundEffect.Infinite:1});
        activeHandles[id]=sound;
        sound.source=path.startsWith("file://")?path:"file://"+path;
        return id;
    }
    function playSfx(path,volume,duration){return play(Caching.serpantinumDir+"/assets/sounds/"+path,volume,duration,false)}
    function playUntilStopped(path,volume,loop){return play(path.startsWith("/")?path:Caching.serpantinumDir+"/assets/sounds/"+path,volume,0,loop)}
    function stopSfx(id){let sound=activeHandles[id];if(sound){delete activeHandles[id];sound.destroy()}}
    function stopAllSfx(){for(let id in activeHandles)stopSfx(id)}
}
