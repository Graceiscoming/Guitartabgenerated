"""
Unit tests: core/guitar_logic.py
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.guitar_logic import (
    note_to_midi,
    get_guitar_fretboard,
    find_all_positions,
    filter_by_box_constraint,
    calculate_distance,
    generate_tab_path,
    parse_tab_token,
    _parse_note_str,
)


class TestNoteAndFretboard(unittest.TestCase):
    def test_note_to_midi_with_octave(self):
        self.assertEqual(note_to_midi("C4"), [60])
        self.assertEqual(note_to_midi("A4"), [69])

    def test_note_to_midi_without_octave(self):
        midis = note_to_midi("C")
        self.assertIn(48, midis)
        self.assertIn(60, midis)
        self.assertIn(72, midis)

    def test_note_to_midi_invalid_raises(self):
        with self.assertRaises(ValueError):
            note_to_midi("X9")

    def test_get_guitar_fretboard_standard_tuning(self):
        self.assertEqual(get_guitar_fretboard(), [40, 45, 50, 55, 59, 64])

    def test_find_all_positions_c4(self):
        pos = find_all_positions(60)
        self.assertTrue(any(p["string"] == 2 and p["fret"] == 1 for p in pos))
        self.assertTrue(any(p["string"] == 3 and p["fret"] == 5 for p in pos))


class TestConstraints(unittest.TestCase):
    def test_filter_by_fret_box(self):
        pos = [
            {"string": 2, "fret": 1, "midi_value": 60},
            {"string": 3, "fret": 5, "midi_value": 60},
        ]
        filtered = filter_by_box_constraint(pos, 3, 7)
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0]["fret"], 5)

    def test_filter_by_allowed_strings(self):
        pos = [
            {"string": 2, "fret": 1, "midi_value": 60},
            {"string": 3, "fret": 5, "midi_value": 60},
        ]
        filtered = filter_by_box_constraint(pos, 0, 24, allowed_strings=[1, 2])
        self.assertEqual(filtered[0]["string"], 2)

    def test_open_string_always_passes_fret_box(self):
        """fret 0 (open string) ผ่าน filter เสมอ แม้ min/max ไม่ครอบคลุม 0"""
        pos = [{"string": 6, "fret": 0, "midi_value": 40}]
        self.assertEqual(len(filter_by_box_constraint(pos, 5, 10)), 1)
        self.assertEqual(len(filter_by_box_constraint(pos, 0, 24)), 1)

    def test_calculate_distance_symmetry(self):
        a = {"string": 3, "fret": 5}
        b = {"string": 2, "fret": 3}
        self.assertEqual(calculate_distance(a, b), calculate_distance(b, a))


class TestParseNoteStr(unittest.TestCase):
    def test_plain_note(self):
        self.assertEqual(_parse_note_str("C"), ("C", None))

    def test_up_directive(self):
        self.assertEqual(_parse_note_str("C^"), ("C", "up"))

    def test_down_directive(self):
        self.assertEqual(_parse_note_str("C%"), ("C", "down"))


class TestParseTabToken(unittest.TestCase):
    def test_explicit_sf_format(self):
        tok = parse_tab_token("S3F10")
        self.assertEqual(tok["string"], 3)
        self.assertEqual(tok["fret"], 10)

    def test_slide_to_fret(self):
        tok = parse_tab_token("/S3F12")
        self.assertEqual(tok["modifier"], "/")
        self.assertEqual(tok["fret"], 12)

    def test_slide_range_sf(self):
        tok = parse_tab_token("S3F12/13")
        self.assertEqual(tok["slideToFret"], 13)
        self.assertEqual(tok["modifier"], "range")

    def test_slide_range_s_slash_format(self):
        tok = parse_tab_token("S3/12/13")
        self.assertEqual(tok["fret"], 12)
        self.assertEqual(tok["slideToFret"], 13)

    def test_hammer_on_token(self):
        tok = parse_tab_token("S2F5h8")
        self.assertEqual(tok["legatoType"], "hammer")
        self.assertEqual(tok["legatoToFret"], 8)

    def test_pull_off_token(self):
        tok = parse_tab_token("S2F8p5")
        self.assertEqual(tok["legatoType"], "pull")
        self.assertEqual(tok["legatoToFret"], 5)

    def test_invalid_token_returns_none(self):
        self.assertIsNone(parse_tab_token("not-a-note"))


class TestGenerateTabPath(unittest.TestCase):
    def test_basic_two_notes(self):
        path = generate_tab_path(["C4", "D4"], min_fret=0, max_fret=5)
        self.assertEqual(len(path), 2)
        self.assertEqual(path[0]["string"], 3)
        self.assertEqual(path[0]["fret"], 5)

    def test_empty_notes(self):
        self.assertEqual(generate_tab_path([]), [])

    def test_pitch_up_directive(self):
        path = generate_tab_path(["C", "C^"], min_fret=0, max_fret=24)
        self.assertGreater(path[1]["midi_value"], path[0]["midi_value"])

    def test_pitch_down_directive(self):
        path = generate_tab_path(["C5", "C%"], min_fret=0, max_fret=24)
        self.assertLess(path[1]["midi_value"], path[0]["midi_value"])

    def test_with_explicit_start_position(self):
        path = generate_tab_path(
            ["D4", "E4"],
            min_fret=0,
            max_fret=12,
            start_pos={"string": 2, "fret": 3, "midi_value": 62},
        )
        self.assertEqual(path[0]["string"], 2)
        self.assertEqual(path[0]["fret"], 3)


class TestTechniquesInPath(unittest.TestCase):
    def test_slide_first_note_no_prior(self):
        path = generate_tab_path(["/S3F12"])
        self.assertEqual(len(path), 1)
        self.assertEqual(path[0]["modifier"], "/")
        self.assertEqual(path[0]["fret"], 12)

    def test_two_slides_same_string(self):
        path = generate_tab_path(["/S3F5", "/S3F12"])
        self.assertEqual(len(path), 2)
        self.assertEqual(path[0]["modifier"], "/")
        self.assertEqual(path[1]["modifier"], "/")

    def test_slide_range_in_path(self):
        path = generate_tab_path(["S3F12/13"])
        self.assertEqual(path[0]["slideToFret"], 13)

    def test_hammer_on_in_path(self):
        path = generate_tab_path(["S2F5h8"])
        self.assertEqual(path[0]["fret"], 5)
        self.assertEqual(path[0]["legatoToFret"], 8)

    def test_pull_off_in_path(self):
        path = generate_tab_path(["S2F8p5"])
        self.assertEqual(path[0]["fret"], 8)
        self.assertEqual(path[0]["legatoToFret"], 5)

    def test_mixed_sequence(self):
        path = generate_tab_path(
            ["S3F5", "S3F5h7", "S3F12/13", "/S4F10"],
            min_fret=0,
            max_fret=24,
        )
        self.assertGreaterEqual(len(path), 4)


if __name__ == "__main__":
    unittest.main()
