# Guitar Tab Generator

แอปสร้างแทปกีตาร์แบบจิ้มคอกีตาร์ — ใช้คนเดียวบนเครื่องตัวเอง ไม่ต้องพึ่ง cloud

---

## เริ่มใช้ (3 ขั้น)

```powershell
pip install -r requirements.txt
```

ดับเบิลคลิก **`run_app.bat`** หรือ:

```powershell
python app.py
```

เปิดเบราว์เซอร์ที่ **http://127.0.0.1:8000/v2** — ปิด Terminal = หยุดเซิร์ฟเวอร์

ถ้า port ค้าง: **`stop_app.bat`**

---

## ใช้งานประจำวัน

| ทำอะไร | วิธี |
|--------|------|
| เพลงใหม่ | โปรเจกต์ใหม่ → ตั้งชื่อเพลง |
| หลายท่อน | + เพิ่มแทป (Intro / Verse / Chorus) |
| บันทึก | **Ctrl+S** หรือ บันทึกโปรเจกต์นี้ |
| สำรอง | หน้า Hub → **สำรอง JSON** |
| ย้ายเครื่อง | นำเข้า JSON ที่ Hub |
| ทั้งเพลง | **ดาวน์โหลด .txt ทั้งเพลง** · **พิมพ์/PDF พื้นขาว** |
| ท่อนเดียว | PNG (จอ/พิมพ์) · .txt ท่อน · **คัดลอกแทป** |
| แก้ผิด | **Undo / Redo** · แทปอัปเดตอัตโนมัติ |

**เทคนิค:** เลือกโหมดเดียว — `/12` · `12/13` · `5h8` · `8p5` แล้วคลิกบนคอกีตาร์

---

## โครงสร้างโปรเจกต์ (สะอาดแล้ว)

```
app.py                 # เซิร์ฟเวอร์ + API
core/
  guitar_logic.py      # สร้างแทป / slide / hammer / pull
  learning.py          # จำสไตล์ (memory)
  models.py            # Pydantic
static/
  fretboard_builder.html
  v2-project.js        # โปรเจกต์ + localStorage
tests/                 # unit tests
run_app.bat            # เปิดแอป
run_tests.py           # รัน test แบบสวย
```

ลบของเก่าออกแล้ว: `main.py`, `main_v2.py`, หน้า `/` และ `/manual` แบบเก่า, สคริปต์ test ที่ root

---

## ทดสอบ

```powershell
pip install -r requirements-dev.txt
python run_tests.py
```

---

## โหมดพัฒนา

```powershell
set DEV_RELOAD=1
set LOG_LEVEL=DEBUG
python app.py
```

รายละเอียดเวอร์ชัน: `patch_notes.md` · แนวคิดเดิม: `idea.md`
