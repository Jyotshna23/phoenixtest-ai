# PhoenixTest AI

A self-healing Selenium locator helper. When a Selenium locator breaks, PhoenixTest AI sends the current page HTML to Google Gemini, gets back a replacement CSS selector, checks it against safety guardrails, and logs every attempt.

This is a personal learning project. The numbers below come from a small experiment on one public demo site, not a benchmark.

## How it works

1. A test calls `find_with_healing(driver, by, value, description)` instead of `driver.find_element(...)`.
2. If the normal lookup works, nothing else happens.
3. If it raises `NoSuchElementException`, the page HTML is cleaned (scripts, styles, SVG and comments removed) and sent to Gemini with a plain-English description of the element.
4. Gemini returns structured JSON (validated with a Pydantic schema): a CSS selector, a reason, and a confidence score.
5. Guardrails: the fix is accepted only if confidence is at least 75 and the selector matches exactly one element on the page. Otherwise the test fails with a clear error.
6. Every attempt (old locator, new locator, confidence, reason, seconds, healed or not) is appended to `healing_log.json`.

## Files

| File | Purpose |
|---|---|
| `healer.py` | Healing logic: Gemini call, schema validation, guardrails, logging |
| `tests/test_saucedemo.py` | Plain Selenium and PyTest tests (login, add to cart, checkout) on saucedemo.com |
| `tests/test_healing_rate.py` | Breaks 6 locators on purpose and checks the healed element is the correct one |
| `summary.py` | Reads `healing_log.json` and prints heal count and timings |
| `phoenix_agent.py` | Original version of the agent. It works on simulated UI snapshots, not a real browser |
| `.github/workflows/` | GitHub Actions workflow file (the Selenium tests are not run in CI yet) |

## Experiment results

Setup: saucedemo.com login page, 6 locators broken on purpose, model `gemini-3.8-flash`. For each one the test asserts that the healed element has the correct `id`, so a wrong but confident answer would fail.

| Broken locator | Healed to | Seconds |
|---|---|---|
| `id=usr-name` | `#user-name` | 153.7 |
| `id=pwd` | `#password` | 452.0 |
| `id=login-btn` | `#login-button` | 17.1 |
| `css=input.login-submit` | `#login-button` | 38.5 |
| `xpath=//input[@id='username-field']` | `[data-test="username"]` | 14.0 |
| `name=pass-word` | `#password` | 37.4 |

Result: 6 of 6 healed to the correct element.

About the timings: the first two runs were paused by my terminal while I was measuring, so 153.7 s and 452.0 s are not reliable. The other four took between 14 and 38 seconds. Latency is the main weakness of this approach.

## Limitations

- Small sample: 6 locators, one website, one page, broken by me on purpose.
- Confidence is the score Gemini reports about itself, not a measured accuracy.
- Only the first 30,000 characters of cleaned HTML are sent, so very large pages may be cut off.
- Each heal takes tens of seconds, which is too slow for large suites without caching.
- The Selenium tests need Chrome installed and are not part of the GitHub Actions workflow yet.

## Run it

```
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
set GEMINI_API_KEY=your_key_here
pytest tests\test_saucedemo.py -v
pytest tests\test_healing_rate.py -v -s
python summary.py
```

Never commit your API key.

## Next steps

- Expose the healer as a small FastAPI endpoint.
- Cache healed locators so each broken locator costs one Gemini call.
- Store results in SQLite and add a simple dashboard.
- Run the Selenium tests in GitHub Actions with headless Chrome.
