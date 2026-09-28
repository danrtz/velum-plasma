#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later
"""Install the pinned HyprKwin script and animation effect for Velum."""
import json,os,shutil,subprocess,sys,time
from pathlib import Path
root=Path(__file__).resolve().parent;home=Path.home()
data=Path(os.environ.get('XDG_DATA_HOME',home/'.local/share'))
config=Path(os.environ.get('XDG_CONFIG_HOME',home/'.config'))
state=Path(os.environ.get('XDG_STATE_HOME',home/'.local/state'))/'velum-install/tiling.json'
packages=[('Script','hyprkwin','package'),('Effect','hyprkwinanimations','package-effect')]
def run(*args):return subprocess.check_output(list(map(str,args)),text=True).strip()
def cfg(group,key,value):run('kwriteconfig6','--file',config/'kwinrc','--group',group,'--key',key,str(value).lower() if isinstance(value,bool) else str(value))
def kwin(path,method,*args):return run('qdbus6','org.kde.KWin',path,method,*args)
saved=json.loads(state.read_text()) if state.exists() else None
if saved and saved.get('backend')!='hyprkwin':
 raise SystemExit('A previous Velum tiler is configured. Restore it before installing HyprKwin.')
if '--restore' in sys.argv:
 if saved:
  for _,name,_ in packages:cfg('Plugins',name+'Enabled',False)
  kwin('/Scripting','org.kde.kwin.Scripting.unloadScript','hyprkwin')
  kwin('/Effects','org.kde.kwin.Effects.unloadEffect','hyprkwinanimations')
  for kind,name,_ in packages:
   if name in saved.get('owned',[]):run('kpackagetool6','--type=KWin/'+kind,'--remove',name)
  state.unlink()
 sys.exit()
if saved and saved.get('complete',True):
 for kind,name,_ in packages:
  if subprocess.run(['kpackagetool6','--type=KWin/'+kind,'--show',name],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL).returncode:
   raise SystemExit(name+' is missing; restore this installation before reinstalling.')
 print('HyprKwin is configured; keeping user settings.');sys.exit()
for name in ['tessera','polonium','krohnkite','bismuth','kwin_effect_plasmazones']:
 if run('kreadconfig6','--file',config/'kwinrc','--group','Plugins','--key',name+'Enabled')=='true':
  raise SystemExit('Disable the existing '+name+' tiler before installing HyprKwin.')
if not saved:
 for kind,name,_ in packages:
  if subprocess.run(['kpackagetool6','--type=KWin/'+kind,'--show',name],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL).returncode==0:
   raise SystemExit('An existing '+name+' installation is present; leaving it untouched.')
 if '--check' in sys.argv:sys.exit()
 backup=state.parent/('hyprkwin-'+str(time.time_ns()));backup.mkdir(parents=True,mode=0o700)
 for name in ['kwinrc','kglobalshortcutsrc']:
  if (config/name).exists():shutil.copy2(config/name,backup/name)
 saved={'backend':'hyprkwin','version':'0.12.2','backup':str(backup),'owned':[],'complete':False}
 state.write_text(json.dumps(saved))
if '--check' in sys.argv:sys.exit()
for kind,name,folder in packages:
 if name not in saved['owned']:
  run('kpackagetool6','--type=KWin/'+kind,'--install',root/'tiling'/folder)
  saved['owned'].append(name);state.write_text(json.dumps(saved))
for key,value in json.loads((root/'tiling/settings.json').read_text()).items():cfg('Script-hyprkwin',key,value)
for key,value in {'Duration':250,'Curve':3,'AnimateMove':True,'AnimateResize':True,'CrossFade':True,'OpenCloseEffect':0}.items():cfg('Effect-hyprkwinanimations',key,value)
for key,value in {'CommandAllKey':'Meta','CommandAll1':'Move','CommandAll3':'Resize'}.items():cfg('MouseBindings',key,value)
for _,name,_ in packages:cfg('Plugins',name+'Enabled',True)
kwin('/KWin','org.kde.KWin.reconfigure');kwin('/Scripting','org.kde.kwin.Scripting.start')
if kwin('/Scripting','org.kde.kwin.Scripting.isScriptLoaded','hyprkwin')!='true':raise SystemExit('HyprKwin did not start; use velum restore to roll back.')
loaded=kwin('/Effects','org.kde.kwin.Effects.isEffectLoaded','hyprkwinanimations')=='true'
if not loaded:loaded=kwin('/Effects','org.kde.kwin.Effects.loadEffect','hyprkwinanimations')=='true'
saved['complete']=True;state.write_text(json.dumps(saved,indent=2))
print('HyprKwin enabled; rollback snapshot:',saved['backup'])
if not loaded:print('Log out and back in once so KWin discovers the new animation effect.')
