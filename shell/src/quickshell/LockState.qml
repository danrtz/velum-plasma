// SPDX-License-Identifier: AGPL-3.0-or-later
import QtQuick
import Quickshell
import Quickshell.Io
import Quickshell.Services.UPower
Item {
    id: root
    property bool testing: false
    readonly property bool active: testing || !!KdeBackend.state.locked
    onActiveChanged: {
        if(active){SysData.subscribe();Cava.registerConsumer();publish()}
        else{SysData.unsubscribe();Cava.unregisterConsumer()}
    }
    function props(obj, names){let result={};names.forEach(n=>result[n]=obj[n]);return result}
    function publish(){
        let translations={};
        ["lock.default_user", "lock.power.power_off", "lock.power.reboot", "lock.power.suspend", "lock.status.access_denied", "lock.status.authenticating", "lock.status.enter_pin", "lock.status.locked", "music.nothing_playing", "quickactions.systemusage.cpu", "quickactions.systemusage.net", "quickactions.systemusage.ram", "quickactions.systemusage.temp", "syspanel.notifications.clear", "syspanel.notifications.empty", "syspanel.notifications.mute", "syspanel.notifications.silent", "syspanel.notifications.title"].forEach(k=>translations[k]=I18n.t(k));
        ['notifications.types.default.action','notifications.types.default.fallback_summary','notifications.types.screenshot.badge','notifications.types.screenshot.click_to_open','notifications.types.screenshot.fallback_summary','notifications.types.weather.fallback_body','notifications.types.weather.fallback_summary','notifications.types.weather.title'].forEach(k=>translations[k]=I18n.t(k));
        const player=MprisController.activePlayer;
        let groups=[];for(let i=0;i<NotificationManager.groupedHistory.count;i++) groups.push(props(NotificationManager.groupedHistory.get(i),['groupKey','displayName','icon','count','unreadCount','latestSummary','latestBody','latestTimestamp','itemsJson']));
        const data={
            source:Caching.serpantinumDir, cache:Caching.cacheDir, run:Caching.runDir, state:Caching.stateDir,
            theme:props(ThemeBackend, ['fontFamily','activeFontPath','borderRadius','clampedBorderRadius','base','mantle','crust','text','subtext0','subtext1','surface0','surface1','surface2','overlay0','overlay1','overlay2','blue','sapphire','peach','green','red','mauve','pink','yellow','maroon','teal']),
            config:{bar:Config.getSetting('bar',{}),general:props(Config.getSetting('general',{}),['uiScale','muteSfx','sfxVolume']),notifications:Config.getSetting('notifications',{})},
            user:props(SystemInfo,['username','avatarPath']),
            weather:props(Weather,['data','currentHex','currentIcon','currentTemp','currentTempFormatted','isLoading','isReady']),
            city:Location.city,translations:translations,
            stats:props(SysData,['cpu','diskGb','diskPercent','diskTotalGb','isScanningNet','netRx','netTx','ramGb','ramPercent','temp']),
            cava:Cava.barLevels, groups:groups,
            media:props(MprisController,['artUrl','trackTitle','trackArtist','isPlaying','livePosition']),
            player:player?props(player,['playbackState','trackTitle','length','canGoPrevious','canGoNext','canTogglePlaying']):null,
            kbLayout:KdeBackend.state.keyboardLayout,
            isDesktop:SystemInfo.isDesktop,
            batIcon:UPower.onBattery?'󰁹':'󰂄',batPercent:Math.round(UPower.displayDevice.percentage*100)+'%',batDynamicColor:ThemeBackend.text
        };
        output.setText(JSON.stringify(data));
    }
    FileView {id:output;path:Quickshell.env('XDG_RUNTIME_DIR')+'/velum/lock.json';preload:false;atomicWrites:true;printErrors:false}
    Timer {interval:100;repeat:true;running:root.active;onTriggered:root.publish()}
    IpcHandler {
        target:'lockState'
        function preview(enabled:bool):void {root.testing=enabled;root.publish()}
        function action(name:string,value:string):void {
            const p=MprisController.activePlayer;
            if(name==='keyboard')Quickshell.execDetached(['qdbus6','org.kde.keyboard','/Layouts','org.kde.KeyboardLayouts.switchToNextLayout']);
            else if(name==='clear')NotificationManager.clearNotifications();
            else if(name==='dismiss')NotificationManager.dismissNotification(Number(value));
            else if(name==='dismissGroup')NotificationManager.dismissGroup(value);
            else if(name==='setDnd'){let settings=Config.getSetting('notifications',{});settings.dnd=value==='true';Config.setSetting('notifications',settings)}
            else if(name==='markNotificationRead')NotificationManager.markAsRead(Number(value));
            else if(name==='notificationAction'){
                try {
                    const request=JSON.parse(value), notification=NotificationManager.liveNotifs[request.uid];
                    if(notification) {
                        const action=notification.actions.find(a=>a.identifier===request.action);
                        if(action)action.invoke();
                    }
                } catch(error) {console.warn('Notification action:',error)}
            }
            else if(name==='markRead')NotificationManager.markGroupRead(value);
            else if(name==='previous'&&p&&p.canGoPrevious)p.previous();
            else if(name==='next'&&p&&p.canGoNext)p.next();
            else if(name==='togglePlaying'&&p)p.togglePlaying();
            else if(name==='scanNetwork')SysData.scanNetwork();
            else if(name==='sound'&&!value.includes('..')&&!value.startsWith('/'))Sounds.playSfx(value);
        }
    }
}
