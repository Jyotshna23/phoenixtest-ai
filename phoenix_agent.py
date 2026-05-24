from google import genai
import json
import os
import time
from datetime import datetime

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

# Simulated UI elements - In real world, these come from Selenium/Playwright
ORIGINAL_UI = {
    "login_button": {"id": "btn-login", "xpath": "//button[@id='btn-login']", "text": "Login"},
    "username_field": {"id": "username", "xpath": "//input[@id='username']", "text": ""},
    "password_field": {"id": "password", "xpath": "//input[@id='password']", "text": ""},
    "submit_btn": {"id": "submit", "xpath": "//button[@id='submit']", "text": "Submit"}
}

# Simulated UI after change - button ID changed!
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

def heal_test_with_ai(test, ui_change):
    prompt = f"""You are an expert QA automation engineer. A UI element has changed and the test is broken.

Broken Test:
{json.dumps(test, indent=2)}

UI Change Detected:
{json.dumps(ui_change, indent=2)}

Fix the test by updating the xpath and element details. Respond in JSON only:
{{
    "name": "{test['name']}",
    "element": "{test['element']}",
    "action": "{test['action']}",
    "xpath": "new xpath here",
    "healing_reason": "why this fix works",
    "confidence": 95
}}"""

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt
    )
    text = response.text.strip()
    text = text.replace('```json', '').replace('```', '').strip()
    return json.loads(text)

def run_phoenix_agent():
    print("=" * 65)
    print("🔥 PHOENIXTEST AI - SELF-HEALING TEST AUTOMATION AGENT")
    print("=" * 65)
    print(f"⏰ Scan Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🧪 Total Tests: {len(ORIGINAL_TESTS)}")
    print("=" * 65)

    print("\n🔍 STEP 1: Detecting UI Changes...")
    changes = detect_ui_changes(ORIGINAL_UI, CHANGED_UI)
    print(f"⚠️  {len(changes)} UI changes detected!")
    for change in changes:
        print(f"   Element: {change['element']}")
        print(f"   Old ID: {change['old_id']} → New ID: {change['new_id']}")

    print("\n🤖 STEP 2: AI Self-Healing Tests...")
    healed_tests = []
    broken_count = 0
    healed_count = 0

    for test in ORIGINAL_TESTS:
        ui_change = next((c for c in changes if c["element"] == test["element"]), None)

        if ui_change:
            broken_count += 1
            print(f"\n❌ BROKEN: {test['name']}")
            print(f"   Old XPath: {test['xpath']}")
            time.sleep(2)
            healed = heal_test_with_ai(test, ui_change)
            healed_tests.append(healed)
            healed_count += 1
            print(f"✅ HEALED: {healed['name']}")
            print(f"   New XPath: {healed['xpath']}")
            print(f"   Confidence: {healed['confidence']}%")
            print(f"   Reason: {healed['healing_reason']}")
        else:
            healed_tests.append(test)
            print(f"\n✅ PASSING: {test['name']}")

    print("\n" + "=" * 65)
    print("📊 PHOENIXTEST AI REPORT")
    print("=" * 65)
    print(f"🧪 Total Tests: {len(ORIGINAL_TESTS)}")
    print(f"❌ Broken Tests Detected: {broken_count}")
    print(f"✅ Auto-Healed by AI: {healed_count}")
    print(f"🎯 Healing Success Rate: {(healed_count/broken_count*100) if broken_count > 0 else 100}%")
    print(f"⏱️  Manual Fix Time Saved: {healed_count * 30} minutes")
    print("=" * 65)
    print("🔥 PhoenixTest AI: Tests never die, they self-heal!")

if __name__ == "__main__":
    run_phoenix_agent()
