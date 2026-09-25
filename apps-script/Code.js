/**
 * Tækifæravaktin – bakendi fyrir merkingar.
 * Gögn: Google Sheet "Tækifæravaktin – merkingar (gögn)" í Claude Projects/Eignaradar.
 *   Flipi "stada": ein lína á hvert mál, síðasta vistun gildir.
 *   Flipi "saga":  hver einasta vistun, ekkert yfirskrifað.
 * Vefþjónn (GET):
 *   ?action=get&k=TOKEN                       -> {status, verdicts:{item:{verdict,reason,by,ts}}, history:[...]}
 *   ?action=set&k=TOKEN&item=..&verdict=..&reason=..&by=..  -> {status:"ok"}
 */
var SHEET_ID = '1kx32adfYkJRFppznXrrVP0DkhUXsq0Hln0Wgg149V7s';
var TOKEN = '5Ah9yKXOO218v7Omm3NRHQPT';
var VERDICTS = ['ahugavert', 'skoda', 'ekki', ''];

function out_(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj)).setMimeType(ContentService.MimeType.JSON);
}

function sheets_() {
  var ss = SpreadsheetApp.openById(SHEET_ID);
  var st = ss.getSheetByName('stada');
  if (!st) { st = ss.insertSheet('stada'); st.appendRow(['item', 'verdict', 'reason', 'by', 'ts', 'title']); st.setFrozenRows(1); }
  var sg = ss.getSheetByName('saga');
  if (!sg) { sg = ss.insertSheet('saga'); sg.appendRow(['ts', 'item', 'verdict', 'reason', 'by', 'title']); sg.setFrozenRows(1); }
  var dflt = ss.getSheetByName('Sheet1') || ss.getSheetByName('Blað1');
  if (dflt && ss.getSheets().length > 2) { try { ss.deleteSheet(dflt); } catch (e) {} }
  return { st: st, sg: sg };
}

function doGet(e) {
  var p = (e && e.parameter) || {};
  if (p.k !== TOKEN) return out_({ status: 'denied' });
  var lock = LockService.getScriptLock();
  lock.waitLock(20000);
  try {
    var s = sheets_();
    if (p.action === 'set') return out_(set_(s, p));
    return out_(get_(s, p));
  } finally { lock.releaseLock(); }
}

function get_(s, p) {
  var rows = s.st.getDataRange().getValues();
  var verdicts = {};
  for (var i = 1; i < rows.length; i++) {
    var r = rows[i]; if (!r[0]) continue;
    verdicts[r[0]] = { verdict: r[1], reason: r[2], by: r[3], ts: r[4], title: r[5] };
  }
  var hist = [];
  var hv = s.sg.getDataRange().getValues();
  var from = Math.max(1, hv.length - 400);
  for (var j = from; j < hv.length; j++) {
    var h = hv[j]; if (!h[1]) continue;
    hist.push({ ts: h[0], item: h[1], verdict: h[2], reason: h[3], by: h[4] });
  }
  return { status: 'ok', verdicts: verdicts, history: hist, updated: new Date().toISOString() };
}

function set_(s, p) {
  var item = String(p.item || '').trim();
  if (!item || !/^[a-z0-9-]{3,120}$/.test(item)) return { status: 'error', message: 'bad item' };
  var verdict = String(p.verdict || '').trim();
  if (VERDICTS.indexOf(verdict) < 0) return { status: 'error', message: 'bad verdict' };
  var reason = String(p.reason || '').slice(0, 600);
  var by = String(p.by || '').slice(0, 40) || 'óþekkt';
  var title = String(p.title || '').slice(0, 200);
  var ts = new Date().toISOString();
  if (p.ts && /^\d{4}-\d{2}-\d{2}/.test(String(p.ts))) ts = String(p.ts).slice(0, 25);
  s.sg.appendRow([ts, item, verdict, reason, by, title]);
  var rows = s.st.getDataRange().getValues();
  for (var i = 1; i < rows.length; i++) {
    if (rows[i][0] === item) { s.st.getRange(i + 1, 1, 1, 6).setValues([[item, verdict, reason, by, ts, title]]); return { status: 'ok', ts: ts }; }
  }
  s.st.appendRow([item, verdict, reason, by, ts, title]);
  return { status: 'ok', ts: ts };
}

/** Keyrðu þetta einu sinni í ritlinum til að heimila aðgang að Sheet-inu. */
function authorize() { sheets_(); Logger.log('ok'); }
