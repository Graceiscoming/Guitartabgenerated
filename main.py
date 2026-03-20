import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("API_MAIN")
from fastapi.responses import HTMLResponse
import os

from core.models import TabGenerateRequest, ManualOverrideRequest, RecalculateRequest
from core.guitar_logic import generate_tab_path
from core.learning import save_edit_history, DB_EDIT_HISTORY

app = FastAPI(
    title="Smart Adaptive Guitar Tab Generator",
    description="Backend API for generating and adapting guitar tabs dynamically.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", response_class=HTMLResponse)
def read_root():
    """
    Step 3.1: สร้าง Frontend UI พื้นฐานแสดงผมแทป
    """
    html_path = os.path.join(os.path.dirname(__file__), "static", "index.html")
    if os.path.exists(html_path):
        with open(html_path, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>UI is missing</h1><p>Please ensure static/index.html exists</p>"

@app.post("/api/tab/generate")
def api_generate_tab(req: TabGenerateRequest):
    """ Phase 2 API """
    logger.info(f"--- Generate Tab Request ---")
    logger.debug(f"Notes: {req.notes} | FretBox: {req.min_fret}-{req.max_fret} | Strings: {req.allowed_strings}")
    start_pos = None
    if req.start_fret is not None and req.start_string is not None:
        start_pos = {"string": req.start_string, "fret": req.start_fret}
        logger.debug(f"Explicit Start Pos: {start_pos}")
        
    path = generate_tab_path(
        req.notes, 
        req.min_fret, 
        req.max_fret, 
        start_pos=start_pos,
        allowed_strings=req.allowed_strings
    )
    logger.info(f"Generate tab completed: {len(path)} positions returned.")
    return {"tab_path": path}

@app.post("/api/tab/override")
def api_manual_override(req: ManualOverrideRequest):
    """ Phase 3.2 & 4: รับข้อมูลตอนผู้ใช้แก้โน้ต บันทึกประวัติ และคำนวณ path ใหม่จากจุดนั้น """
    logger.info(f"--- Manual Override Request ---")
    logger.debug(f"Edited Index: {req.edited_index} | Profile: {req.profile_id}")
    old_pos = req.tab_state[req.edited_index].dict()
    new_pos = req.new_position.dict()
    logger.debug(f"Old Position: {old_pos} -> New Position: {new_pos}")
    
    # 1. บันทึกเป็น Learning History
    save_edit_history(old_pos, new_pos, req.profile_id)
    
    # 2. อัปเดตตำแหน่ง
    updated_state = [p.dict() for p in req.tab_state]
    updated_state[req.edited_index] = new_pos
    
    # 3. Recalculate ส่วนที่เหลือ
    if req.edited_index + 1 < len(req.note_names):
        logger.debug(f"Recalculating tail starting from index {req.edited_index + 1}")
        dummy_remaining = ["DUMMY"] + req.note_names[req.edited_index + 1:]
        new_tail = generate_tab_path(
            dummy_remaining, 
            req.min_fret, 
            req.max_fret, 
            start_pos=new_pos, 
            profile_id=req.profile_id,
            allowed_strings=req.allowed_strings
        )
        updated_state = updated_state[:req.edited_index] + new_tail
        
    logger.info(f"Manual Override completed. Returning updated path.")
    return {"tab_path": updated_state}

@app.get("/api/learning/stats")
def api_learning_stats(profile_id: str = "default"):
    """ Return learning history and bonus scoring for dashboard """
    try:
        # Pydantic v1 vs v2 dict conversion wrapper
        history = [h.dict() if hasattr(h, 'dict') else h.model_dump() for h in DB_EDIT_HISTORY if h.profile_id == profile_id]
    except Exception:
        history = []
        
    favorites = {}
    for h in history:
        key = f"String {h['new_string']}, Fret {h['new_fret']}"
        if key not in favorites:
            favorites[key] = {"count": 0, "bonus": 0.0}
        favorites[key]["count"] += 1
        favorites[key]["bonus"] += 0.5
        
    return {
        "total_edits": len(history),
        "history": history,
        "favorites": favorites
    }

@app.post("/api/tab/recalculate")
def api_recalculate(req: RecalculateRequest):
    """
    Step 3.3: Manual explicitly calling AutoRecalculate
    """
    remaining_notes = req.note_names[req.start_index:]
    start_pos = req.tab_state[req.start_index].model_dump()
    recalc_path = generate_tab_path(
        remaining_notes, 
        req.min_fret, 
        req.max_fret, 
        start_pos=start_pos
    )
    return {"recalc_path": recalc_path}

if __name__ == "__main__":
    import uvicorn
    # run with python main.py
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
