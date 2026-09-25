# Tækifæravaktin — læst mælaborð

Live: https://isfast-is.github.io/taekifaeravaktin/ (aðgangsorð hjá Gunnari).

Only `index.html` (passphrase gate + WebCrypto decrypt) and `content.enc` are published.
Working copy on the Mac mini: `~/repos/taekifaeravaktin`.

Rebuild after the daily run updates `Claude Projects/Eignaradar/data/docs/`:

    python3 gen.py && python3 encrypt.py && git add content.enc && git commit -m "vakt: update" && git push

Backend for marks: Google Apps Script `apps-script/` (Sheet "Tækifæravaktin – merkingar (gögn)"
in Claude Projects/Eignaradar). Deploy = Gunnar's click in the Apps Script UI (see
~/.claude/skills/apps-script-safe-deploy). `config.json` holds the /exec URL; `.token` the key.
