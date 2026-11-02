"""A species' level comes from evidence, and a failed proof takes the old one away."""

from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import species_status as status


class Levels(unittest.TestCase):
    def test_a_species_with_no_evidence_is_only_in_the_game(self):
        table = {'species': {}}
        self.assertEqual(status.level(table, 3), 'native')
        self.assertEqual(status.level(table, 234), 'imported')

    def test_a_passed_proof_is_smoke_tested_not_reviewed(self):
        table = {'species': {}}
        status.record(table, {'234': {'ok': True}}, 'abc1234')
        self.assertEqual(status.level(table, 234), 'smoke-tested')
        self.assertEqual(table['species']['234']['proof'], 'abc1234')

    def test_a_failed_proof_removes_the_old_one(self):
        table = {'species': {'234': {'proof': 'old'}}}
        status.record(table, {'234': {'ok': False}}, 'new')
        self.assertEqual(status.level(table, 234), 'imported')

    def test_the_committed_table_names_species_that_exist(self):
        ids = set(status.species_ids())
        self.assertLessEqual({int(key) for key in status.load()['species']}, ids)


if __name__ == '__main__':
    unittest.main()
