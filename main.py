from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import os

from core.models import TabGenerateRequest, ManualOverrideRequest, RecalculateRequest
from core.guitar_logic import generate_tab_path
from core.learning import save_edit_history

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
    return "<h1>UI is missing</h1>"

@app.post("/api/tab/generate")
def api_generate_tab(req: TabGenerateRequest):
    """ Phase 2 API """
    path = generate_tab_path(req.notes, req.min_fret, req.max_fret)
    return {"tab_path": path}

@app.post("/api/tab/override")
def api_manual_override(req: ManualOverrideRequest):
    """
    Step 3.2: ManualOverrideNote(index, newPosition) & Step 3.3: AutoRecalculate
    """
    old_pos = req.tab_state[req.index].model_dump()
    new_pos = req.new_position.model_dump()
    
    # 4.2 Save Edit History
    save_edit_history(old_pos, new_pos, req.profile_id)
    
    # 3.3 AutoRecalculate remaining tab path
    remaining_notes = req.note_names[req.index:]
    recalc_path = generate_tab_path(
        remaining_notes, 
        start_pos=new_pos, 
        profile_id=req.profile_id
    )
    
    # Update tab state locally
    req.tab_state[req.index:] = recalc_path
    
    return {"status": "success", "new_tab_state": req.tab_state}

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
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
