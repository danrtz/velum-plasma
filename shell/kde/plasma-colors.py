#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later
"""Apply the active shell palette to KDE apps, keeping the same color roles."""
import configparser,json,subprocess
from pathlib import Path
p=json.loads((Path.home()/'.local/state/velum/qs_colors.json').read_text())
def rgb(key):
 h=p[key].lstrip('#');return ','.join(str(int(h[i:i+2],16)) for i in (0,2,4))
c=configparser.ConfigParser();c.optionxform=str
c['General']={'Name':'Velum','ColorScheme':'Velum'}
for group,bg in [('Window','base'),('View','crust'),('Button','surface0'),('Tooltip','surface0'),('Complementary','mantle'),('Header','mantle'),('Selection','blue')]:
 fg='crust' if group=='Selection' else 'text'
 c['Colors:'+group]={'BackgroundNormal':rgb(bg),'BackgroundAlternate':rgb('surface1'),'ForegroundNormal':rgb(fg),'ForegroundInactive':rgb('subtext0'),'ForegroundActive':rgb('blue'),'ForegroundLink':rgb('blue'),'ForegroundVisited':rgb('mauve'),'ForegroundNegative':rgb('red'),'ForegroundNeutral':rgb('peach'),'ForegroundPositive':rgb('green'),'DecorationFocus':rgb('blue'),'DecorationHover':rgb('mauve')}
f=Path.home()/'.local/share/color-schemes/Velum.colors';f.parent.mkdir(parents=True,exist_ok=True)
with f.open('w') as stream:c.write(stream)
subprocess.run(['plasma-apply-colorscheme','Velum'],check=True)
