# 🎸 Smart Adaptive Guitar Tab Generator V2.1

**The Ultimate, Unified Guitar Tab Ecosystem with Visual Fretboard & Desktop App Mode.**

ชุดเครื่องมือสร้างและสุ่มแทปกีตาร์อัจฉริยะที่ควบรวมทุกฟีเจอร์ไว้ในหนึ่งเดียว (Unified Backend) ทำงานบนระบบสมองกล (Greedy Pathfinding) เพื่อค้นหาเส้นทางการเล่นที่ลื่นไหลที่สุดบนคอกีตาร์ 24 เฟรต พร้อมระบบเรียนรู้พฤติกรรม (AI Learning) และโหมดแอปพลิเคชันติดตั้งได้ (PWA)

---

## ✨ NEW Features in V2.1 (จุดเด่นใหม่)
- **🎨 Premium Visual Builder (V2):** หน้าจำลองคอกีตาร์ 24 เฟรตแบบสมจริง จิ้มเลือกโน้ตได้โดยตรง พร้อมระบบบอกลำดับ (Sequence Number) และโหมดลูกสไลด์ 🔗
- **🖥️ Desktop App Mode (PWA):** สามารถติดตั้งเป็นแอปพลิเคชันเดี่ยว (Install as App) ได้ทันที มีไอคอน 🎸 บน Desktop และทำงานในหน้าต่างแยกส่วนตัว
- **⚡ Unified Backend (`app.py`):** ยุบรวมทุกฟังก์ชันจากรุ่นก่อนหน้ามาไว้ในที่เดียว เพื่อความเสถียรและความเร็วสูงสุด
- **🖱️ One-Click Launcher:** สคริปต์ `run_app.bat` กดดับเบิลคลิกเดียวเปิดใช้งานได้ทุกอย่าง ไม่ต้องพิมพ์คำสั่งใน Terminal เองอีกต่อไป
- **💎 Premium UI Design:** ดีไซน์ใหม่หมดจดด้วย Gradient Colors, Drop Shadows และ Layout แบบ Responsive ไม่ทับซ้อนกัน

---

## 🚀 Setup & Launch (วิธีเริ่มใช้งานอย่างง่าย)

1. **ติดตั้ง Dependencies (ครั้งแรกเท่านั้น):**
   เปิด Terminal ในโฟลเดอร์นี้แล้วรัน:
   ```powershell
   pip install -r requirements.txt
   ```

2. **เปิดใช้งานแอป (เมื่อต้องการใช้เท่านั้น):**
   ```powershell
   cd D:\GitHub\guitartabgenerated
   python app.py
   ```
   หรือดับเบิลคลิก `run_app.bat` — **ปิดหน้าต่าง Terminal หรือกด Ctrl+C = หยุดเซิร์ฟเวอร์** (ไม่รันค้างหลังปิด)

   ถ้าเคยรันแบบเก่าแล้วยังค้างอยู่: ดับเบิลคลิก `stop_app.bat`

   โหมดพัฒนา (auto-reload เมื่อแก้โค้ด): `set DEV_RELOAD=1` แล้ว `python app.py`

3. **ติดตั้งลงเครื่อง (PWA):**
   เมื่อแอปเปิดขึ้นมา แนะนำให้กดปุ่ม **"Install" (รูป 📥 ในช่อง URL)** เพื่อสร้างไอคอนแอปบนหน้า Desktop ครับ

---

## 💻 3 โหมดการใช้งานหลัก
1. **Smart Auto Tab (`/`):** พิมพ์ชื่อโน้ต (เช่น C, D, E) แล้วให้ AI คำนวณหาจุดที่ดีที่สุดให้เอง พร้อมระบบแก้โน้ตแบบ Interactive
2. **Visual Builder (`/v2`):** จิ้มที่คอกีตาร์เพื่อแต่งเพลง — **โปรเจกต์หลายท่อน** (Intro / Verse / Chorus) บันทึกอัตโนมัติในเบราว์เซอร์ และ **Save ท่อนเป็น PNG**
3. **Manual Builder (`/manual`):** ระบุสายและเฟรตเองทีละตำแหน่งสำหรับขาโหดที่ต้องการควบคุมทุกอย่าง

### การทดสอบ (Unit Tests)

รันครั้งเดียวครบทุกไฟล์ใน `tests/`:

```powershell
cd D:\GitHub\guitartabgenerated
python -m unittest discover -s tests -p "test_*.py" -v
```

หรือดับเบิลคลิก `run_tests.bat`

| ไฟล์ | ครอบคลุม |
|------|-----------|
| `tests/test_guitar_logic.py` | โน้ต, fretboard, pathfinding, slide, hammer, pull |
| `tests/test_learning.py` | AI learning, weight score |
| `tests/test_api.py` | หน้าเว็บ, API generate / override / recalculate / stats |

---

### V2 — โปรเจกต์แยกชัด
1. เปิด `/v2` → **สร้างโปรเจกต์ใหม่** (1 เพลง = 1 โปรเจกต์)
2. ในโปรเจกต์: **+ เพิ่มแทป** / **− ลบแทป** (Intro, Verse, Chorus…)
3. **💾 บันทึกโปรเจกต์นี้** (Ctrl+S) — กลับมาเปิดจากรายการโปรเจกต์
4. **เพลงใหม่** = โปรเจกต์ใหม่แยกต่างหาก · แถบบอก **โปรเจกต์ปัจจุบัน** ตลอด
5. **🖼 Export PNG** — ดาวน์โหลดรูปแทปเดียว

---

## ✅ Quality & Development
หากต้องการทดสอบกลไกเชิงเทคนิค สามารถรัน `unittest` ได้ด้วย:
```powershell
python -m unittest discover tests
```

---

## 📄 Patch Notes & Credits
สามารถดูรายละเอียดการอัปเดตย้อนหลังและเจาะลึกฟีเจอร์แต่ละเวอร์ชันได้ที่ไฟล์ `patch_notes.md` ครับ 🎸🔥



