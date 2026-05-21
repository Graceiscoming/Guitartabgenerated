"""
Smart Adaptive Guitar Tab Generator — entry point
เปิดใช้งานหลักที่ /v2 (Visual Builder)
"""
import logging
import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

from core.guitar_logic import generate_tab_path
from core.learning import DB_EDIT_HISTORY, save_edit_history
from core.models import ManualOverrideRequest, RecalculateRequest, TabGenerateRequest

ROOT = Path(__file__).resolve().parent
STATIC = ROOT / "static"

HTML_NO_CACHE = {
    "Cache-Control": "no-cache, no-store, must-revalidate",
    "Pragma": "no-cache",
}

_log_name = os.getenv("LOG_LEVEL", "WARNING").upper()
logging.basicConfig(
    level=getattr(logging, _log_name, logging.WARNING),
    format="%(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger("app")

app = FastAPI(
    title="Guitar Tab Generator",
    description="Visual fretboard tab builder with pathfinding API",
    version="2.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _html_page(filename: str) -> HTMLResponse:
    path = STATIC / filename
    if path.exists():
        return HTMLResponse(path.read_text(encoding="utf-8"), headers=HTML_NO_CACHE)
    return HTMLResponse(f"<h1>Missing: {filename}</h1>", headers=HTML_NO_CACHE)


@app.get("/service-worker.js")
async def get_sw():
    return FileResponse(STATIC / "service-worker.js")


@app.get("/manifest.json")
async def get_manifest():
    return FileResponse(STATIC / "manifest.json")


@app.get("/icon.svg")
async def get_icon():
    return FileResponse(STATIC / "icon.svg")


app.mount("/static", StaticFiles(directory=str(STATIC)), name="static")


@app.get("/", response_class=HTMLResponse)
def root():
    return _html_page("index.html")


@app.get("/manual", response_class=HTMLResponse)
def read_manual_page():
    return _html_page("manual.html")


@app.get("/v2", response_class=HTMLResponse)
def read_v2_page():
    return _html_page("fretboard_builder.html")


@app.post("/api/tab/generate")
def api_generate_tab(req: TabGenerateRequest):
    start_pos = None
    if req.start_fret is not None and req.start_string is not None:
        start_pos = {"string": req.start_string, "fret": req.start_fret}
    path = generate_tab_path(
        req.notes,
        req.min_fret,
        req.max_fret,
        start_pos=start_pos,
        allowed_strings=req.allowed_strings,
    )
    return {"tab_path": path}


@app.post("/api/tab/override")
def api_manual_override(req: ManualOverrideRequest):
    old_pos = req.tab_state[req.edited_index].model_dump()
    new_pos = req.new_position.model_dump()
    save_edit_history(old_pos, new_pos, req.profile_id)

    updated_state = [p.model_dump() for p in req.tab_state]
    updated_state[req.edited_index] = new_pos

    if req.edited_index + 1 < len(req.note_names):
        dummy_remaining = ["DUMMY"] + req.note_names[req.edited_index + 1 :]
        new_tail = generate_tab_path(
            dummy_remaining,
            req.min_fret,
            req.max_fret,
            start_pos=new_pos,
            profile_id=req.profile_id,
            allowed_strings=req.allowed_strings,
        )
        updated_state = updated_state[: req.edited_index] + new_tail

    return {"tab_path": updated_state}


@app.get("/api/learning/stats")
def api_learning_stats(profile_id: str = "default"):
    history = [h.model_dump() for h in DB_EDIT_HISTORY if h.profile_id == profile_id]
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
        "favorites": favorites,
    }


@app.post("/api/tab/recalculate")
def api_recalculate(req: RecalculateRequest):
    remaining_notes = req.note_names[req.start_index:]
    start_pos = req.tab_state[req.start_index].model_dump()
    recalc_path = generate_tab_path(
        remaining_notes,
        req.min_fret,
        req.max_fret,
        start_pos=start_pos,
    )
    return {"recalc_path": recalc_path}


if __name__ == "__main__":
    import uvicorn

    dev_reload = os.getenv("DEV_RELOAD", "").lower() in ("1", "true", "yes")
    uvicorn.run(
        "app:app",
        host="127.0.0.1",
        port=int(os.getenv("PORT", "8000")),
        reload=dev_reload,
        log_level=_log_name.lower(),
    )
