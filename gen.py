#!/usr/bin/env python3
"""Build app.html for Tækifæravaktin from the Eignaradar data folder.

  python3 gen.py            -> app.html (then: python3 encrypt.py && git push)

Reads  Claude Projects/Eignaradar/data/docs/*.json  (one file per item; *.update.json
files are merged onto their base item), keeps score >= 2, and injects them plus the
backend config (config.json: url, token from .token, names) into app_template.html.
Secrets never leave the encrypted payload: app.html, content.json, config.json,
.token and .passphrase are gitignored; only content.enc and index.html are published.
"""
import glob
import json
import os
from datetime import date

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = "/Users/villithor/Library/CloudStorage/GoogleDrive-gunnar@lgt.is/My Drive/Claude Projects/Eignaradar/data"

items = {}
for p in sorted(glob.glob(os.path.join(DATA, "docs", "*.json"))):
    name = os.path.basename(p)[:-5]
    if name.endswith(".update"):
        continue
    with open(p) as f:
        d = json.load(f)
    d["id"] = name
    items[name] = d
for p in sorted(glob.glob(os.path.join(DATA, "docs", "*.update.json"))):
    base = os.path.basename(p)[:-len(".update.json")]
    if base in items:
        with open(p) as f:
            items[base].update(json.load(f))

shown = [d for d in items.values() if (d.get("score") or 0) >= 2]

cfg = {}
cfg_path = os.path.join(HERE, "config.json")
if os.path.exists(cfg_path):
    with open(cfg_path) as f:
        cfg = json.load(f)
tok_path = os.path.join(HERE, ".token")
if os.path.exists(tok_path):
    with open(tok_path) as f:
        cfg["token"] = f.read().strip()
cfg.setdefault("names", ["Gunnar", "Björn", "Sveinn"])

content = {"generated": date.today().isoformat(), "items": shown, "config": cfg}
with open(os.path.join(HERE, "content.json"), "w") as f:
    json.dump(content, f, ensure_ascii=False, indent=1)

with open(os.path.join(HERE, "app_template.html")) as f:
    tpl = f.read()
payload = json.dumps(content, ensure_ascii=False).replace("</", "<\\/")
with open(os.path.join(HERE, "app.html"), "w") as f:
    f.write(tpl.replace("__CONTENT_JSON__", payload))
print(f"app.html: {len(shown)} items shown of {len(items)}; backend {'SET' if cfg.get('url') else 'NOT SET'}")
