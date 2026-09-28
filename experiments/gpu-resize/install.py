"""Install without restarting KWin or altering distribution-owned binaries."""
from pathlib import Path
import subprocess,shutil,time,json,re
root=Path(__file__).resolve().parent;home=Path.home();dest=home/'.local/lib/velum-kwin-resize'
check=json.loads(subprocess.check_output([str(root/'deploy/bin/kwin_wayland'),'--velum-check'],text=True))
if not check['custom']:
    raise SystemExit('Stage a complete matching build first: '+check['reason'])
config=home/'.config/systemd/user/plasma-kwin_wayland.service.d/90-velum-resize.conf'
contents=home/'.local/share/kwin/scripts/hyprkwin/contents'
old=subprocess.check_output(['kreadconfig6','--file','kwinrc','--group','Script-hyprkwin','--key','BuildId'],text=True).strip()
assert re.fullmatch(r'[0-9]+',old),old
new=str(time.time_ns());oldbuild=contents/('build-'+old);newbuild=contents/('build-'+new)
assert oldbuild.is_dir()
assert not dest.exists(),'Existing installation requires deliberate update'
assert not config.exists(),'Existing override requires deliberate update'
state=home/'.local/state/velum-install'/('gpu-resize-'+new);state.mkdir(parents=True)
shutil.copy2(home/'.config/kwinrc',state/'kwinrc')
shutil.copytree(root/'deploy',dest)
shutil.copytree(oldbuild,newbuild)
p=newbuild/'code/driver.js';s=p.read_text()
a='            slideHold: Math.max(0, num(rc("SlideHold", 220), 220)),'
b='                var r = st.hold || w.frameGeometry, b = cfg.borderSize;'
assert s.count(a)==1 and s.count(b)==1
s=s.replace(a,a+'\n            gpuResizePreview: bool(rc("GpuResizePreview", false), false),')
s=s.replace(b,b+'\n                if (cfg.gpuResizePreview && drag && drag.mode === "resize" && isTiled(st))\n                    r = (drag.st === st ? drag.last : st.placed) || r;');p.write_text(s)
# Select only the new tiler build; it loads with the next compositor session.
subprocess.run(['kwriteconfig6','--file','kwinrc','--group','Script-hyprkwin','--key','BuildId',new],check=True)
# The addon supplies the required transformed-window clipping correction.
# Do not enable the rejected hold/stretch mode or extra app throttling.
for group,key,value in [('Plugins','velum_chatgpt_resize_v2Enabled','true'),
                        ('Effect-velum_chatgpt_resize','DeferUntilRelease','false'),
                        ('Effect-velum_chatgpt_resize','RedrawDivisor','1')]:
    subprocess.run(['kwriteconfig6','--file','kwinrc','--group',group,'--key',key,value],check=True)
config.parent.mkdir(parents=True,exist_ok=True)
config.write_text('[Service]\nExecStart=\nExecStart='+str(dest/'start-session')+' --xwayland\n')
info={'old_build':old,'new_build':new,'backup':str(state),'override':str(config),'installed':str(dest)}
(state/'installation.json').write_text(json.dumps(info,indent=2));(dest/'installation.json').write_text(json.dumps(info,indent=2))
rollback=dest/'disable'
rollback.write_text('''#!/usr/bin/python
from pathlib import Path
import json,subprocess
root=Path(__file__).resolve().parent
info=json.loads((root/'installation.json').read_text())
(root/'disabled').touch()
Path(info['override']).unlink(missing_ok=True)
current=subprocess.check_output(['kreadconfig6','--file','kwinrc','--group','Script-hyprkwin','--key','BuildId'],text=True).strip()
if current==info['new_build']:
 subprocess.run(['kwriteconfig6','--file','kwinrc','--group','Script-hyprkwin','--key','BuildId',info['old_build']],check=True)
subprocess.run(['kwriteconfig6','--file','kwinrc','--group','Script-hyprkwin','--key','GpuResizePreview','false'],check=True)
subprocess.run(['systemctl','--user','daemon-reload'],check=True)
print('Stock KWin selected for the next login; the current session was not restarted.')
''');rollback.chmod(0o755)
subprocess.run(['systemctl','--user','daemon-reload'],check=True)
subprocess.run([str(dest/'bin/kwin_wayland'),'--velum-check'],check=True)
print(json.dumps(info,indent=2))
