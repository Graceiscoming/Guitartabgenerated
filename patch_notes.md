# Patch Notes

---

## V1.0 — Smart Guitar Tab Ecosystem (Core)

- **[Core] Smart Guitar Tab Generator:** สร้างแทปอัตโนมัติจากชื่อโน้ต (C, D, E…) รองรับ Modifier `^` / `%` และโหมด Full Guitar / Midi
- **[Core] Interactive Tab Editor:** คลิกแก้ตำแหน่งบนแทป ระบบคำนวณโน้ตที่เหลือใหม่ทันที
- **[AI] AI Learning Dashboard:** จดจำ Manual Override สร้าง Favorites / Bonus Distance สำหรับรอบถัดไป
- **[Feature] Manual Position Builder (`/manual`):** ระบุสาย 1–6 และเฟรต 0–24 ทีละตำแหน่ง
- **[Feature] Export .txt:** ดาวน์โหลดแทป ASCII พร้อม Metadata

---

## V2.2 — แกะกระดาษ → แทปมาตรฐาน (21/5/2026)

- **[UX] หัวแทป:** ศิลปิน, Tuning, Capo, Tempo
- **[UX] Export ทั้งเพลง:** `.txt` รวมทุกท่อน · **พิมพ์ / PDF** พื้นขาว
- **[UX] คัดลอกแทป** · **Undo / Redo** (Ctrl+Z / Ctrl+Y)
- **[UX] อัปเดตแทปอัตโนมัติ** เมื่อเพิ่มโน้ต (ปิดได้)
- **[UX] PNG พิมพ์ (ขาว)** ต่อท่อน · จัดคอลัมน์แทปเท่ากันทุกสาย (`tab-format.js`)

---

## V2.1 — Clean & ใช้เองง่าย (21/5/2026)

- **[Clean]** ลบ `main.py`, `main_v2.py`, `index.html`, `manual.html`, สคริปต์ test ที่ root
- **[UX]** `/` redirect ไป `/v2` — จุดเข้าเดียว · PWA `start_url` = `/v2`
- **[UX]** Hub: **สำรอง JSON** / **นำเข้า JSON** · คำแนะนำ Ctrl+S
- **[Clean]** `app.py` สั้นลง · log ปกติ `WARNING` (ตั้ง `LOG_LEVEL=DEBUG` ตอนพัฒนา)
- **[Test]** `python run_tests.py` — pytest + output สวย

---

## V2.0 — Visual Builder, โปรเจกต์ & เทคนิคแทป (21/5/2026)

> รุ่นหลักที่รวม Backend เดียว (`app.py`), Visual Builder แบบโปรเจกต์, เทคนิคกีตาร์ครบชุด และการรันเซิร์ฟเวอร์แบบเปิด–ปิดได้

### แกนกลางระบบ (Backend & Launcher)

- **[Core] Unified Backend (`app.py`):** รวม `main.py` / `main_v2.py` เป็นจุดเข้าเดียว — routes `/`, `/v2`, `/manual`, API ครบ
- **[Core] Guitar Logic Engine:** Greedy pathfinding 24 เฟรต, รองรับ `S3F10`, slide, hammer-on, pull-off ผ่าน `parse_tab_token()`
- **[Fix] เซิร์ฟเวอร์รันเมื่อสั่งเท่านั้น:** `run_app.bat` รัน `python app.py` แบบ foreground — **ปิดหน้าต่างหรือ Ctrl+C = หยุด** (ไม่ใช้ `start /B` ค้างหลังปิด)
- **[Feature] `stop_app.bat`:** ปิด process ที่ค้างบน port 8000
- **[Feature] โหมดพัฒนา:** ตั้ง `DEV_RELOAD=1` ก่อน `python app.py` เพื่อเปิด auto-reload (ปกติปิดไว้)
- **[Fix] Service Worker:** ไม่แคชหน้า `/v2` แบบเก่า — โหลด HTML/JS จากเซิร์ฟเวอร์เสมอ (`cache v7`, network-first)

### PWA & Desktop

- **[Feature] Progressive Web App (PWA):** `manifest.json`, `service-worker.js`, `icon.svg` — ติดตั้งเป็นแอปบน Desktop ได้
- **[Feature] Desktop Launcher:** `run_app.bat` เปิดเซิร์ฟเวอร์ + เบราว์เซอร์ไป `/v2`

