"""Isolated real-window regression; argv[1] is the pinned HyprKwin checkout.

The test uses kwin_wayland on PATH, so it can check stock or the optional build.
Requires the upstream e2e harness and its dependencies; never drives host windows.
"""
from pathlib import Path
import os
import sys
import tempfile

sys.path.insert(0, str(Path(sys.argv[1]).resolve()/'tests/e2e'))
import sandbox
root = Path(__file__).resolve().parents[1]
sandbox.PACKAGE = root/'shell/kde/tiling/package'
sandbox.EFFECT_PACKAGE = root/'shell/kde/tiling/package-effect'
os.environ['WAYLAND_DISPLAY'] = 'velum-no-host-display'
os.environ.pop('DISPLAY', None)

class Isolated(sandbox.Sandbox):
    def _write_config(self, env, group, values, file='kwinrc'):
        if group == 'Plugins':
            values = dict(values, kwin_effect_plasmazonesEnabled='false',
                          kwin4_effect_shapecornersEnabled='false',
                          velum_resize_pacerEnabled='false', velum_resize_pacer_v2Enabled='true',
                          velum_chatgpt_resize_v2Enabled='true')
        super()._write_config(env, group, values, file)
        if group == 'Plugins':
            super()._write_config(env, 'Effect-velum_chatgpt_resize',
                                 {'DeferUntilRelease':'false', 'RedrawDivisor':'1'})

with tempfile.TemporaryDirectory(prefix='velum-edge-test-') as tmp:
    with Isolated(base=Path(tmp)/'session', width=1920, height=1080, effect=True,
                  config={'SplitWidthMultiplier':'4', 'PreserveSplit':'true',
                          'GapsIn':'2', 'GapsOut':'4'}) as sb:
        sb.spawn('A'); sb.spawn('B'); sb.invoke('focusLeft'); sb.spawn('C')
        sb.settle(1)
        original = sb.kwin_geometries()
        a, c, b = [original[n] for n in ('A', 'C', 'B')]
        assert a[0] < c[0] < b[0] and a[1] == c[1] == b[1], original
        fi = sb.input()
        for side, delta in [('right', 120), ('left', -80), ('right', -120), ('left', 80)]:
            before = sb.kwin_geometries()
            x, y, w, h = before['C']
            start = (x+w-15 if side == 'right' else x+15, y+h//2)
            fi.drag(start, (start[0]+delta, start[1]), btn=0x111, modifiers=('meta',))
            sb.settle(.8)
            after = sb.kwin_geometries()
            expected = (x, y, w+delta, h) if side == 'right' else (x+delta, y, w-delta, h)
            assert after['C'] == expected, (side, before, after, expected)
            untouched = 'A' if side == 'right' else 'B'
            assert after[untouched] == before[untouched], (side, before, after)
            print('PASS', side, 'drag:', before['C'], '->', after['C'], flush=True)
        assert sb.kwin_geometries() == original
    assert not sb.crashed(), 'Virtual KWin crashed'
print('PASS real nested-edge resizing and round-trip geometry')
