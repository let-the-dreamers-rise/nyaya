"""The ledger page, served to the phone's own browser from the phone itself.

Binds 127.0.0.1 and nothing else. The page loads no font, no script and no
image from anywhere; it is one file, and the only requests it makes go back
to this process. That is the whole privacy model and it is checkable with
`netstat` rather than with a policy document.
"""

from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from . import sources
from .witness import SCAM_WORDS, witness

DEFAULT_PORT = 8765


class Ledger:
    """Messages from one source plus the person's preferences on disk."""

    def __init__(self, source, home=None):
        self.source = source
        self.home = Path(home) if home else Path.home() / ".nyaya-money"
        self.messages = []
        self.prefs = {"nicknames": {}, "muted": [], "scam_words": list(SCAM_WORDS)}
        self._load_prefs()
        self.reload()

    @property
    def prefs_path(self):
        return self.home / "prefs.json"

    def _load_prefs(self):
        if self.prefs_path.exists():
            saved = json.loads(self.prefs_path.read_text(encoding="utf-8"))
            self.prefs.update({k: saved[k] for k in self.prefs if k in saved})

    def save_prefs(self):
        self.home.mkdir(parents=True, exist_ok=True)
        self.prefs_path.write_text(json.dumps(self.prefs, indent=2, sort_keys=True), encoding="utf-8")

    def set_prefs(self, incoming):
        clean = {
            "nicknames": {str(k): str(v) for k, v in dict(incoming.get("nicknames") or {}).items()},
            "muted": [str(x) for x in incoming.get("muted") or []],
            "scam_words": [str(x).lower() for x in incoming.get("scam_words") or SCAM_WORDS],
        }
        self.prefs = clean
        self.save_prefs()

    def reload(self):
        self.messages = sources.load(self.source)

    def result(self):
        out = witness(self.messages, self.prefs)
        out["source"] = self.source
        out["prefs"] = self.prefs
        return out


def make_handler(ledger):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):  # quiet on the phone
            pass

        def _send(self, code, body, ctype="application/json; charset=utf-8"):
            data = body if isinstance(body, bytes) else body.encode("utf-8")
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(data)

        def do_GET(self):
            if self.path == "/":
                return self._send(200, PAGE, "text/html; charset=utf-8")
            if self.path == "/api/witness":
                return self._send(200, json.dumps(ledger.result()))
            if self.path == "/api/prefs":
                return self._send(200, json.dumps(ledger.prefs))
            self._send(404, json.dumps({"error": "no such path"}))

        def do_POST(self):
            length = int(self.headers.get("Content-Length") or 0)
            raw = self.rfile.read(length) if length else b"{}"
            if self.path == "/api/prefs":
                try:
                    ledger.set_prefs(json.loads(raw.decode("utf-8") or "{}"))
                except (ValueError, AttributeError) as exc:
                    return self._send(400, json.dumps({"error": str(exc)}))
                return self._send(200, json.dumps(ledger.prefs))
            if self.path == "/api/refresh":
                ledger.reload()
                return self._send(200, json.dumps({"messages": len(ledger.messages)}))
            self._send(404, json.dumps({"error": "no such path"}))

    return Handler


def make_server(ledger, port=DEFAULT_PORT):
    """Loopback only. Port 0 asks the OS for a free one (tests)."""
    return ThreadingHTTPServer(("127.0.0.1", port), make_handler(ledger))


def serve(source, port=DEFAULT_PORT, home=None, announce=print):
    ledger = Ledger(source, home)
    server = make_server(ledger, port)
    announce("open http://127.0.0.1:{0}/ on this phone. Ctrl+C stops it.".format(server.server_port))
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


