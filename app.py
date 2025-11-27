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
    print("Health check requested")
    return {"status": "ok"}

@app.post("/upload")
async def upload_and_tag(
    files: List[UploadFile] = File(...)
):
    print(f"Received {len(files)} file(s) for tagging")
    all_events = []
    page_index = 1

    for f in files:
        print(f"\nProcessing file {page_index}: {f.filename}")
        content = await f.read()
        print(f"Read {len(content)} bytes from file {f.filename}")
        
        events = analyze_image(content)
        print(f"Found {len(events)} events in {f.filename}")
        
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
        print("No events detected in any file. Adding fallback row.")
        all_events.append({
            "page": "N/A",
            "element": "Unknown",
            "event_type": "View",
            "trigger": "No element detected by heuristics",
            "description": "Please review manually or enable Google Vision for better detection"
        })

    print(f"Total events collected: {len(all_events)}. Generating Excel...")
    xlsx_bytes = json_to_excel_bytes(all_events)
    print("Excel generation complete. Sending response.")

    return StreamingResponse(BytesIO(xlsx_bytes),
                             media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                             headers={"Content-Disposition": 'attachment; filename="data_tagging.xlsx"'})
