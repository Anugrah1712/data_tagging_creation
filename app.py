import os
import logging
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import StreamingResponse
from typing import List
from analyzer import analyze_image
from excel_util import json_to_excel_bytes
from io import BytesIO

# -----------------------------
# Configure logging
# -----------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Screenshot Tagging Service")

@app.get("/health")
async def health():
    logger.info("Health check requested")
    return {"status": "ok"}

@app.post("/upload")
async def upload_and_tag(files: List[UploadFile] = File(...)):
    logger.info(f"Received {len(files)} file(s) for tagging")
    all_events = []
    page_index = 1

    for f in files:
        logger.info(f"\nProcessing file {page_index}: {f.filename}")
        content = await f.read()
        logger.info(f"Read {len(content)} bytes from file {f.filename}")
        
        # Analyze image
        events = analyze_image(content)
        logger.info(f"Found {len(events)} events in {f.filename}")
        
        for e in events:
            all_events.append({
                "page": f"{f.filename} (page {page_index})",
                "element": e.get("element", ""),
                "event_type": e.get("event_type", ""),
                "trigger": e.get("trigger", ""),
                "description": e.get("description", "")
            })
        page_index += 1

    if not all_events:
        logger.info("No events detected in any file. Adding fallback row.")
        all_events.append({
            "page": "N/A",
            "element": "Unknown",
            "event_type": "View",
            "trigger": "No element detected by heuristics",
            "description": "Please review manually or enable Google Vision for better detection"
        })

    logger.info(f"Total events collected: {len(all_events)}. Generating Excel...")
    xlsx_bytes = json_to_excel_bytes(all_events)
    logger.info("Excel generation complete. Sending response.")

    return StreamingResponse(BytesIO(xlsx_bytes),
                             media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                             headers={"Content-Disposition": 'attachment; filename="data_tagging.xlsx"'})
