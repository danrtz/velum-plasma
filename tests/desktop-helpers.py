"""Regression checks without starting apps or changing the desktop."""
import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import runpy
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('launch_app', ROOT/'shell/src/quickshell/launcher/launch_app.py')
launcher = importlib.util.module_from_spec(spec)
spec.loader.exec_module(launcher)

class DesktopHelpers(unittest.TestCase):
    def test_missing_and_single_window_apps(self):
        self.assertIsNone(launcher.new_window_action(None))
        class App:
            def list_actions(self): return ['preferences', 'new-private-window']
        self.assertIsNone(launcher.new_window_action(App()))

    def test_explicit_new_window_action(self):
        class App:
            def list_actions(self): return ['new-private-window', 'New_Window', 'quit']
        self.assertEqual(launcher.new_window_action(App()), 'New_Window')

    def test_selector_fallbacks(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            script = root/'bin/kwin_wayland'
            script.parent.mkdir()
            shutil.copy2(ROOT/'experiments/gpu-resize/deploy/bin/kwin_wayland', script)
            for name in ['kwin_wayland', 'libkwin.so.6', 'kwin/effects/plugins/velum_chatgpt_resize_v2.so']:
                p = root/'runtime'/name
                p.parent.mkdir(parents=True, exist_ok=True)
                p.touch()
            versions = 'kwin 6.7.5-1\nqt6-base 6.11.2-3\nkdecoration 6.7.5-1\n'
            manifest = root/'manifest.json'
            manifest.write_text(json.dumps({'packages':['kwin','qt6-base','kdecoration'], 'versions':versions, 'fps':30}))
            def check(custom, output=versions, restart='0'):
                buf = io.StringIO()
                with patch.object(sys, 'argv', [str(script), '--velum-check']), \
                     patch.dict(os.environ, {'KWIN_RESTART_COUNT':restart}), \
                     patch('subprocess.run', return_value=subprocess.CompletedProcess([], 0, output)), \
                     contextlib.redirect_stdout(buf), self.assertRaises(SystemExit) as end:
                    runpy.run_path(str(script), run_name='__main__')
                self.assertEqual(end.exception.code, 0)
                result = json.loads(buf.getvalue())
                self.assertEqual(result['custom'], custom, result)
                if not custom: self.assertEqual(result['executable'], '/usr/bin/kwin_wayland')
            check(True)
            check(False, output=versions.replace('6.7.5-1', '6.7.6-1'))
            check(False, restart='1')
            (root/'disabled').touch(); check(False); (root/'disabled').unlink()
            plugin = root/'runtime/kwin/effects/plugins/velum_chatgpt_resize_v2.so'
            plugin.unlink(); check(False); plugin.touch()
            manifest.write_text('{}'); check(False)
            manifest.write_text('[]'); check(False)
            manifest.write_text('{'); check(False)
            manifest.unlink(); check(False)

if __name__ == '__main__': unittest.main()
