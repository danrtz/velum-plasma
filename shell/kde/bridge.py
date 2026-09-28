#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later
"""KWin event bridge for the Serpantinum UI. Runtime state stays private and local."""
import json
import re
import os
from pathlib import Path
import signal
import subprocess
import sys
from PySide6.QtCore import QCoreApplication, QObject, Slot, QTimer, ClassInfo
from PySide6.QtDBus import QDBusConnection, QDBusServiceWatcher

ROOT = Path(__file__).resolve().parent
RUNTIME = Path(os.environ['XDG_RUNTIME_DIR']) / 'velum'
RUNTIME.mkdir(mode=0o700, exist_ok=True)
os.umask(0o077)


def dbus(*args):
    return subprocess.check_output(['qdbus6', *map(str,args)], text=True, timeout=5).strip()


def script(path, name):
    dbus('org.kde.KWin', '/Scripting', 'org.kde.kwin.Scripting.unloadScript', name)
    sid = dbus('org.kde.KWin', '/Scripting', 'org.kde.kwin.Scripting.loadScript', path, name)
    dbus('org.kde.KWin', '/Scripting/Script' + sid, 'org.kde.kwin.Script.run')


@ClassInfo(**{'D-Bus Interface': 'io.github.danrtz.Velum'})
class Bridge(QObject):
    def __init__(self):
        super().__init__()
        self.state = {}
        self.system = {'locked':False,'keyboardLayout':'US'}
        QTimer.singleShot(0,self.keyboardChanged)
        QTimer.singleShot(0,self.readLock)
        QTimer.singleShot(0,self.readNight)
        self.flush = QTimer(self)
        self.flush.setSingleShot(True)
        self.flush.setInterval(60)
        self.flush.timeout.connect(self.save)

    @Slot()
    def attach(self):
        # Plasma's desktop shell normally selects the initial activity.
        try:
            activity = ('org.kde.ActivityManager', '/ActivityManager/Activities')
            interface = 'org.kde.ActivityManager.Activities.'
            if not dbus(*activity, interface + 'CurrentActivity'):
                choices = dbus(*activity, interface + 'ListActivities').splitlines()
                if len(choices) == 1:
                    dbus(*activity, interface + 'SetCurrentActivity', choices[0])
        except subprocess.SubprocessError:
            pass
        try:
            script(ROOT / 'observer.js', 'velum-observer')
        except subprocess.SubprocessError:
            QTimer.singleShot(1000, self.attach)

    @Slot(str)
    def publish(self, payload):
        self.state = json.loads(payload)
        if not self.flush.isActive():
            self.flush.start()

    def save(self):
        temp = RUNTIME / 'kwin.tmp'
        temp.write_text(json.dumps(dict(self.state, **self.system)))
        temp.replace(RUNTIME / 'kwin.json')

    @Slot()
    @Slot('uint')
    def keyboardChanged(self, index=0):
        try:
            index = int(dbus('org.kde.keyboard','/Layouts','org.kde.KeyboardLayouts.getLayout'))
            labels = re.findall(r'"([^"\n]*)"',dbus('org.kde.keyboard','/Layouts','org.kde.KeyboardLayouts.getLayoutsList'))
            self.system['keyboardLayout'] = labels[index*3].upper() if len(labels)>index*3 else 'US'
            if self.state:self.save()
        except (ValueError,subprocess.SubprocessError):pass

    @Slot(bool)
    def lockedChanged(self, locked):
        self.system['locked'] = locked
        if self.state:self.save()

    def readLock(self):
        try:self.lockedChanged(dbus('org.freedesktop.ScreenSaver','/ScreenSaver','org.freedesktop.ScreenSaver.GetActive')=='true')
        except subprocess.SubprocessError:pass

    def readNight(self):
        try:
            values={}
            for line in dbus('org.kde.KWin','/org/kde/KWin/NightLight','org.freedesktop.DBus.Properties.GetAll','org.kde.KWin.NightLight').splitlines():
                key,_,value=line.partition(': ')
                if value in ('true','false'):values[key]=value=='true'
                elif value.isdigit():values[key]=int(value)
            self.system['nightLight']=values
            if self.state:self.save()
        except subprocess.SubprocessError:pass

    @Slot(str,'QVariantMap','QStringList')
    def nightChanged(self, interface, changed, invalidated):
        if interface=='org.kde.KWin.NightLight':self.readNight()

    @Slot(str, str, result=bool)
    def command(self, action, value):
        if action in ('workspace', 'moveWorkspace'):
            if not value.isdigit() or not 1 <= int(value) <= 100:
                return False
            for index in range(len(self.state.get('workspaces',[])),int(value)):
                dbus('org.kde.KWin','/VirtualDesktopManager','org.kde.KWin.VirtualDesktopManager.createDesktop',index,str(index+1))
            code = 'var d=workspace.desktops.find(d=>d.x11DesktopNumber===' + value + ');if(d){' + ('if(workspace.activeWindow)workspace.activeWindow.desktops=[d];' if action == 'moveWorkspace' else 'workspace.currentDesktop=d;') + '}'
        elif action in ('activate', 'close', 'minimize', 'move'):
            if value not in [w['id'] for w in self.state.get('windows',[])]:
                return False
            operation = {'activate':'w.minimized=false;workspace.activeWindow=w;', 'close':'w.closeWindow();',
                         'minimize':'w.minimized=true;', 'move':'w.desktops=[workspace.currentDesktop];'}[action]
            code = 'var w=workspace.windowList().find(w=>String(w.internalId)===' + json.dumps(value) + ');if(w){' + operation + '}'
        else:
            return False
        try:
            path = RUNTIME / 'command.js'
            path.write_text(code)
            script(path, 'velum-command')
            dbus('org.kde.KWin', '/Scripting', 'org.kde.kwin.Scripting.unloadScript', 'velum-command')
            return True
        except subprocess.SubprocessError:
            return False


