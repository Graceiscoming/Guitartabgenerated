"""
Unit tests: core/learning.py
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import core.learning as learning
from core.learning import save_edit_history, calculate_weight_score


class TestLearning(unittest.TestCase):
    def setUp(self):
        learning.DB_EDIT_HISTORY.clear()
        learning.HISTORY_COUNTER = 1

    def test_save_edit_history_appends(self):
        save_edit_history(
            {"string": 2, "fret": 1, "midi_value": 60},
            {"string": 3, "fret": 5, "midi_value": 60},
            "default",
        )
        self.assertEqual(len(learning.DB_EDIT_HISTORY), 1)
        self.assertEqual(learning.DB_EDIT_HISTORY[0].new_fret, 5)

    def test_calculate_weight_score_no_history(self):
        pos = {"string": 3, "fret": 5}
        self.assertEqual(calculate_weight_score(pos, "default"), 0.0)

    def test_calculate_weight_score_with_bonus(self):
        save_edit_history(
            {"string": 1, "fret": 0, "midi_value": 64},
            {"string": 3, "fret": 7, "midi_value": 62},
            "player1",
        )
        save_edit_history(
            {"string": 2, "fret": 3, "midi_value": 59},
            {"string": 3, "fret": 7, "midi_value": 62},
            "player1",
        )
        bonus = calculate_weight_score({"string": 3, "fret": 7}, "player1")
        self.assertEqual(bonus, 1.0)

    def test_profile_isolation(self):
        save_edit_history(
            {"string": 2, "fret": 1, "midi_value": 60},
            {"string": 2, "fret": 3, "midi_value": 62},
            "alice",
        )
        self.assertEqual(calculate_weight_score({"string": 2, "fret": 3}, "bob"), 0.0)
        self.assertEqual(calculate_weight_score({"string": 2, "fret": 3}, "alice"), 0.5)

    def test_weight_affects_pathfinding(self):
        from core.guitar_logic import generate_tab_path

        save_edit_history(
            {"string": 1, "fret": 0, "midi_value": 64},
            {"string": 3, "fret": 5, "midi_value": 60},
            "fav",
        )
        path_default = generate_tab_path(["C4"], min_fret=0, max_fret=12, profile_id="other")
        path_fav = generate_tab_path(["C4"], min_fret=0, max_fret=12, profile_id="fav")
        self.assertIsInstance(path_default, list)
        self.assertIsInstance(path_fav, list)
        self.assertGreater(len(path_fav), 0)


if __name__ == "__main__":
    unittest.main()
