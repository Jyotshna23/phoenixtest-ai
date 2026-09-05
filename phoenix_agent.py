import json
import os
import time
import logging
from datetime import datetime
from google import genai
from google.genai import types
from pydantic import BaseModel, Field

# Enterprise Logging Framework Setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler()]
)

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
MODEL = "gemini-2.5-flash"
CONFIDENCE_THRESHOLD = 75

# Simulated UI Elements Architecture
ORIGINAL_UI = {
    "login_button": {"id": "btn-login", "xpath": "//button[@id='btn-login']", "text": "Login"},
    "username_field": {"id": "username", "xpath": "//input[@id='username']", "text": ""},
    "password_field": {"id": "password", "xpath": "//input[@id='password']", "text": ""},
    "submit_btn": {"id": "submit", "xpath": "//button[@id='submit']", "text": "Submit"}
}

CHANGED_UI = {
    "login_button": {"id": "btn-signin", "xpath": "//button[@id='btn-signin']", "text": "Sign In"},
    "username_field": {"id": "user-email", "xpath": "//input[@id='user-email']", "text": ""},
    "password_field": {"id": "user-pwd", "xpath": "//input[@id='user-pwd']", "text": ""},
    "submit_btn": {"id": "signin-submit", "xpath": "//button[@id='signin-submit']", "text": "Sign In"}
}

ORIGINAL_TESTS = [
    {"name": "Login Button Click", "element": "login_button", "action": "click", "xpath": "//button[@id='btn-login']"},
    {"name": "Enter Username", "element": "username_field", "action": "type", "xpath": "//input[@id='username']"},
    {"name": "Enter Password", "element": "password_field", "action": "type", "xpath": "//input[@id='password']"},
    {"name": "Submit Form", "element": "submit_btn", "action": "click", "xpath": "//button[@id='submit']"}
]

class HealingResponseSchema(BaseModel):
    name: str = Field(description="The original name of the test instance")
    element: str = Field(description="The key identifier of the UI target element")
    action: str = Field(description="The technical automation execution command type")
    xpath: str = Field(description="The newly generated, corrected and valid XPath string parameter")
    healing_reason: str = Field(description="Logical explanation for why this new xpath selection is accurate")
    confidence: int = Field(description="Integer rating score from 0 to 100 based on mapping accuracy")

def detect_ui_changes(original, changed):
    changes = []
    for element, props in original.items():
        if element in changed:
            if props["id"] != changed[element]["id"]:
                changes.append({
                    "element": element,
                    "old_id": props["id"],
                    "new_id": changed[element]["id"],
                    "old_xpath": props["xpath"],
                    "new_xpath": changed[element]["xpath"]
                })
    return changes

def heal_test_with_ai(test, ui_change, retries=2):
    prompt = f"""You are an elite QA automation engineer. A UI element change has broken an active execution test block.
    Target Test Meta: {json.dumps(test)}
    Telemetry UI Change Event: {json.dumps(ui_change)}
    Analyse metadata properties and map out the correct new xpath parameters."""

    for attempt in range(retries + 1):
        try:
            response = client.models.generate_content(
                model=MODEL,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=HealingResponseSchema,
                    temperature=0.1
                )
            )
            return json.loads(response.text)
        except Exception as e:
            if attempt == retries:
                logging.error(f"Autonomous Healing Pipeline Context Fault: {e}")
                return {
                    "name": test['name'],
                    "element": test['element'],
                    "action": test['action'],
                    "xpath": test['xpath'],
                    "healing_reason": f"Self-healing session execution error boundary caught: {str(e)[:100]}",
                    "confidence": 0
                }
            time.sleep(3)

def run_phoenix_agent():
    logging.info("=" * 60)
    logging.info("PHOENIXTEST AI ENGINE — INITIALIZING SELF-HEALING SUITE")
    logging.info("=" * 60)
    logging.info(f"Scan Lifecyle Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logging.info(f"Total Test Sequence Count: {len(ORIGINAL_TESTS)}")
    logging.info("=" * 60)

    logging.info("Executing Pipeline Node Step 1: Parsing UI Delta Metrics...")
    changes = detect_ui_changes(ORIGINAL_UI, CHANGED_UI)
    logging.info(f"Telemetry Scan Results: {len(changes)} active structural changes caught.")

    logging.info("Executing Pipeline Node Step 2: Running Generative Diagnostics...")
    broken_count = 0
    healed_count = 0

    for test in ORIGINAL_TESTS:
        ui_change = next((c for c in changes if c["element"] == test["element"]), None)

        if ui_change:
            broken_count += 1
            logging.warning(f"CRITICAL FAULT DETECTED: Core Test Instance Broken -> [ {test['name']} ]")
            logging.info(f"   Decommissioned Legacy XPath Target: {test['xpath']}")
            
            time.sleep(1)
            healed = heal_test_with_ai(test, ui_change)
            
            if healed["confidence"] >= CONFIDENCE_THRESHOLD:
                healed_count += 1
                logging.info(f"   SUCCESSFULLY HEALED: Target [ {healed['name']} ] Repaired Programmatically.")
                logging.info(f"   Patched Active XPath Target: {healed['xpath']}")
                logging.info(f"   AI Engine Mapping Confidence Index: {healed['confidence']}%")
                logging.info(f"   Diagnostics Resolution Trace: {healed['healing_reason']}")
            else:
                logging.error(f"   AUTOMATED HEALING ABORTED: Confidence index below safety threshold boundary.")
                logging.error(f"   Reason Code Log: {healed['healing_reason']}")
        else:
            logging.info(f"PASSING INTEGRITY CHECK: Test Node Clear -> [ {test['name']} ]")

    logging.info("=" * 60)
    logging.info("PHOENIXTEST SUMMARY METRICS REPORT")
    logging.info("=" * 60)
    logging.info(f"Total Evaluated Nodes: {len(ORIGINAL_TESTS)}")
    logging.info(f"Total Intercepted Faults: {broken_count}")
    logging.info(f"Total Successful Deployments: {healed_count}")
    success_rate = (healed_count / broken_count * 100) if broken_count > 0 else 100.0
    logging.info(f"Automated Self-Healing Operational Success Ratio: {success_rate:.2f}%")
    logging.info("=" * 60)
    logging.info("PhoenixTest Agent Lifecycle Management Complete.")

if __name__ == "__main__":
    run_phoenix_agent()
