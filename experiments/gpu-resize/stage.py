#!/usr/bin/env python3
"""Stage a locally built, patched KWin 6.7.5; never change the live session."""
from pathlib import Path
import json
import re
import shutil
import subprocess
import sys
import tempfile

root = Path(__file__).resolve().parent
build = Path(sys.argv[1]).resolve()
packages = ['kwin', 'qt6-base', 'kdecoration']
versions = subprocess.check_output(['pacman', '-Q', *packages], text=True)
expected = 'kwin 6.7.5-1\nqt6-base 6.11.2-3\nkdecoration 6.7.5-1\n'
if versions != expected:
    raise SystemExit('Only the documented Arch package versions were validated.')
if b'KWIN_GPU_RESIZE_FPS' not in (build/'bin/libkwin.so.6.7.5').read_bytes():
    raise SystemExit('This build does not contain the GPU resize patch.')
plugin = root/'addon/build/plugins/kwin/effects/plugins/velum_chatgpt_resize_v2.so'
if not plugin.is_file():
    raise SystemExit('Build the required clipping addon first.')
runtime = root/'deploy/runtime'
if runtime.exists():
    raise SystemExit('Remove the old staging runtime deliberately before restaging.')
runtime.mkdir()
shutil.copy2(build/'bin/kwin_wayland', runtime/'kwin_wayland')
shutil.copy2(build/'bin/libkwin.so.6.7.5', runtime/'libkwin.so.6.7.5')
(runtime/'libkwin.so.6').symlink_to('libkwin.so.6.7.5')
binary = runtime/'kwin_wayland'
dynamic = subprocess.check_output(['readelf', '-d', str(binary)], text=True)
match = re.search(r'\((?:RUNPATH|RPATH)\).*\[(.*?)\]', dynamic)
if not match:
    raise SystemExit('Expected a build RPATH in the executable.')
def bracket(value):
    delim = '='
    while ']'+delim+']' in value: delim += '='
    return '['+delim+'['+value+']'+delim+']'
with tempfile.NamedTemporaryFile(mode='w', suffix='.cmake') as script:
    script.write('file(RPATH_CHANGE FILE '+bracket(str(binary))+' OLD_RPATH '+bracket(match[1])+' NEW_RPATH [[$ORIGIN]])\n')
    script.flush()
    subprocess.run(['cmake', '-P', script.name], check=True)
target = runtime/'kwin/effects/plugins'
target.mkdir(parents=True)
shutil.copy2(plugin, target/plugin.name)
(root/'deploy/manifest.json').write_text(json.dumps({
    'packages': packages, 'versions': versions, 'fps': 30, 'kwin': '6.7.5'
}, indent=2)+'\n')
subprocess.run([str(root/'deploy/bin/kwin_wayland'), '--velum-check'], check=True)
