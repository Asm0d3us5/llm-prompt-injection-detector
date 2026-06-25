import json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from scanner import hybrid_scan
import db

# Load ATLAS mapping once at startup
with open("../data/atlas_map.json") as f:
    ATLAS_MAP = json.load(f)

app = FastAPI(title="LLM Prompt Injection Detection API")

# Allow the frontend (running on a different port) to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

db.init_db()

class ScanRequest(BaseModel):
    text: str

@app.post("/scan")
def scan_endpoint(request: ScanRequest):
    result = hybrid_scan(request.text)
    atlas_info = ATLAS_MAP.get(result["category"], {"id": None, "name": None, "url": None})

    db.log_scan(request.text, result, atlas_info)

    return {
        "flagged": result["flagged"],
        "category": result["category"],
        "confidence": result["confidence"],
        "method": result["method"],
        "atlas": atlas_info,
    }

@app.get("/history")
def history_endpoint(limit: int = 50):
    return db.get_history(limit)

@app.get("/stats")
def stats_endpoint():
    return db.get_stats()

@app.get("/")
def root():
    return FileResponse("static/index.html")

app.mount("/static", StaticFiles(directory="static"), name="static")
