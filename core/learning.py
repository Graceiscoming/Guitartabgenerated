import logging

from core.models import EditHistory

logger = logging.getLogger("LEARNING")

# Mock Database สำหรับทดสอบ (บันทึกใน Memory)
DB_EDIT_HISTORY: list[EditHistory] = []
HISTORY_COUNTER = 1

def save_edit_history(old_pos: dict, new_pos: dict, profile_id: str) -> None:
    """
    Step 4.2: เก็บบันทึกประวัติการแก้ไข
    """
    global HISTORY_COUNTER
    history = EditHistory(
        id=HISTORY_COUNTER,
        profile_id=profile_id,
        midi_value=new_pos.get('midi_value', 0),
        old_string=old_pos.get('string', 0),
        old_fret=old_pos.get('fret', 0),
        new_string=new_pos.get('string', 0),
        new_fret=new_pos.get('fret', 0)
    )
    DB_EDIT_HISTORY.append(history)
    HISTORY_COUNTER += 1
    logger.debug("Saved preference profile=%s %s", profile_id, history)

def calculate_weight_score(position: dict, profile_id: str) -> float:
    """
    Step 4.3: คำนวณน้ำหนัก (Weight) ให้กับการเลือกเส้นทางตามสไตล์ผู้ใช้
    จำลองการเพิ่มโบนัสให้ระยะทาง (ยิ่งคะแนนโบนัสเยอะ ระยะทางเสมือนจะสั้นลง ทำให้ AI อยากเลือกเส้นนี้)
    """
    bonus = 0.0
    # ค้นหาว่าผู้ใช้ชอบเปลี่ยนมาใช้ fret/string นี้บ่อยแค่ไหน
    for history in DB_EDIT_HISTORY:
        if history.profile_id == profile_id and \
           history.new_string == position['string'] and \
           history.new_fret == position['fret']:
            bonus += 0.5 # หักล้างระยะ distance ให้ใกล้ขึ้น 0.5 หน่วย
            
    return bonus
