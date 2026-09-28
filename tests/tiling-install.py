"""Real KWin integration check; pass a HyprKwin source checkout as argv[1]."""
import json,os,subprocess,sys
from pathlib import Path
sys.path.insert(0,str(Path(sys.argv[1]).resolve()/'tests/e2e'))
from sandbox import Sandbox
root=Path(__file__).resolve().parents[1]
with Sandbox(base='/tmp/velum-tiling-install-test',effect=True) as sb:
 home=sb.base/'home';home.mkdir();(home/'.config').symlink_to(sb.base/'config');(home/'.local').mkdir();(home/'.local/share').symlink_to(sb.base/'data');(home/'.local/state/velum-install').mkdir(parents=True);(sb.base/'data/applications').mkdir(exist_ok=True)
 env=dict(sb.env,HOME=str(home),XDG_STATE_HOME=str(home/'.local/state'))
 def run(*a):return subprocess.check_output(list(map(str,a)),env=env,text=True,stderr=subprocess.STDOUT,timeout=60).strip()
 def q(path,method,*a):return run('qdbus6','org.kde.KWin',path,method,*a)
 for name in ['hyprkwin','hyprkwinanimations']:run('kwriteconfig6','--file','kwinrc','--group','Plugins','--key',name+'Enabled','false')
 q('/Scripting','org.kde.kwin.Scripting.unloadScript','hyprkwin');q('/Effects','org.kde.kwin.Effects.unloadEffect','hyprkwinanimations')
 for kind,name in [('Script','hyprkwin'),('Effect','hyprkwinanimations')]:run('kpackagetool6','--type=KWin/'+kind,'--remove',name)
 # Remove the harness's registrations to model a genuinely fresh install.
 for name in json.loads((root/'shell/kde/tiling/shortcuts.json').read_text()):
  run('gdbus','call','--session','--dest','org.kde.kglobalaccel','--object-path','/kglobalaccel','--method','org.kde.KGlobalAccel.unregister','kwin',name)
 # Use the same ordering as the main installer: shortcuts before activation.
 for script in ['shortcuts.py','tiling.py']:print(run(sys.executable,root/'shell/kde'/script),flush=True)
 assert q('/Scripting','org.kde.kwin.Scripting.isScriptLoaded','hyprkwin')=='true'
 assert q('/Effects','org.kde.kwin.Effects.isEffectLoaded','hyprkwinanimations')=='true'
 for n in ['A','B','C']:sb.spawn(n)
 assert sum(sb.geometry(n)[2]*sb.geometry(n)[3] for n in ['A','B','C'])>1920*1080*.85
 sb.invoke('toggleFloating');sb.invoke('toggleFloating');before=sb.geometry('C');sb.invoke('toggleSplit');assert sb.geometry('C')!=before
 print('PASS fresh install, tile area, floating and split rotation',flush=True)
 from PySide6.QtGui import QKeySequence
 import ast,re
 def accel(method,*a):
  text=run('gdbus','call','--session','--dest','org.kde.kglobalaccel','--object-path','/kglobalaccel','--method','org.kde.KGlobalAccel.'+method,*a)
  return ast.literal_eval(re.sub(r'@[^ ]+ ','',text))[0]
 for name,key in json.loads((root/'shell/kde/tiling/shortcuts.json').read_text()).items():
  if key:assert accel('action',str(QKeySequence(key)[0].toCombined()))[:2]==['kwin',name]
  else:assert not accel('shortcut',json.dumps(['kwin',name,'KWin',name]))
 print('PASS shortcut ownership and unbound defaults',flush=True)
 run('kwriteconfig6','--file','kwinrc','--group','Script-hyprkwin','--key','GapsOut','13')
 print(run(sys.executable,root/'shell/kde/tiling.py'),flush=True)
 assert run('kreadconfig6','--file','kwinrc','--group','Script-hyprkwin','--key','GapsOut')=='13'
 saved=json.loads((home/'.local/state/velum-install/shortcuts.json').read_text())
 for script in ['tiling.py','shortcuts.py']:run(sys.executable,root/'shell/kde'/script,'--restore')
 assert q('/Scripting','org.kde.kwin.Scripting.isScriptLoaded','hyprkwin')=='false'
 assert q('/Effects','org.kde.kwin.Effects.isEffectLoaded','hyprkwinanimations')=='false'
 for item in saved['previous']:
  actual=accel('shortcut',json.dumps(item['action']));assert actual==item['keys'],(item['action'],item['keys'],actual)
 assert not (home/'.local/state/velum-install/tiling.json').exists()
 print('PASS repeat installation preserves settings; rollback restores previous shortcuts',flush=True)
assert not sb.crashed(),'KWin crashed during teardown'
