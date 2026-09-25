#!/usr/bin/env python3
"""One-time: seed Gunnar's 28 calibration verdicts (exported from the claude.ai artifact
into seed/**/*.json) into the Apps Script backend, keeping his original dates.

  python3 seed_verdicts.py          (needs config.json url + .token; idempotent per item)
"""
import glob
import json
import os
import time
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
cfg = json.load(open(os.path.join(HERE, "config.json")))
key = open(os.path.join(HERE, ".token")).read().strip()
url = cfg["url"]
assert url.endswith("/exec"), "config.json url must be the /exec URL"

files = sorted(glob.glob(os.path.join(HERE, "seed", "**", "*.json"), recursive=True))
print(f"{len(files)} verdict files")
ok = 0
for p in files:
    d = json.load(open(p))
    data = d.get("data", d)
    item = os.path.basename(p)[:-5]
    q = {"action": "set", "k": key, "item": item, "verdict": data.get("verdict", ""),
         "reason": data.get("reason", ""), "by": "Gunnar", "title": data.get("title", ""),
         "ts": (data.get("ts") or "2026-09-22") + "T12:00:00.000Z"}
    with urllib.request.urlopen(url + "?" + urllib.parse.urlencode(q), timeout=60) as r:
        res = json.loads(r.read().decode())
    print(item, res.get("status"), res.get("message", ""))
    ok += res.get("status") == "ok"
    time.sleep(0.4)
print(f"seeded {ok}/{len(files)}")
