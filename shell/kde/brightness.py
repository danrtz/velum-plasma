#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later
import subprocess,sys

def call(*args):return subprocess.check_output(['qdbus6',*args],text=True,timeout=5).strip()
service='org.kde.ScreenBrightness';root='/org/kde/ScreenBrightness';interface=service+'.Display'
def prop(path,key):return int(call(service,path,'org.freedesktop.DBus.Properties.Get',interface,key))
action=sys.argv[1] if len(sys.argv)>1 else 'get'
if action=='watch':
 import os
 os.execvp('dbus-monitor',['dbus-monitor','--session',"type='signal',interface='org.kde.ScreenBrightness',member='BrightnessChanged'"])
if action=='backend':print('kde');raise SystemExit
names=call(service,root,'org.freedesktop.DBus.Properties.Get',service,'DisplaysDBusNames').splitlines()
if not names:raise SystemExit('No brightness-capable display')
paths=[root+'/'+name for name in names]
if action=='get':print(round(100*prop(paths[0],'Brightness')/max(1,prop(paths[0],'MaxBrightness'))))
elif action in ('set','raise','lower'):
 for path in paths:
  maximum=prop(path,'MaxBrightness');current=100*prop(path,'Brightness')/max(1,maximum)
  value=float(sys.argv[2]) if action=='set' else current+(5 if action=='raise' else -5)
  target=round(maximum*max(0,min(100,value))/100)
  call(service,path,interface+'.SetBrightness',str(target),'0')
else:raise SystemExit('Unknown brightness action')
