from pydantic import BaseModel
from typing import List, Optional

# ==========================================
# Phase 4: Database Schema (ERD) แบบง่าย
# ==========================================

class NotePosition(BaseModel):
    string: int
    fret: int
    midi_value: int

class UserProfile(BaseModel):
    profile_id: str
    name: str
    description: str

class EditHistory(BaseModel):
    """
    ตารางบันทึกประวัติการแก้ไข เพื่อนำไปใช้คำนวณ Weight ในอนาคต
    """
    id: int
    profile_id: str
    midi_value: int
    old_string: int
    old_fret: int
    new_string: int
    new_fret: int

# ==========================================
# Request Models สำหรับ Phase 3 (API)
# ==========================================

class TabGenerateRequest(BaseModel):
    notes: List[str]
    min_fret: int = 0
    max_fret: int = 15
    allowed_strings: List[int] = [1, 2, 3, 4, 5, 6]
    start_string: Optional[int] = None
    start_fret: Optional[int] = None

class ManualOverrideRequest(BaseModel):
    note_names: List[str]
    tab_state: List[NotePosition]
    edited_index: int
    new_position: NotePosition
    profile_id: str = "default"
    min_fret: int = 0
    max_fret: int = 24
    allowed_strings: List[int] = [1, 2, 3, 4, 5, 6]

class RecalculateRequest(BaseModel):
    tab_state: List[NotePosition]
    note_names: List[str]
    start_index: int
    min_fret: int = 0
    max_fret: int = 15
