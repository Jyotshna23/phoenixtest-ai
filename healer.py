import json
import os
import re
import time
from datetime import datetime

from google import genai
from google.genai import types
from pydantic import BaseModel, Field
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
MODEL = "gemini-3.8-flash"
CONFIDENCE_THRESHOLD = 75
MAX_HTML_CHARS = 30000
LOG_FILE = "healing_log.json"


class LocatorFix(BaseModel):
    css_selector: str = Field(description="A CSS selector that matches exactly one element on the page")
    reason: str = Field(description="Why this selector points to the intended element")
    confidence: int = Field(description="Integer from 0 to 100")


def clean_html(html):
    # Remove scripts, styles, svgs and comments so Gemini gets a smaller, faster prompt
    html = re.sub(r"<(script|style|svg|noscript)\b.*?</\1>", "", html, flags=re.S | re.I)
    html = re.sub(r"<!--.*?-->", "", html, flags=re.S)
    html = re.sub(r"\s+", " ", html)
    return html[:MAX_HTML_CHARS]


def ask_gemini(description, failed_by, failed_value, page_html):
    prompt = f"""You are a QA automation engineer. A Selenium locator no longer works.
Element we want: {description}
Broken locator: By.{failed_by.upper()} = "{failed_value}"
Below is the current page HTML. Return a CSS selector that matches exactly one element,
the one described above. Prefer id or data-test attributes.

{page_html}"""
    response = client.models.generate_content(
        model=MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=LocatorFix,
            temperature=0.1,
        ),
    )
    return json.loads(response.text)


def save_log(entry):
    try:
        with open(LOG_FILE, "r") as f:
            log = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        log = []
    log.append(entry)
    with open(LOG_FILE, "w") as f:
        json.dump(log, f, indent=2)


def find_with_healing(driver, by, value, description):
    try:
        return driver.find_element(by, value)
    except NoSuchElementException:
        print(f"[PhoenixTest] Locator broken: {by}={value}. Asking Gemini to heal...")

    start = time.time()
    entry = {
        "time": datetime.now().isoformat(timespec="seconds"),
        "element": description,
        "old_locator": f"{by}={value}",
    }
    element = None
    try:
        fix = ask_gemini(description, by, value, clean_html(driver.page_source))
        entry["new_locator"] = fix["css_selector"]
        entry["confidence"] = fix["confidence"]
        entry["reason"] = fix["reason"]
        if fix["confidence"] >= CONFIDENCE_THRESHOLD:
            matches = driver.find_elements(By.CSS_SELECTOR, fix["css_selector"])
            if len(matches) == 1:
                element = matches[0]
    except Exception as e:
        entry["error"] = str(e)[:200]

    entry["seconds"] = round(time.time() - start, 1)
    entry["healed"] = element is not None
    save_log(entry)

    if element is None:
        raise NoSuchElementException(f"PhoenixTest could not heal: {description}")
    print(f"[PhoenixTest] Healed -> {entry['new_locator']} (confidence {entry['confidence']}, {entry['seconds']}s)")
    return element
