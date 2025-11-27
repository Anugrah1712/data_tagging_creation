import logging
from openpyxl import Workbook
from io import BytesIO

# -----------------------------
# Configure logging
# -----------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

HEADERS = ["Page", "Element", "Event Type", "Trigger", "Description"]

def json_to_excel_bytes(page_events: list):
    """
    page_events: list of {page, element, event_type, trigger, description}
    returns bytes of xlsx file
    """
    logger.info("Creating Excel workbook...")
    wb = Workbook()
    ws = wb.active
    ws.title = "Data Tagging"
    
    logger.info("Adding header row...")
    ws.append(HEADERS)

    for idx, ev in enumerate(page_events, start=1):
        ws.append([
            ev.get("page", ""),
            ev.get("element", ""),
            ev.get("event_type", ""),
            ev.get("trigger", ""),
            ev.get("description", "")
        ])
        if idx % 5 == 0 or idx == len(page_events):
            logger.info(f"Added {idx}/{len(page_events)} rows to Excel")

    f = BytesIO()
    wb.save(f)
    f.seek(0)
    logger.info(f"Excel workbook created successfully with {len(page_events)} rows.")
    return f.read()