app = QCoreApplication(sys.argv)
bus = QDBusConnection.sessionBus()
bridge = Bridge()
if not bus.registerService('io.github.danrtz.Velum'):
    raise SystemExit('Velum bridge is already running or the session bus is unavailable.')
bus.registerObject('/Bridge', bridge, QDBusConnection.ExportAllSlots)
bus.connect('org.freedesktop.ScreenSaver','/ScreenSaver','org.freedesktop.ScreenSaver','ActiveChanged',bridge,'1lockedChanged(bool)')
bus.connect('org.kde.keyboard','/Layouts','org.kde.KeyboardLayouts','layoutChanged',bridge,'1keyboardChanged(uint)')
bus.connect('org.kde.keyboard','/Layouts','org.kde.KeyboardLayouts','layoutListChanged',bridge,'1keyboardChanged()')
bus.connect('org.kde.KWin','/org/kde/KWin/NightLight','org.freedesktop.DBus.Properties','PropertiesChanged',bridge,'1nightChanged(QString,QVariantMap,QStringList)')
kwin_watch = QDBusServiceWatcher('org.kde.KWin', bus, QDBusServiceWatcher.WatchForRegistration)
kwin_watch.serviceRegistered.connect(lambda _: bridge.attach())
QTimer.singleShot(0, bridge.attach)
signal.signal(signal.SIGTERM, lambda *_: app.quit())
signal.signal(signal.SIGINT, lambda *_: app.quit())
# Let Python handle termination while Qt owns the event loop.
tick = QTimer();tick.timeout.connect(lambda:None);tick.start(1000)
def detach():
    try: dbus('org.kde.KWin','/Scripting','org.kde.kwin.Scripting.unloadScript','velum-observer')
    except subprocess.SubprocessError: pass  # KWin may already be gone at logout.
app.aboutToQuit.connect(detach)
app.exec()
