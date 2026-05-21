"""
Comprehensive and Multi-Category Test Suite
Covers:
1. Unit Testing (Edge & Boundary Cases)
2. Integration Testing (Workflow & API Contracts)
3. Negative & Failure Testing (Robustness, Input Validation & Exceptions)
4. Advanced State & Profile Isolation Testing
"""
import os
import sys
import unittest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import app
from core.guitar_logic import (
    note_to_midi,
    find_all_positions,
    filter_by_box_constraint,
    calculate_distance,
    generate_tab_path,
    parse_tab_token,
)
import core.learning as learning


class Test1_UnitBoundaryAndEdgeCases(unittest.TestCase):
    """
    CATEGORY 1: Unit Testing - Boundary & Edge Cases
    Tests functions with extreme, empty, or boundary values.
    """

    def test_empty_notes_input(self):
        """Edge case: empty note list should return empty path cleanly."""
        path = generate_tab_path([], min_fret=0, max_fret=24)
        self.assertEqual(path, [])

    def test_single_fret_box_constraint(self):
        """Boundary case: extremely narrow fret box (e.g. min_fret=5, max_fret=5)."""
        # Note A3 is MIDI 57
        # Open A string (string 5, fret 0) is 57.
        # String 6, fret 5 is 40 + 5 = 45 (not 57).
        # String 6, fret 17 is 57.
        # If we constrain fret to exactly 5, can we find positions?
        # Let's test note D3 (MIDI 50). Standard string 6 is 40. Fret 10 is 50.
        # String 5 (45) + fret 5 = 50.
        pos = find_all_positions(50)
        filtered = filter_by_box_constraint(pos, min_fret=5, max_fret=5)
        self.assertTrue(len(filtered) > 0)
        for p in filtered:
            # Must either be open string (fret 0) or exactly fret 5
            self.assertTrue(p["fret"] == 0 or p["fret"] == 5)

    def test_zero_fret_box_constraint(self):
        """Boundary case: Box constraint allowing ONLY open strings (min_fret=0, max_fret=0)."""
        pos = find_all_positions(64) # Note E4 (MIDI 64)
        # Should be open E1 string (string 1, fret 0)
        filtered = filter_by_box_constraint(pos, min_fret=0, max_fret=0)
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0]["string"], 1)
        self.assertEqual(filtered[0]["fret"], 0)

    def test_no_allowed_strings(self):
        """Edge case: allowed_strings is empty. Should return empty list of positions."""
        pos = find_all_positions(60)
        filtered = filter_by_box_constraint(pos, min_fret=0, max_fret=24, allowed_strings=[])
        self.assertEqual(filtered, [])

    def test_distance_calculation_same_position(self):
        """Boundary case: distance between the exact same fretboard position should be 0."""
        pos = {"string": 3, "fret": 5}
        self.assertEqual(calculate_distance(pos, pos), 0.0)


class Test2_NegativeAndFailureTesting(unittest.TestCase):
    """
    CATEGORY 2: Negative & Failure Testing
    Tests behavior when given invalid inputs, malformed data, or illegal parameters.
    """

    def test_invalid_note_octave_high(self):
        """Negative case: note with invalid sharp/flat naming conventions raises ValueError."""
        with self.assertRaises(ValueError):
            note_to_midi("C#X")

    def test_invalid_note_name_malformed(self):
        """Negative case: totally malformed string instead of a note."""
        with self.assertRaises(ValueError):
            note_to_midi("GuitarNote")

    def test_invalid_token_parsing(self):
        """Negative case: invalid syntax tokens should return None cleanly instead of crashing."""
        self.assertIsNone(parse_tab_token("S9F99"))  # String 9 doesn't exist
        self.assertIsNone(parse_tab_token("F12"))    # Missing String
        self.assertIsNone(parse_tab_token("S2F5x8"))  # Invalid technique key 'x'

    def test_unplayable_note_for_fretboard(self):
        """Negative case: a note too low to be played on a standard guitar (e.g. C1 = MIDI 24)."""
        path = generate_tab_path(["C1"], min_fret=0, max_fret=24)
        # The algorithm should skip/exclude it since no position can be found, returning empty or shorter path.
        self.assertEqual(path, [])


