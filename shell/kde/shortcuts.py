#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later
import ast,json,re,subprocess,sys
from pathlib import Path
from PySide6.QtGui import QKeySequence
home=Path.home();state=home/'.local/state/velum-install/shortcuts.json';root=Path(__file__).resolve().parents[1]
def call(method,*args):
 out=subprocess.check_output(['gdbus','call','--session','--dest','org.kde.kglobalaccel','--object-path','/kglobalaccel','--method','org.kde.KGlobalAccel.'+method,*args],text=True)
 if out.strip() in ('(true,)','(false,)'):return out.strip()=='(true,)'
 return ast.literal_eval(re.sub(r'@[^ ]+ ', '',out))[0] if out.strip()!='()' else None
entries=[('launcher','Launcher','Meta+D,Meta+Space','toggle launcher'),('clipboard','Clipboard','Meta+V','toggle clipboard'),('settings','Settings','Meta+I','open guide'),('system','Quick Settings','Meta+A','toggle system'),('capture','Screenshot & Recording','Print','screenshot')]
if '--restore' in sys.argv:
 if state.exists():
  saved=json.loads(state.read_text())
  for component in saved['created']:call('unregister',component,'_launch');(home/'.local/share/applications'/(component)).unlink(missing_ok=True)
  for name in saved.get('actions',[]):call('unregister','kwin',name)
  for item in saved['previous']:call('setForeignShortcut',json.dumps(item['action']),str(item['keys']))
  state.unlink()
 sys.exit()
fresh=not state.exists()
if not fresh and not any(flag in sys.argv for flag in ['--update-launcher','--workspaces','--tiling-controls']):sys.exit() # Preserve user bindings.
saved=json.loads(state.read_text()) if state.exists() else {'created':[],'previous':[]}
if '--update-launcher' in sys.argv:entries=entries[:1]
if '--workspaces' in sys.argv or '--tiling-controls' in sys.argv:entries=[]
registered=[]
for name,title,shortcut,command in entries:
 component='org.danrtz.velum.'+name+'.desktop'
 for sequence in shortcut.split(','):
  key=QKeySequence(sequence)[0].toCombined();previous=call('action',str(key))
  if previous and previous[0]!=component:
   keys=call('shortcut',json.dumps(previous))
   if not any(item['action'][:2]==previous[:2] for item in saved['previous']):saved['previous'].append({'action':previous,'keys':keys})
   call('setForeignShortcut',json.dumps(previous),str([x for x in keys if x!=key]))
 entry=home/'.local/share/applications'/component
 entry.write_text('[Desktop Entry]\nType=Application\nName=Velum '+title+'\nExec='+str(root/'kde/velum')+' '+command+'\nIcon=preferences-desktop\nNoDisplay=true\nX-KDE-Shortcuts='+shortcut+'\n')
 if component not in saved['created']:saved['created'].append(component)
 registered.append(component)
if registered:subprocess.run(['kbuildsycoca6','--noincremental'],check=True)
# KGlobalAccel flags: SetPresent (2) | NoAutoloading (4).
for (name,title,shortcut,command),component in zip(entries,registered):
 action=[component,'_launch','Velum '+title,'Launch'];call('doRegister',json.dumps(action));call('setShortcut',json.dumps(action),str([QKeySequence(sequence)[0].toCombined() for sequence in shortcut.split(',')]),'6')
if fresh or '--workspaces' in sys.argv or '--tiling-controls' in sys.argv:
 def remember(action):
  if not any(item['action'][:2]==action[:2] for item in saved['previous']):saved['previous'].append({'action':action,'keys':call('shortcut',json.dumps(action))})
 bindings={}
 for i in range(1,11):
  bindings['VelumWorkspace'+str(i)]='Meta+'+str(i%10)
  bindings['VelumMoveWorkspace'+str(i)]='Meta+Shift+'+str(i%10)
 if fresh or '--tiling-controls' in sys.argv:
  bindings.update(json.loads((root/'kde/tiling/shortcuts.json').read_text()))
 for name,sequence in bindings.items():
  action=['kwin',name,'KWin',name];keys=[QKeySequence(sequence)[0].toCombined()] if sequence else []
  owner=call('action',str(keys[0])) if keys else None
  if owner and owner[:2]!=action[:2]:
   remember(owner);call('setForeignShortcut',json.dumps(owner),str([x for x in call('shortcut',json.dumps(owner)) if x not in keys]))
  native=not name.startswith(('Velum','HyprKwin '))
  if native:remember(action)
  elif name.startswith(('Velum','HyprKwin ')) and name not in saved.setdefault('actions',[]):saved['actions'].append(name)
  if native:keys=list(dict.fromkeys(call('shortcut',json.dumps(action))+keys))
  call('doRegister',json.dumps(action));call('setShortcut',json.dumps(action),str(keys),'6')
  state.write_text(json.dumps(saved))
state.write_text(json.dumps(saved))
