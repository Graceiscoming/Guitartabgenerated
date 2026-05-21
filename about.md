# โครงสร้างโปรเจกต์

## Backend (`app.py`)
- `GET /` → redirect ไป `/v2`
- `GET /v2` — Visual Builder
- `POST /api/tab/generate` — สร้าง path จากชื่อโน้ต
- `POST /api/tab/override` — แก้โน้ต + recalc ท้ายลำดับ
- `POST /api/tab/recalculate` — คำนวณใหม่จาก index
- `GET /api/learning/stats` — สถิติการแก้ (memory)

## Core
- `guitar_logic.py` — pathfinding, token parser
- `learning.py` — ประวัติแก้ไขใน RAM
- `models.py` — request/response schemas

## Frontend
- `fretboard_builder.html` + `v2-project.js` — Hub, โปรเจกต์, แทป, localStorage, PNG/JSON

## รัน
- `run_app.bat` — เปิดเซิร์ฟเวอร์ + เบราว์เซอร์
- `run_tests.py` — pytest