### Visual Fretboard Builder (`/v2`) — คอกีตาร์ & UI

- **[Feature] คอกีตาร์ 24 เฟรต:** Scroll แนวนอน, Fret markers (3–24), สาย 3D shadow
- **[Feature] Visual Persistence:** โน้ตที่เลือกค้างบนคอกีตาร์ พร้อมเลขลำดับ (1, 2, 3…)
- **[UI] Premium Layout:** โทนสีส้ม/เทา, Responsive, ไม่ทับปุ่ม

### ระบบโปรเจกต์ & หลายท่อน (Project Workspace)

- **[Feature] หน้า Hub โปรเจกต์:** เริ่มที่รายการเพลง — **1 เพลง = 1 โปรเจกต์** — เพลงใหม่ต้องสร้างโปรเจกต์ใหม่
- **[Feature] แทป/ท่อนในโปรเจกต์:** เพิ่ม/ลบ/สลับแทป (Intro, Verse, Chorus…) ข้อมูลอยู่ในโปรเจกต์เดียวเท่านั้น
- **[Feature] แถบสถานะ:** แสดง **โปรเจกต์ปัจจุบัน**, แทปที่กำลังแก้, สถานะ (ร่าง / ยังไม่บันทึก / บันทึกแล้ว)
- **[Feature] บันทึกในเว็บ:** ปุ่ม **บันทึกโปรเจกต์นี้** + `Ctrl+S` → `localStorage` กลับมาเปิดแก้ได้จาก Hub
- **[Feature] Export PNG:** ดาวน์โหลดแทปท่อนละรูป (html2canvas)
- **[Feature] Export .txt:** รายละเอียดทุกท่อนในโปรเจกต์
- **[Module] `static/v2-project.js`:** จัดการ store, Hub/Editor, บันทึก, PNG

### เทคนิคแทป (Techniques) — คลิกบนคอกีตาร์

| โหมด | วิธีใช้ | ผลบนแทป |
|------|---------|----------|
| สไลด์จุดเดียว | ติ๊กแล้วคลิก 1 ครั้ง | `/12` |
| สไลด์ช่วง | คลิกเฟรตต้นทาง → ปลายทาง (สายเดียวกัน) | `12/13` |
| Hammer-on | คลิกต่ำ → สูง | `5h8` |
| Pull-off | คลิกสูง → ต่ำ | `8p5` |

- **[Feature] สไลด์ `/12` ไม่ต้องมีโน้ตก่อนหน้า:** เริ่มแทปด้วย slide ได้
- **[Feature] Hammer / Pull:** แสดงเฉพนอ `h` / `p` ในแทป (ไม่มี H/P บรรทัดบน)
- **[Core] API token:** `S3F12`, `/S3F12`, `S3F12/13`, `S3F5h8`, `S3F8p5` ฯลฯ

### ไฟล์ & โครงสร้างสำคัญ

```
app.py                    # Entry point เดียว
core/guitar_logic.py      # Engine + parse_tab_token
core/learning.py          # AI learning (in-memory)
static/fretboard_builder.html
static/v2-project.js      # โปรเจกต์ / Hub / บันทึก
run_app.bat               # เปิดแอป (ปิด = หยุดเซิร์ฟเวอร์)
stop_app.bat              # หยุดตัวค้าง port 8000
```

### การทดสอบ

- **`tests/test_guitar_logic.py`** — engine, token, slide, hammer, pull
- **`tests/test_learning.py`** — ประวัติแก้ไข, weight score
- **`tests/test_api.py`** — หน้า HTML + REST API
- รันครั้งเดียว (output สวย): `python run_tests.py` หรือ `run_tests.bat` (pytest + pytest-sugar)
- แบบเดิม: `python -m unittest discover -s tests -p "test_*.py" -v`

---

## หมายเหตุเวอร์ชันก่อนหน้า (รวมเข้า V2.0 แล้ว)

รายการจาก V2.0 (26/3/2026) และ V2.1 (26/3/2026) เช่น การรวม `app.py`, PWA, คอกีตาร์ 24 เฟรต, Slide mode รุ่นแรก — **ถูกรวมและขยายใน V2.0 ด้านบนแล้ว** ไม่แยกเป็น V2.1 อีกต่อไป