PAGE = r"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>What my phone knows about my money</title>
<style>
:root{--bg:#F7F8F5;--panel:#fff;--ink:#1B2430;--muted:#5C6670;--rule:#D6DBD2;--green:#0F6E56;--green-soft:#E3F0EA;--red:#B4532A;--red-soft:#F6E7DF}
@media(prefers-color-scheme:dark){:root{--bg:#141A1F;--panel:#1B232A;--ink:#E8ECE6;--muted:#97A19B;--rule:#2A343A;--green:#4FB894;--green-soft:#17302A;--red:#E08A5F;--red-soft:#3A2419}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:17px/1.5 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}
main{max-width:640px;margin:0 auto;padding:20px 16px 60px}
h1{font-size:1.5rem;line-height:1.2;margin:0 0 4px}h2{font-size:.8rem;letter-spacing:.08em;text-transform:uppercase;color:var(--muted);margin:28px 0 8px}
.sub{color:var(--muted);margin:0 0 6px}.private{display:inline-block;font-size:.85rem;color:var(--green);background:var(--green-soft);padding:4px 10px;border-radius:3px}
.row{background:var(--panel);border:1px solid var(--rule);padding:12px 14px;margin-top:8px;display:flex;gap:10px;align-items:flex-start}
.row.alert{border-left:4px solid var(--red);background:var(--red-soft)}.row .t{flex:1}
.ev{font-size:.75rem;color:var(--muted);white-space:nowrap;padding-top:3px;font-variant-numeric:tabular-nums}
button{font:inherit;background:none;border:1px solid var(--rule);color:var(--muted);border-radius:3px;padding:2px 8px;cursor:pointer}
button:focus-visible{outline:2px solid var(--green)}
.names{display:flex;flex-wrap:wrap;gap:6px}.names button{padding:6px 10px;color:var(--ink)}
.family{border:1px solid var(--green);background:var(--green-soft);padding:14px;margin-top:8px}.family strong{color:var(--green)}
.family p{margin:6px 0}.foot{margin-top:28px;font-size:.85rem;color:var(--muted)}
.empty{color:var(--muted);font-style:italic}
</style></head><body><main>
<h1>What my phone knows about my money</h1>
<p class="sub" id="span">Reading&hellip;</p>
<span class="private">Nothing leaves this phone. No server, no account, no model.</span>
<div id="alerts"></div>
<h2>The last 30 days</h2><div id="facts"></div>
<h2>Every month</h2><div id="recurring"></div>
<h2>What it has learned about you</h2>
<p class="sub" style="font-size:.9rem">Each line was found by searching your own payments. Tap &times; if one is wrong; it stays gone.</p>
<div id="beliefs"></div>
<h2>Names</h2><p class="sub" style="font-size:.9rem">Tap a payee to give it a name you recognise.</p><div class="names" id="names"></div>
<h2>Family</h2>
<div class="family"><p><strong>Free on this phone, forever.</strong> It is a file, not a subscription.</p>
<p>To put it on your parents&rsquo; phones with the scam alerts sent to you: <strong>Rs 499, once.</strong> Never monthly, never ads, never your data. If we disappear, it keeps working.</p>
<p class="sub" style="font-size:.85rem">Not available yet. This line is here so you know how it will pay for itself.</p></div>
<p class="foot" id="foot"></p>
</main>
<script>
let data=null;
function esc(s){return String(s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));}
function row(s,mutable){const ev=s.evidence||{};let e='';if('fired on' in ev)e=ev.right+' of '+ev['fired on'];else if('count' in ev)e=ev.count+'&times;';else if('minutes' in ev)e=ev.minutes+' min';
return '<div class="row '+(s.kind==='alert'?'alert':'')+'"><div class="t">'+esc(s.text)+'</div>'+(e?'<div class="ev">'+e+'</div>':'')+(mutable?'<button title="Mute this" aria-label="Mute" onclick="mute(\''+s.id+'\')">&times;</button>':'')+'</div>';}
function fill(id,list,mutable,empty){const el=document.getElementById(id);el.innerHTML=list.length?list.map(s=>row(s,mutable)).join(''):'<p class="empty">'+empty+'</p>';}
async function load(){const r=await fetch('/api/witness');data=await r.json();
document.getElementById('span').textContent=data.count?data.count+' transactions, '+data.span:'No bank messages found yet.';
const S=data.sentences||[];fill('alerts',S.filter(s=>s.kind==='alert'),true,'');
fill('facts',S.filter(s=>s.kind==='fact'&&!s.text.startsWith('Every month')),false,'Nothing in the last 30 days.');
fill('recurring',S.filter(s=>s.kind==='fact'&&s.text.startsWith('Every month')),false,'No monthly pattern yet.');
fill('beliefs',S.filter(s=>s.kind==='belief'),true,'Not enough payments yet to learn from. It needs a few weeks.');
const parties=[...new Set((data.transactions||[]).map(t=>t.party).filter(Boolean))];
document.getElementById('names').innerHTML=parties.map(p=>'<button onclick="rename(\''+esc(p)+'\')">'+esc(data.prefs.nicknames[p]||p)+'</button>').join('');
document.getElementById('foot').innerHTML=(data.muted||0)+' muted. <button onclick="restore()">Restore all</button>';}
async function put(){await fetch('/api/prefs',{method:'POST',body:JSON.stringify(data.prefs)});await load();}
function mute(id){data.prefs.muted.push(id);put();}
function restore(){data.prefs.muted=[];put();}
function rename(p){const n=prompt('Call '+p+':',data.prefs.nicknames[p]||'');if(n===null)return;if(n.trim())data.prefs.nicknames[p]=n.trim();else delete data.prefs.nicknames[p];put();}
load();
</script></body></html>
"""