class Test3_IntegrationAndWorkflowTesting(unittest.TestCase):
    """
    CATEGORY 3: Integration & Workflow Testing
    Tests full API flows and data integration pipelines.
    """

    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def setUp(self):
        learning.DB_EDIT_HISTORY.clear()
        learning.HISTORY_COUNTER = 1

    def test_full_generate_override_recalculate_workflow(self):
        """
        Integration case: Simulate a complete user flow.
        1. Generate a tab path.
        2. Perform a manual override on the first note.
        3. Recalculate remaining notes based on the override.
        """
        # Step 1: Generate initial tab
        gen_resp = self.client.post(
            "/api/tab/generate",
            json={"notes": ["C4", "D4", "E4"], "min_fret": 0, "max_fret": 12}
        )
        self.assertEqual(gen_resp.status_code, 200)
        initial_path = gen_resp.json()["tab_path"]
        self.assertEqual(len(initial_path), 3)

        # Step 2: Override the 1st note (C4) from string 3, fret 5 to string 2, fret 1
        override_resp = self.client.post(
            "/api/tab/override",
            json={
                "note_names": ["C4", "D4", "E4"],
                "tab_state": initial_path,
                "edited_index": 0,
                "new_position": {
                    "string": 2,
                    "fret": 1,
                    "midi_value": 60
                },
                "min_fret": 0,
                "max_fret": 12,
                "profile_id": "test_workflow_user"
            }
        )
        self.assertEqual(override_resp.status_code, 200)
        overridden_path = override_resp.json()["tab_path"]
        self.assertEqual(overridden_path[0]["string"], 2)
        self.assertEqual(overridden_path[0]["fret"], 1)

        # Step 3: Recalculate the remaining notes starting from index 1 based on the override
        recalc_resp = self.client.post(
            "/api/tab/recalculate",
            json={
                "tab_state": overridden_path,
                "note_names": ["C4", "D4", "E4"],
                "start_index": 1,
                "min_fret": 0,
                "max_fret": 12
            }
        )
        self.assertEqual(recalc_resp.status_code, 200)
        recalc_path = recalc_resp.json()["recalc_path"]
        # Recalculated path length from index 1 should be 2 notes
        self.assertEqual(len(recalc_path), 2)


class Test4_RobustnessAndExtremeInputs(unittest.TestCase):
    """
    CATEGORY 4: Robustness & Security / Extreme Input Testing
    Tests API response under malicious or highly extreme parameters.
    """

    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_api_notes_parameter_injection(self):
        """Robustness: malicious strings in notes list should raise ValueError (propagated by TestClient)."""
        with self.assertRaises(ValueError):
            self.client.post(
                "/api/tab/generate",
                json={"notes": ["DROP TABLE Users;", "<script>alert(1)</script>"], "min_fret": 0, "max_fret": 12}
            )

    def test_api_out_of_bounds_recalculate_index(self):
        """Robustness: recalculate API with out-of-bounds start_index should raise IndexError (propagated by TestClient)."""
        with self.assertRaises(IndexError):
            self.client.post(
                "/api/tab/recalculate",
                json={
                    "tab_state": [{"string": 3, "fret": 5, "midi_value": 60}],
                    "note_names": ["C4"],
                    "start_index": 9999, # Absurd index
                    "min_fret": 0,
                    "max_fret": 12
                }
            )

    def test_extremely_large_profile_id(self):
        """Robustness: profile_id containing a massive string should not cause database / buffer overflows."""
        huge_profile_id = "A" * 10000
        r = self.client.get(f"/api/learning/stats?profile_id={huge_profile_id}")
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertEqual(data["total_edits"], 0)


if __name__ == "__main__":
    unittest.main()
