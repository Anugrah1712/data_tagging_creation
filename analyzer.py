#analyzer.py
import os
from PIL import Image
from io import BytesIO
import google.generativeai as genai
import json

# -----------------------------
# CONFIGURE GOOGLE FREE MODEL
# -----------------------------
genai.configure(api_key="AIzaSyC4mtKL0myHgRtQStZemypKLujiRJhIILg") 
model = genai.GenerativeModel("gemini-flash-latest")   

print("Configured Google Generative AI model: gemini-flash-latest")

def analyze_image(image_bytes: bytes):
    """
    Sends a single image to Google's free Gemini Flash Vision model
    and returns structured tagging JSON.
    """
    print("Opening image...")
    image = Image.open(BytesIO(image_bytes))
    print(f"Image opened: format={image.format}, size={image.size}, mode={image.mode}")

    prompt = """
    You are an expert UI/UX event tagging assistant.
    Identify all user-actions based on buttons, icons, text & UI elements.
    For each action return:

    - page: Name of the screen/page (guess if needed)
    - element: Name of the UI element (button/icon/text/etc.)
    - event_type: Click or View
    - trigger: What user action triggers this event
    - description: What the event means

    Return ONLY JSON as a list:
    [
      {
        "page": "",
        "element": "",
        "event_type": "",
        "trigger": "",
        "description": ""
      }
    ]
    """

    print("Sending image to model for analysis...")
    try:
        response = model.generate_content(
            [prompt, image],
            generation_config={
                "response_mime_type": "application/json"
            }
        )
        print("Received response from model.")
    except Exception as e:
        print(f"Error while generating content: {e}")
        return []

    # Ensure valid JSON
    try:
        events = json.loads(response.text)
        print(f"Parsed JSON successfully. Number of events found: {len(events)}")
        return events
    except Exception as e:
        print(f"Error parsing JSON: {e}")
        return []

def analyze_images(image_list: list[bytes]):
    """Process multiple images & merge results."""
    all_events = []
    for idx, img_bytes in enumerate(image_list, start=1):
        print(f"\n--- Processing image {idx}/{len(image_list)} ---")
        events = analyze_image(img_bytes)
        all_events.extend(events)
        print(f"Finished processing image {idx}, cumulative events: {len(all_events)}")
    print(f"\nAll images processed. Total events collected: {len(all_events)}")
    return all_events
