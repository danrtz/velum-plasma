#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later
"""Local-only KDE shell installation with a complete, timestamped rollback."""
import argparse,datetime,json,os,shutil,subprocess,sys
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--restore',action='store_true');p.add_argument('--start',action='store_true');a=p.parse_args()
root=Path(__file__).resolve().parents[1];home=Path.home();data=home/'.local/share';config=home/'.config';state=home/'.local/state/velum-install';installed=data/'velum-shell'
state.mkdir(parents=True,exist_ok=True,mode=0o700)
def run(*args):return subprocess.run(list(map(str,args)),check=True)
def service(*args):return run('systemctl','--user',*args)
if a.restore:
 service('stop','velum.target')
 run(sys.executable,installed/'kde/tiling.py','--restore')
 run(sys.executable,installed/'kde/shortcuts.py','--restore')
 backup=Path((state/'last-backup').read_text().strip());manifest=json.loads((backup/'manifest.json').read_text())
 for path,saved in manifest.items():
  dest=Path(path)
  if saved:dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(backup/saved,dest)
  else:dest.unlink(missing_ok=True)
 service('daemon-reload');run('qdbus6','org.kde.KWin','/KWin','org.kde.KWin.reconfigure')
 service('restart','plasma-plasmashell.service','plasma-polkit-agent.service')
 (state/'last-backup').unlink()
 (state/'motion-preset').unlink(missing_ok=True)
 print('Restored the Plasma configuration from',backup);sys.exit()
for cmd in ('kpackagetool6','quickshell','qdbus6','kscreen-doctor','wl-paste','wl-copy','cliphist','matugen','ffmpeg','spectacle','satty','zbarimg','cava','jq','curl','magick','pactl','wpctl','nmcli','powerprofilesctl','sensors','inotifywait','notify-send','fc-query','kwriteconfig6','kreadconfig6','plasma-apply-colorscheme','gdbus','cmake','ninja'):
 if not shutil.which(cmd):raise SystemExit('Missing required program: '+cmd)
run(sys.executable,root/'kde/tiling.py','--check')
for project in ('lockscreen/native','kde/recorder'):
 build=state/'build'/project.replace('/','-');run('cmake','-S',root/project,'-B',build,'-G','Ninja');run('cmake','--build',build)
backup=state/'backups'/datetime.datetime.now().strftime('%Y%m%d-%H%M%S');backup.mkdir(parents=True,mode=0o700)
units=['velum.target','velum-shell.service','velum-bridge.service','velum-clipboard.service','velum-wellbeing.service']
files=[config/x for x in ['plasmashellrc','kdeglobals','kwinrc','kglobalshortcutsrc','autostart/velum.desktop']]+[config/'systemd/user'/x for x in units]
files+=[data/'color-schemes/Velum.colors',data/'applications/org.danrtz.velum.recorder.desktop']
manifest={}
for i,path in enumerate(files):
 if path.exists():name=str(i);shutil.copy2(path,backup/name);manifest[str(path)]=name
 else:manifest[str(path)]=None
(backup/'manifest.json').write_text(json.dumps(manifest))
# Updates get their own snapshot without replacing the original Plasma rollback.
if not (state/'last-backup').exists():(state/'last-backup').write_text(str(backup))
# Build/install all code locally. No network or publishing step.
if root!=installed:shutil.copytree(root,installed,dirs_exist_ok=True,ignore=shutil.ignore_patterns('__pycache__','*.pyc','lock-package','contents'))
(config/'velum').mkdir(exist_ok=True,mode=0o700)
if not (config/'velum/settings.json').exists():shutil.copy2(root/'config/serpantinum/settings.json',config/'velum/settings.json')
# KDE 6.7 gets its lock UI from the selected ShellPackage. Copy the installed
# stock package so native Plasma remains a usable fallback, then replace only the locker.
package=data/'plasma/shells/org.danrtz.velum';shutil.copytree('/usr/share/plasma/shells/org.kde.plasma.desktop',package,dirs_exist_ok=True)
locker=package/'contents/lockscreen'
if locker.exists():shutil.rmtree(locker)
shutil.copytree(installed/'lockscreen',locker,ignore=shutil.ignore_patterns('native'))
metadata=json.loads((package/'metadata.json').read_text());metadata['KPlugin']['Id']='org.danrtz.velum';metadata['KPlugin']['Name']='Velum';(package/'metadata.json').write_text(json.dumps(metadata))
# Papirus is an optional system/user package; the shell's Lucide controls are bundled.
if any((base/'Papirus-Dark/index.theme').exists() for base in [data/'icons',Path('/usr/share/icons')]):
 run('kwriteconfig6','--file','kdeglobals','--group','Icons','--key','Theme','Papirus-Dark')
