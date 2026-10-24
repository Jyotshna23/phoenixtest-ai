import json

with open("healing_log.json") as f:
    log = json.load(f)

total = len(log)
healed = [e for e in log if e.get("healed")]
times = [e["seconds"] for e in log if "seconds" in e]

print(f"Heal attempts : {total}")
print(f"Healed        : {len(healed)}")
print(f"Not healed    : {total - len(healed)}")
if total:
    print(f"Heal rate     : {len(healed) / total * 100:.0f}%")
if times:
    print(f"Avg time      : {sum(times) / len(times):.1f}s per heal")
print()
for e in log:
    status = "OK  " if e.get("healed") else "FAIL"
    print(f"{status} {e['old_locator']}  ->  {e.get('new_locator', '-')}")
