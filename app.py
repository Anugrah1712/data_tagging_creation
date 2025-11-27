# app.py
import os
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import StreamingResponse, JSONResponse
from typing import List
from analyzer import analyze_image
from excel_util import json_to_excel_bytes
from io import BytesIO

app = FastAPI(title="Screenshot Tagging Service")

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/upload")
async def upload_and_tag(
    files: List[UploadFile] = File(...),
    use_google: bool = Form(False)
):
    """
    Accepts multiple image files.
    - use_google (form bool) if True will attempt to use Google (you must implement keys).
    Returns an xlsx file as streaming response.
    """
    all_events = []
    page_index = 1
    for f in files:
        content = await f.read()
        # run analyzer (local by default)
        events = analyze_image(content, use_google=use_google)
        # map into page-level events
        for e in events:
            all_events.append({
                "page": f"{f.filename} (page {page_index})",
                "element": e.get("element", ""),
                "event_type": e.get("event_type", ""),
                "trigger": e.get("trigger", ""),
                "description": e.get("description", "")
            })
        page_index += 1

    # If no events were found, add a fallback row to help user
    if not all_events:
        all_events.append({
            "page": "N/A",
            "element": "Unknown",
            "event_type": "View",
            "trigger": "No element detected by heuristics",
            "description": "Please review manually or enable Google Vision for better detection"
        })

    xlsx_bytes = json_to_excel_bytes(all_events)
    return StreamingResponse(BytesIO(xlsx_bytes),
                             media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                             headers={"Content-Disposition": 'attachment; filename="data_tagging.xlsx"'})
