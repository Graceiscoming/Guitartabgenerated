import unittest
import sys
import os

# Ensure the root directory is accessible for module imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.guitar_logic import (
    note_to_midi,
    get_guitar_fretboard,
    find_all_positions,
    filter_by_box_constraint,
    calculate_distance,
    generate_tab_path,
    _parse_note_str
)

class TestGuitarLogic(unittest.TestCase):
    
    def test_note_to_midi(self):
        self.assertEqual(note_to_midi("C4"), [60])
        self.assertEqual(note_to_midi("A4"), [69])
        # Octave-less notes return multiple valid ones across the fretboard
        midis = note_to_midi("C")
        self.assertTrue(48 in midis)
        self.assertTrue(60 in midis)
        self.assertTrue(72 in midis)
        
    def test_get_guitar_fretboard(self):
        tuning = get_guitar_fretboard()
        self.assertEqual(len(tuning), 6)
        self.assertEqual(tuning, [40, 45, 50, 55, 59, 64]) # E2, A2, D3, G3, B3, E4
        
    def test_find_all_positions(self):
        pos = find_all_positions(60) # C4
        # String 2 (B3=59), Fret 1 -> 59+1=60
        self.assertTrue(any(p['string'] == 2 and p['fret'] == 1 for p in pos))
        # String 3 (G3=55), Fret 5 -> 55+5=60
        self.assertTrue(any(p['string'] == 3 and p['fret'] == 5 for p in pos))

    def test_filter_by_box_constraint(self):
        pos = [
            {"string": 2, "fret": 1, "midi_value": 60},
            {"string": 3, "fret": 5, "midi_value": 60}
        ]
        # Restrict to fret 3-7
        filtered = filter_by_box_constraint(pos, 3, 7) 
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0]['fret'], 5)
        self.assertEqual(filtered[0]['string'], 3)
        
        # Restrict to strings 1-2 only
        filtered_str = filter_by_box_constraint(pos, 0, 24, allowed_strings=[1, 2])
        self.assertEqual(len(filtered_str), 1)
        self.assertEqual(filtered_str[0]['string'], 2)

    def test_parse_note_str(self):
        self.assertEqual(_parse_note_str("C"), ("C", None))
        self.assertEqual(_parse_note_str("C^"), ("C", "up"))
        self.assertEqual(_parse_note_str("C%"), ("C", "down"))

    def test_generate_tab_path_basic(self):
        path = generate_tab_path(["C4", "D4"], min_fret=0, max_fret=5)
        self.assertEqual(len(path), 2)
        # Engine selects S3 F5 for C4 based on top-down string iteration
        self.assertEqual(path[0]['fret'], 5)
        self.assertEqual(path[0]['string'], 3)
        self.assertEqual(path[1]['fret'], 3)
        self.assertEqual(path[1]['string'], 2)

    def test_generate_tab_path_directives(self):
        # Strict Pitch Modulators
        # C -> C^ (Must jump up one octave minimum)
        path = generate_tab_path(["C", "C^"], min_fret=0, max_fret=24)
        self.assertEqual(len(path), 2)
        self.assertGreater(path[1]['midi_value'], path[0]['midi_value'])

        # Explicit C5 -> C% (Must jump lower than C5)
        path_down = generate_tab_path(["C5", "C%"], min_fret=0, max_fret=24)
        self.assertEqual(len(path_down), 2)
        self.assertLess(path_down[1]['midi_value'], path_down[0]['midi_value'])

if __name__ == '__main__':
    unittest.main()
