"""The compatibility page names the decompilation this checkout pins, and the generator refuses to publish by accident."""

from pathlib import Path
import os
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]


class EngineTree(unittest.TestCase):
    def test_the_page_names_the_pinned_decompilation(self):
        pin = subprocess.run(['git', 'rev-parse', '--short=7', 'HEAD:decomp'], cwd=ROOT, capture_output=True,
                             text=True, check=True).stdout.strip()
        self.assertIn(f'`{pin}`', (ROOT / 'docs/mods/compatibility.md').read_text())

    def test_pushing_needs_the_publish_switch(self):
        env = {k: v for k, v in os.environ.items() if k != 'DW1H_PUBLISH'}
        run = subprocess.run([str(ROOT / 'tools/engine_tree.sh'), 'push', 'v0', 'nowhere'], env=env, capture_output=True,
                             text=True)
        self.assertEqual(run.returncode, 1)
        self.assertIn('DW1H_PUBLISH', run.stderr)


if __name__ == '__main__':
    unittest.main()
