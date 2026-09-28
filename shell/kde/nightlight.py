#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later
import subprocess,sys

def setting(key,value):subprocess.run(['kwriteconfig6','--file','kwinrc','--group','NightColor','--key',key,'--notify',str(value)],check=True)
if sys.argv[1]=='reset':setting('Active','false')
elif sys.argv[1]=='set':
 temperature=max(1000,min(6500,int(sys.argv[2])))
 auto=len(sys.argv)>4 and sys.argv[4]=='auto'
 setting('NightTemperature',temperature);setting('Mode',1 if auto else 0)
 setting('Active','true')
else:raise SystemExit('Unknown night light action')
subprocess.run(['qdbus6','org.kde.KWin','/KWin','org.kde.KWin.reconfigure'],check=True)
