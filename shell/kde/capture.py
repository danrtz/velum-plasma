#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later
"""Grim-compatible capture entry point backed by KDE Spectacle."""
import argparse,json,os,re,subprocess,tempfile,time
from pathlib import Path
from PySide6.QtGui import QImage
p=argparse.ArgumentParser();p.add_argument('-o',dest='monitor');p.add_argument('-g',dest='region');p.add_argument('-l',default='0');p.add_argument('target');a=p.parse_args()
state=json.loads((Path(os.environ['XDG_RUNTIME_DIR'])/'velum/kwin.json').read_text());screens=state['screens']
x0=min(s['x'] for s in screens);y0=min(s['y'] for s in screens)
x1=max(s['x']+s['width'] for s in screens);y1=max(s['y']+s['height'] for s in screens)
with tempfile.TemporaryDirectory(prefix='velum-capture-',dir=os.environ['XDG_RUNTIME_DIR']) as tmp:
 capture=Path(tmp)/'screen.png'
 subprocess.run(['spectacle','-b','-n','-f','--scaled','-o',str(capture)],check=True,timeout=20)
 deadline=time.monotonic()+15
 while time.monotonic()<deadline:
  if capture.exists() and capture.read_bytes()[-8:-4]==b'IEND':break
  time.sleep(.05)
 image=QImage(str(capture))
 if image.isNull():raise SystemExit('KDE returned an empty capture')
 region=None
 if a.region:
  match=re.fullmatch(r'(-?\d+),(-?\d+) (\d+)x(\d+)',a.region)
  if not match:raise SystemExit('Invalid region')
  region=list(map(int,match.groups()))
 elif a.monitor:
  screen=next(s for s in screens if s['name']==a.monitor)
  region=[screen[k] for k in ('x','y','width','height')]
 if region:
  x,y,w,h=region;sx=image.width()/(x1-x0);sy=image.height()/(y1-y0)
  image=image.copy(round((x-x0)*sx),round((y-y0)*sy),round(w*sx),round(h*sy))
 if not image.save(a.target):raise SystemExit('Could not save capture')
