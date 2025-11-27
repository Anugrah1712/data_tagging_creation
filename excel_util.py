# excel_util.py
from openpyxl import Workbook
from io import BytesIO

HEADERS = ["Page", "Element", "Event Type", "Trigger", "Description"]

def json_to_excel_bytes(page_events: list):
    """
    page_events: list of {page, element, event_type, trigger, description}
    returns bytes of xlsx file
    """
    wb = Workbook()
    ws = wb.active
    ws.title = "Data Tagging"
    ws.append(HEADERS)

    for ev in page_events:
        ws.append([
            ev.get("page", ""),
            ev.get("element", ""),
            ev.get("event_type", ""),
            ev.get("trigger", ""),
            ev.get("description", "")
        ])

    f = BytesIO()
    wb.save(f)
    f.seek(0)
    return f.read()
