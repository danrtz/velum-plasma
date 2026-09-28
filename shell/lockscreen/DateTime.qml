pragma Singleton
import QtQuick
import "."
Item {property date now:new Date();readonly property bool is12Hour: ((Config.rawSettings.bar||{}).time||{}).format?.includes("h")??false;signal hourChanged();Timer{interval:1000;running:true;repeat:true;onTriggered:parent.now=new Date()}}
