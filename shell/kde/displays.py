#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later
import json,subprocess,sys
outputs=json.loads(subprocess.check_output(['kscreen-doctor','-j'],text=True))['outputs']
rows=[]
for o in outputs:
 if not o['connected']:continue
 m=next((m for m in o['modes'] if m['id']==o['currentModeId']),o['modes'][0])
 rows.append(dict(name=o['name'],width=m['size']['width'],height=m['size']['height'],refreshRate=m['refreshRate'],scale=o['scale'],disabled=not o['enabled'],x=o['pos']['x'],y=o['pos']['y']))
if len(sys.argv)==1:print(json.dumps(rows))
elif sys.argv[1]=='names':print('\n'.join(r['name'] for r in rows))
elif sys.argv[1]=='verbose':print('\n'.join(f"{r['name']}|{r['width']}x{r['height']}|{r['refreshRate']:.2f}" for r in rows))
elif sys.argv[1]=='power':
 name=sys.argv[2];enabled=sys.argv[3]=='true'
 if name not in [r['name'] for r in rows]:raise SystemExit('Unknown display')
 if not enabled and sum(not r['disabled'] for r in rows)<2:raise SystemExit('Cannot disable the last display')
 subprocess.run(['kscreen-doctor',f"output.{name}.{'enable' if enabled else 'disable'}"],check=True)
elif sys.argv[1]=='mode':
 name,mode,scale=sys.argv[2:5]
 output=next(o for o in outputs if o['name']==name)
 # Match a supported mode, including fractional refresh rates rounded in the original UI.
 size,rate=mode.split('@');width,height=map(int,size.split('x'))
 matches=[m for m in output['modes'] if m['size']==dict(width=width,height=height)]
 selected=min(matches,key=lambda m:abs(m['refreshRate']-float(rate)))
 if abs(selected['refreshRate']-float(rate))>1 or not .5<=float(scale)<=4:raise SystemExit('Unsupported mode or scale')
 subprocess.run(['kscreen-doctor',f"output.{name}.mode.{selected['id']}",f'output.{name}.scale.{float(scale)}'],check=True)