# Apply the motion preset once; later installs preserve user adjustments.
if not (state/'motion-preset').exists():
 for effect in ('slide','scale','squash','maximize','fullscreen','slidingpopups'):
  run('kwriteconfig6','--file','kwinrc','--group','Plugins','--key',effect+'Enabled','true')
 for key,value in {'Duration':'200','InScale':'0.92','OutScale':'0.96'}.items():
  run('kwriteconfig6','--file','kwinrc','--group','Effect-scale','--key',key,value)
 for key,value in {'SlideInTime':'180','SlideOutTime':'140'}.items():
  run('kwriteconfig6','--file','kwinrc','--group','Effect-slidingpopups','--key',key,value)
 (state/'motion-preset').touch()
run('kwriteconfig6','--file','plasmashellrc','--group','Shell','--key','ShellPackage','org.danrtz.velum')
apps=data/'applications';apps.mkdir(exist_ok=True)
(apps/'org.danrtz.velum.recorder.desktop').write_text('[Desktop Entry]\nType=Application\nName=Velum Screen Recorder\nExec='+str(installed/'kde/velum-recorder')+'\nNoDisplay=true\nX-KDE-Wayland-Interfaces=zkde_screencast_unstable_v1\n')
bindir=home/'.local/bin';bindir.mkdir(exist_ok=True)
link=bindir/'velum'
if link.is_symlink():link.unlink()
if not link.exists():link.symlink_to(installed/'kde/velum')
unitdir=config/'systemd/user';unitdir.mkdir(parents=True,exist_ok=True)
(unitdir/'velum.target').write_text('[Unit]\nDescription=Velum desktop for KDE\nWants=velum-shell.service velum-bridge.service velum-clipboard.service velum-wellbeing.service\nAfter=plasma-workspace.target\nPartOf=plasma-workspace.target\n')
commands={'shell':str(installed/'kde/session.sh'),'bridge':'/usr/bin/python3 '+str(installed/'kde/bridge.py'),'clipboard':str(installed/'kde/clipboard.sh'),'wellbeing':'/usr/bin/bash '+str(installed/'src/quickshell/guide/wellbeing/launch_daemon.sh')}
for name,cmd in commands.items():
 extra='After=velum-bridge.service\nRequires=velum-bridge.service\n' if name=='shell' else ''
 recovery='ExecStopPost='+str(installed/'kde/recover.sh')+'\n' if name=='shell' else ''
 (unitdir/('velum-'+name+'.service')).write_text('[Unit]\nDescription=Velum '+name+'\nPartOf=velum.target plasma-workspace.target\nStartLimitIntervalSec=60\nStartLimitBurst=2\n'+extra+'\n[Service]\nType=simple\nExecStart='+cmd+'\n'+recovery+'Restart=on-failure\nRestartSec=3\nUMask=0077\nKillMode=mixed\nTimeoutStopSec=20\n')
(config/'autostart').mkdir(exist_ok=True)
(config/'autostart/velum.desktop').write_text('[Desktop Entry]\nType=Application\nName=Velum\nExec=systemctl --user start velum.target\nOnlyShowIn=KDE;\nX-KDE-autostart-phase=2\n')
run('kbuildsycoca6','--noincremental');service('daemon-reload')
run(sys.executable,installed/'kde/shortcuts.py')
run(sys.executable,installed/'kde/tiling.py')
if a.start:service('start','velum.target')
print('Installed locally. Restore with: velum restore\nBackup:',backup)
