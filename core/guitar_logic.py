import re
import math
from typing import Optional, Union
import logging
from core.learning import calculate_weight_score

logger = logging.getLogger("GUITAR_LOGIC")

# ==========================================
# Phase 1: Core Guitar Logic
# ==========================================

def note_to_midi(note_name: str) -> list[int]:
    """
    Step 1.1: แปลงชื่อโน้ตเป็นตัวเลข MIDI 
    ถ้าใส่ "C4" คืนค่า [60]
    ถ้าใส่แค่ "C" คืนค่าทุก C บนช่วงโน้ตกีตาร์ [48, 60, 72, 84] (Range E2=40 ถึง E6=88)
    """
    note_map = {
        'C': 0, 'C#': 1, 'Db': 1, 'D': 2, 'D#': 3, 'Eb': 3,
        'E': 4, 'F': 5, 'F#': 6, 'Gb': 6, 'G': 7, 'G#': 8, 'Ab': 8,
        'A': 9, 'A#': 10, 'Bb': 10, 'B': 11
    }
    match = re.match(r"^([A-G][#b]?)(-?\d+)?$", note_name.strip())
    if not match:
        raise ValueError(f"Invalid note name: {note_name}")
    
    note, octave = match.groups()
    if note not in note_map:
         raise ValueError(f"Invalid note name: {note_name}")
         
    if octave is not None:
        return [(int(octave) + 1) * 12 + note_map[note]]
    else:
        valid_midis = []
        for oct_idx in range(2, 7):
            midi = (oct_idx + 1) * 12 + note_map[note]
            if 40 <= midi <= 88: # Range ของกีตาร์ 24 เฟรต (E2=40, E4+24=88)
                valid_midis.append(midi)
        return valid_midis

def get_guitar_fretboard() -> list[int]:
    """
    Step 1.2: สร้างโครงสร้างคอกีตาร์เริ่มต้น (Standard Tuning)
    คืนค่า list ของ MIDI values สำหรับสายเปล่า (E2, A2, D3, G3, B3, E4)
    Index 0 = สาย 6, Index 5 = สาย 1
    """
    return [
        note_to_midi("E2")[0], # String 6
        note_to_midi("A2")[0], # String 5
        note_to_midi("D3")[0], # String 4
        note_to_midi("G3")[0], # String 3
        note_to_midi("B3")[0], # String 2
        note_to_midi("E4")[0]  # String 1
    ]

def find_all_positions(target: Union[int, list[int]], max_fret: int = 24) -> list[dict]:
    """
    Step 1.3: หาตำแหน่งบนคอกีตาร์ทั้งหมดของโน้ตตัวนั้น
    รองรับ array ของ MIDI เพื่อหาตำแหน่งทั้งหมดของโน้ตทุก Octave
    คืนค่า [{'string': 1-6, 'fret': 0-24, 'midi_value': int}]
    """
    positions = []
    tuning = get_guitar_fretboard()
    targets = target if isinstance(target, list) else [target]
    
    for midi_value in targets:
        for idx, open_midi in enumerate(tuning):
            fret = midi_value - open_midi
            if 0 <= fret <= max_fret:
                positions.append({
                    "string": 6 - idx, # สาย 1-6
                    "fret": fret,
                    "midi_value": midi_value
                })
            
    return positions


# ==========================================
# Phase 2: Smart Pathfinding
# ==========================================

def filter_by_box_constraint(positions: list[dict], min_fret: int, max_fret: int, allowed_strings: Optional[list[int]] = None) -> list[dict]:
    """
    Step 2.1: คัดกรองโน้ตให้อยู่ใน Fret Box และช่วงสายที่อนุญาต (เช่น ไม่เอาเบส)
    """
    if allowed_strings is None:
        allowed_strings = [1, 2, 3, 4, 5, 6]
        
    filtered = []
    for pos in positions:
        if pos['string'] in allowed_strings:
            # ยอมให้ใช้สายเปล่าได้เสมอ หรืออยู่ในช่วง fret ที่กำหนด
            if pos['fret'] == 0 or (min_fret <= pos['fret'] <= max_fret):
                filtered.append(pos)
    return filtered

def calculate_distance(pos_a: dict, pos_b: dict, profile_id: str = "default") -> float:
    """
    Step 2.2: คำนวณระยะห่างระหว่างจุด 2 จุด (เฟรต + สาย) เพื่อดูว่ากดยากง่ายแค่ไหน
    ยิ่งค่าน้อย ยิ่งกดย้ายง่าย
    """
    fret_diff = abs(pos_a['fret'] - pos_b['fret'])
    string_diff = abs(pos_a['string'] - pos_b['string'])
    
    # ให้น้ำหนักระยะเฟรตมากกว่าระยะสายเล็กน้อย
    base_dist = math.sqrt((fret_diff * 1.5)**2 + (string_diff * 1.0)**2)
    
    # Step 4.3 Integration: ดึงคะแนนพิเศษ (Weight) มาลดทอนจำลองระยะทาง
    bonus = calculate_weight_score(pos_b, profile_id)
    return max(0.0, base_dist - bonus)

def _parse_note_str(note_str: str) -> tuple[str, Optional[str]]:
    """ Extracts base note and direction modifier (^, %) """
    note_str = note_str.strip()
    direction = None
    if note_str.endswith('^'):
        direction = 'up'
        note_str = note_str[:-1]
    elif note_str.endswith('%'):
        direction = 'down'
        note_str = note_str[:-1]
    return note_str, direction

