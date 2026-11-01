"""Chibi proportions: the floor rule, the height keys, points carried by the bake, and the empty manifest."""
import json
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / 'tools')]
import mmd
from tools.models.field_animations import chibi


def looping_clip():
    """Two bones: a key at frame 1, then a loop over frames 2..10 with one key at each end."""
    a = mmd.Anim()
    a.frame_count, a.has_scale = 12, False
    a.pose = [[0, 0, 0, 0, -100, 0]]
    a.instrs = [dict(op='key', frame=1, bones=[dict(bone=1, div=1, vals={'ty': 0})]),
                dict(op='loop_start', count=0xFF, raw=0x10FF),
                dict(op='key', frame=2, bones=[dict(bone=1, div=4, vals={'ty': 8})]),
                dict(op='sound', frame=4, bank=1, note=2),
                dict(op='key', frame=6, bones=[dict(bone=1, div=4, vals={'ty': -8}), dict(bone=1, div=2, vals={'rx': 4})]),
                dict(op='loop_end', frame=10, jump=2),
                dict(op='end')]
    return a


def heights(animation, ticks):
    player = mmd.AnimPlayer(animation, 2)
    out = {}
    for _ in range(ticks):
        player.tick()
        out.setdefault(player.frames[-1], player.pose[1][7])
    return out, player


class Floor(unittest.TestCase):
    def test_target(self):
        self.assertEqual(chibi.target(20), 0)          # a source that sinks goes on the floor
        self.assertEqual(chibi.target(-5), 0)          # one that nearly stands too
        self.assertEqual(chibi.target(-100), -100)     # a jump or a hover keeps its clearance
        for low in range(-40, 1):
            self.assertLessEqual(abs(chibi.target(low) - chibi.target(low - 1)), 2)   # no step at the margin

    def test_simplify_keeps_the_corners_only(self):
        line = [(x, min(x, 10 - x)) for x in range(11)]
        self.assertEqual(chibi._simplify(line, 0.5), [0, 5, 10])

    def test_heights_are_rewritten_exactly_and_the_loop_stays_closed(self):
        a = looping_clip()
        wanted = {1: -80, 2: -80, 3: -70, 4: -60, 5: -60, 6: -60, 7: -75, 8: -90, 9: -85, 10: -80}
        chibi._rewrite_heights(a, 1, wanted, 0.5)
        seen, player = heights(a, 30)
        self.assertEqual(seen, wanted)
        self.assertEqual(a.pose[0][4], -80)
        self.assertTrue(any(i.get('added') for i in a.instrs))
        self.assertEqual([e[1] for e in player.events][:1], ['sound'])
        frames = [i['frame'] for i in a.instrs if i['op'] in ('key', 'sound')]
        self.assertEqual(frames, sorted(frames))
        rotated = [g for i in a.instrs if i['op'] == 'key' for g in i['bones'] if 'rx' in g['vals']]
        self.assertEqual([(g['div'], g['vals']['rx']) for g in rotated], [(2, 4)])

    def test_a_clip_with_a_loop_that_skips_its_first_frame_is_left_to_a_constant_lift(self):
        a = looping_clip()
        a.instrs[-2]['jump'] = 3
        self.assertIsNone(chibi._chains(a))


class Record(unittest.TestCase):
    def test_points_ride_the_bake(self):
        scales = {7: (chibi._diagonal(2.0), [0.0, 10.0, 0.0])}
        self.assertEqual(chibi.carried_point(scales, 0.5, 7, [4, 20, 0]), [4, 15, 0])
        self.assertEqual(chibi.carried_point(scales, 0.5, 3, [4, 20, 0]), [2, 10, 0])

    def test_species_patch(self):
        scales = {7: (chibi._diagonal(2.0), [0.0, 0.0, 0.0])}
        record = dict(effect_origins=[[7, 'any', 10, 0, 3, 8, 8, 8]], condition_bubble=[0, -50, 0, 7],
                      effect_origin_fallback=[7, 1, 2, 3])
        self.assertEqual(chibi.species_patch(record, scales, 1.0),
                         dict(effect_origins=[[7, 'any', 20, 0, 3, 8, 8, 8]], condition_bubble=[0, -100, 0, 7],
                              effect_origin_fallback=[7, 2, 4, 6]))


class Manifest(unittest.TestCase):
    def test_no_species_is_enabled_without_its_pins(self):
        rows = json.loads(chibi.MANIFEST.read_text())
        for row in rows.values():
            self.assertTrue({'source_sha256', 'post_source_sha256', 'skeleton_sha256', 'groups', 'factors', 'height'} <= set(row))
        with self.assertRaisesRegex(ValueError, 'pinned'):
            chibi.build(b'not a reviewed model', [])

    def test_imports_without_site_packages(self):
        script = 'import sys; sys.path[:0] = [sys.argv[1], sys.argv[1] + "/tools"]\n' \
                 'import tools.models.field_animations.chibi\n' \
                 'assert "numpy" not in sys.modules and "PIL" not in sys.modules'
        result = subprocess.run([sys.executable, '-I', '-S', '-c', script, str(ROOT)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == '__main__':
    unittest.main()
