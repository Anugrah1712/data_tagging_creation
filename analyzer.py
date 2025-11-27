# analyzer.py
from io import BytesIO
from PIL import Image
import pytesseract
import re
import base64

# heuristics keywords -> event mappings (extend as needed)
KEYWORDS = {
    "upload": {"event": "Click", "element_hint": "Upload Button"},
    "submit": {"event": "Click", "element_hint": "Submit Button"},
    "select": {"event": "Click", "element_hint": "Dropdown"},
    "dropdown": {"event": "Click", "element_hint": "Dropdown"},
    "discrepancy": {"event": "View", "element_hint": "Discrepancy panel"},
    "upload front": {"event": "Click", "element_hint": "Upload Front"},
    "upload back": {"event": "Click", "element_hint": "Upload Back"},
    "your deposit is on hold": {"event": "View", "element_hint": "Hold Banner"},
    "camera": {"event": "Click", "element_hint": "Camera Icon"},
}

def _text_from_image_bytes(image_bytes):
    img = Image.open(BytesIO(image_bytes)).convert("L")
    # simple threshold/resizing to help OCR
    img = img.resize((int(img.width * 1.5), int(img.height * 1.5)))
    text = pytesseract.image_to_string(img)
    return text.lower()

def heuristic_parse_text(text):
    parsed_events = []
    lines = text.splitlines()
    joined = " ".join([l.strip() for l in lines if l.strip()])
    # match multi-word keywords first
    for kw, meta in sorted(KEYWORDS.items(), key=lambda x: -len(x[0])):
        if kw in joined:
            parsed_events.append({
                "element": meta["element_hint"],
                "event_type": meta["event"],
                "trigger": f"Detected text '{kw}'",
                "description": f"Auto-detected by keyword '{kw}' in OCR text"
            })
    # fallback: look for words like Upload/Submit and generate generic events
    # find single-word matches
    for w in ["upload", "submit", "select", "dropdown", "camera"]:
        if re.search(r'\b' + w + r'\b', joined):
            meta = KEYWORDS.get(w, None)
            if meta:
                parsed_events.append({
                    "element": meta["element_hint"],
                    "event_type": meta["event"],
                    "trigger": f"Detected text '{w}'",
                    "description": f"Auto-detected by OCR word '{w}'"
                })
    # ensure unique by element+event_type
    seen = set()
    unique = []
    for e in parsed_events:
        key = (e["element"], e["event_type"])
        if key not in seen:
            seen.add(key)
            unique.append(e)
    return unique

def analyze_image(image_bytes: bytes, use_google=False, google_config: dict | None = None):
    """
    Return list of event dicts for the image.
    Each dict: {page, element, event_type, trigger, description}
    """
    # If the user wants to call Google Vision / Gemini, they can enable and implement here.
    if use_google:
        # ---------- PLACEHOLDER: integrate Google Generative Vision API here ----------
        # Example (pseudocode):
        # 1. send image bytes to Google Vision / Generative endpoint
        # 2. receive structured annotations (detected_text, layout, UI elements)
        # 3. map those annotations into the same output format below
        #
        # For now we fallback to local OCR so you can test without keys.
        pass

    # local OCR + heuristics
    text = _text_from_image_bytes(image_bytes)
    events = heuristic_parse_text(text)
    return events