def _get_valid_positions(base_note: str, direction: Optional[str], prev_pos: Optional[dict], min_fret: int, max_fret: int, allowed_strings: Optional[list[int]]) -> list[dict]:
    """ Retrieves strictly valid positions matching the Fret Box, String rules, and Direction (+/-) """
    midi_val = note_to_midi(base_note)
    all_pos = find_all_positions(midi_val)
    valid_pos = filter_by_box_constraint(all_pos, min_fret, max_fret, allowed_strings)
    
    if not valid_pos:
        logger.debug(f"[Engine] '{base_note}' missing in Fret Box. Relaxing constraint to string limits only.")
        valid_pos = [p for p in all_pos if p['string'] in (allowed_strings or [1,2,3,4,5,6])]
        if not valid_pos:
            logger.debug(f"[Engine] '{base_note}' missing entirely. Relaxing all constraints.")
            valid_pos = all_pos

    if direction and prev_pos:
        if direction == 'up':
            dir_pos = [p for p in valid_pos if p['midi_value'] > prev_pos['midi_value']]
            if dir_pos:
                valid_pos = dir_pos
                logger.debug(f"[Engine] Enforced UP pitch constraint. Valid options reduced.")
            else:
                logger.warning(f"[Engine] Cannot enforce UP constraint for {base_note}.")
        elif direction == 'down':
            dir_pos = [p for p in valid_pos if p['midi_value'] < prev_pos['midi_value']]
            if dir_pos:
                valid_pos = dir_pos
                logger.debug(f"[Engine] Enforced DOWN pitch constraint. Valid options reduced.")
            else:
                logger.warning(f"[Engine] Cannot enforce DOWN constraint for {base_note}.")
    elif direction and not prev_pos:
        # First note special case sorting
        if direction == 'up':
            valid_pos.sort(key=lambda x: x['midi_value'], reverse=True)
            logger.debug(f"[Engine] Sorted first note descending due to ^ constraint.")
        elif direction == 'down':
            valid_pos.sort(key=lambda x: x['midi_value'])
            logger.debug(f"[Engine] Sorted first note ascending due to % constraint.")

    return valid_pos

def generate_tab_path(note_names: list[str], min_fret: int = 0, max_fret: int = 12, start_pos: Optional[dict] = None, profile_id: str = "default", allowed_strings: Optional[list[int]] = None) -> list[dict]:
    """
    Step 2.3: อัลกอริทึมหลักในการเชื่อมโยงโน้ตเป็นแทป (Greedy closest path)
    รองรับ ^ (สูงกว่าตัวก่อนหน้า) และ % (ต่ำกว่าตัวก่อนหน้า) 
    โค้ดถูกจัดการโครงสร้างใหม่ให้ Clean ขึ้น (Refactored)
    """
    if not note_names:
        return []

    logger.debug(f"[Engine] Starting Pathfinding | Notes: {len(note_names)} | StartPos: {start_pos}")
    path = []
    
    # 1. จัดการโน้ตเปิดจุดเริ่มต้น
    if start_pos and start_pos.get('fret') is not None:
        current_pos = start_pos
        if 'midi_value' not in current_pos:
            tuning = get_guitar_fretboard()
            string_idx = 6 - current_pos['string']
            open_midi = tuning[string_idx]
            current_pos['midi_value'] = open_midi + current_pos['fret']
        logger.debug(f"[Engine] Using forced start position: {current_pos}")
        path.append(current_pos)
    else:
        # โน้ตตัวแรกแบบออโต้
        base_note, direction = _parse_note_str(note_names[0])
        logger.debug(f"[Engine] First note parsed as: {base_note} | Direction: {direction}")
        valid_first_pos = _get_valid_positions(base_note, direction, None, min_fret, max_fret, allowed_strings)
        if not valid_first_pos:
            logger.warning(f"[Engine] No valid starting position for {base_note}. Returning empty path.")
            return []
        current_pos = valid_first_pos[0]
        logger.debug(f"[Engine] Selected first position: {current_pos}")
        path.append(current_pos)

    # 2. ค้นหาเส้นทางโน้ตตัวถัดๆ ไป (Engine Core Loop)
    start_idx = 1 if not start_pos else 1 
    for i in range(start_idx, len(note_names)):
        base_note, direction = _parse_note_str(note_names[i])
        logger.debug(f"[Engine] Solving Note [{i}]: {note_names[i]} (Base: {base_note}, Dir: {direction})")
        
        valid_next_pos = _get_valid_positions(base_note, direction, current_pos, min_fret, max_fret, allowed_strings)
        if not valid_next_pos:
            logger.warning(f"[Engine] No valid positions left for {base_note}. Aborting subsequent path logic.")
            break
            
        # กลยุทธ์ Greedy: หาตำแหน่งที่ระยะทาง Cost รวมในการย้ายนิ้วน้อยที่สุด
        best_pos = valid_next_pos[0]
        min_distance = calculate_distance(current_pos, best_pos, profile_id)
        
        for pos in valid_next_pos[1:]:
            dist = calculate_distance(current_pos, pos, profile_id)
            if dist < min_distance:
                min_distance = dist
                best_pos = pos
                
        logger.debug(f"[Engine] Selected optimal step -> {best_pos} (Cost: {min_distance:.2f})")
        path.append(best_pos)
        current_pos = best_pos
            
    logger.debug(f"[Engine] Pathfinding complete.")
    return path
