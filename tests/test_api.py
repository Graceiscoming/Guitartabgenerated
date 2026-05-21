"""
Integration tests: FastAPI app (app.py)
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient

import core.learning as learning
from app import app


def _pos(string: int, fret: int, midi: int, modifier=None) -> dict:
    p = {"string": string, "fret": fret, "midi_value": midi}
    if modifier is not None:
        p["modifier"] = modifier
    return p


class TestStaticPages(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_home_page(self):
        r = self.client.get("/")
        self.assertEqual(r.status_code, 200)
        self.assertIn("text/html", r.headers.get("content-type", ""))

    def test_v2_page(self):
        r = self.client.get("/v2")
        self.assertEqual(r.status_code, 200)
        self.assertIn("fretboard", r.text.lower())

    def test_manual_page(self):
        r = self.client.get("/manual")
        self.assertEqual(r.status_code, 200)

    def test_manifest(self):
        r = self.client.get("/manifest.json")
        self.assertEqual(r.status_code, 200)

    def test_service_worker(self):
        r = self.client.get("/service-worker.js")
        self.assertEqual(r.status_code, 200)


class TestTabGenerateAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_generate_basic(self):
        r = self.client.post(
            "/api/tab/generate",
            json={
                "notes": ["C4", "D4"],
                "min_fret": 0,
                "max_fret": 12,
            },
        )
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertIn("tab_path", data)
        self.assertEqual(len(data["tab_path"]), 2)

    def test_generate_with_start_position(self):
        r = self.client.post(
            "/api/tab/generate",
            json={
                "notes": ["E4", "F4"],
                "min_fret": 0,
                "max_fret": 12,
                "start_string": 1,
                "start_fret": 0,
            },
        )
        self.assertEqual(r.status_code, 200)
        path = r.json()["tab_path"]
        self.assertEqual(path[0]["string"], 1)
        self.assertEqual(path[0]["fret"], 0)

    def test_generate_slide_techniques(self):
        r = self.client.post(
            "/api/tab/generate",
            json={
                "notes": ["/S3F12", "S3F12/13", "S2F5h8", "S2F8p5"],
                "min_fret": 0,
                "max_fret": 24,
            },
        )
        self.assertEqual(r.status_code, 200)
        path = r.json()["tab_path"]
        self.assertEqual(len(path), 4)
        self.assertEqual(path[0]["modifier"], "/")
        self.assertEqual(path[1]["slideToFret"], 13)
        self.assertEqual(path[2]["legatoToFret"], 8)


class TestTabRecalculateAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_recalculate_from_index(self):
        tab_state = [
            _pos(3, 5, 60),
            _pos(2, 3, 62),
            _pos(2, 5, 64),
        ]
        r = self.client.post(
            "/api/tab/recalculate",
            json={
                "tab_state": tab_state,
                "note_names": ["C4", "D4", "E4"],
                "start_index": 1,
                "min_fret": 0,
                "max_fret": 12,
            },
        )
        self.assertEqual(r.status_code, 200)
        recalc = r.json()["recalc_path"]
        self.assertGreaterEqual(len(recalc), 2)
        self.assertEqual(recalc[0]["string"], tab_state[1]["string"])


class TestManualOverrideAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def setUp(self):
        learning.DB_EDIT_HISTORY.clear()
        learning.HISTORY_COUNTER = 1

    def test_override_updates_position(self):
        tab_state = [
            _pos(3, 5, 60),
            _pos(2, 3, 62),
        ]
        r = self.client.post(
            "/api/tab/override",
            json={
                "note_names": ["C4", "D4"],
                "tab_state": tab_state,
                "edited_index": 0,
                "new_position": _pos(2, 1, 60),
                "min_fret": 0,
                "max_fret": 12,
            },
        )
        self.assertEqual(r.status_code, 200)
        path = r.json()["tab_path"]
        self.assertEqual(path[0]["string"], 2)
        self.assertEqual(path[0]["fret"], 1)
        self.assertGreaterEqual(len(learning.DB_EDIT_HISTORY), 1)


class TestLearningStatsAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def setUp(self):
        learning.DB_EDIT_HISTORY.clear()
        learning.HISTORY_COUNTER = 1
        from core.learning import save_edit_history

        save_edit_history(
            {"string": 1, "fret": 0, "midi_value": 64},
            {"string": 3, "fret": 5, "midi_value": 60},
            "stats_user",
        )

    def test_learning_stats(self):
        r = self.client.get("/api/learning/stats?profile_id=stats_user")
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertEqual(data["total_edits"], 1)
        self.assertIn("favorites", data)
        self.assertGreater(len(data["favorites"]), 0)


if __name__ == "__main__":
    unittest.main()
