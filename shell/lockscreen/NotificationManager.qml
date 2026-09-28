pragma Singleton
import QtQuick
import "."
Item {
readonly property var liveNotifs: {
    let result={};
    for (const group of NativeState.snapshot.groups || []) {
        let members=[];try{members=JSON.parse(group.itemsJson || "[]")}catch(e){}
        for (const member of members) {
            let actions=[];try{actions=JSON.parse(member.actionsJson || "[]")}catch(e){}
            const uid=member.uid;
            result[uid]={actions:actions.map(a=>({identifier:a.id,invoke:function(){NativeState.action('notificationAction',JSON.stringify({uid:uid,action:a.id}))}}))};
        }
    }
    return result;
}
property alias groupedHistory:groups
ListModel{id:groups}
property string serialized:JSON.stringify(NativeState.snapshot.groups||[])
onSerializedChanged:{groups.clear();for(const n of NativeState.snapshot.groups||[])groups.append(n)}
function dismissGroup(k){NativeState.action('dismissGroup',k)}
function dismissNotification(k){NativeState.action('dismiss',k)}
function markAsRead(k){NativeState.action('markNotificationRead',k)}
function markGroupRead(k){NativeState.action('markRead',k)}
}
