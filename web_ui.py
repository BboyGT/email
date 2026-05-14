"""Web-based GUI for EmailGen using built-in http.server."""
import os
import sys
import webbrowser
import http.server
import socketserver
import threading
from socketserver import ThreadingMixIn
import json
import time
from urllib.parse import urlparse, parse_qs

# Import core modules
from storage import Storage
from email_generator import EmailGenerator
from inbox_reader import InboxReader
from auto_signup import EnhancedAutoSignup
from email_monitor import EmailMonitor

# Initialize modules
storage = Storage()
generator = EmailGenerator()
reader = InboxReader()
auto_signup = EnhancedAutoSignup()
monitor = EmailMonitor(storage, reader)

PORT = 3030
# allow port override via command line
if len(sys.argv) > 1:
    try:
        PORT = int(sys.argv[1])
    except ValueError:
        pass

HTML = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>EmailGen - Email Automation</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', sans-serif; background: linear-gradient(135deg, #1a1a2e, #16213e); min-height: 100vh; color: #fff; }
        .header { background: linear-gradient(90deg, #0f3460, #e94560); padding: 20px; text-align: center; }
        .header h1 { font-size: 2.5em; }
        .container { max-width: 1100px; margin: 30px auto; padding: 20px; }
        .stats { display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin-bottom: 30px; }
        .stat-card { background: rgba(255,255,255,0.1); padding: 20px; border-radius: 10px; text-align: center; transition: transform 0.2s, background 0.2s; }
        .stat-card:hover { transform: translateY(-3px); background: rgba(255,255,255,0.15); }
        .stat-card h3 { font-size: 2em; color: #e94560; }
        .nav { display: flex; gap: 10px; margin-bottom: 20px; flex-wrap: wrap; }
        .nav button { padding: 12px 20px; background: rgba(255,255,255,0.1); border: none; border-radius: 8px; color: #fff; cursor: pointer; transition: background 0.2s, transform 0.15s; }
        .nav button:hover { background: rgba(233,69,96,0.6); transform: scale(1.03); }
        .nav button.active { background: #e94560; }
        .panel { background: rgba(255,255,255,0.05); padding: 25px; border-radius: 15px; margin-bottom: 20px; animation: fadeIn 0.3s ease; }
        .panel h2 { margin-bottom: 15px; border-bottom: 2px solid #e94560; padding-bottom: 10px; }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }
        .form-group { margin-bottom: 15px; }
        .form-group label { display: block; margin-bottom: 5px; }
        .form-group input { width: 100%; padding: 12px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.2); background: rgba(255,255,255,0.1); color: #fff; transition: border-color 0.2s; }
        .form-group input:focus { outline: none; border-color: #e94560; }
        .btn { padding: 12px 24px; border: none; border-radius: 8px; cursor: pointer; font-size: 1em; transition: transform 0.15s, opacity 0.2s; }
        .btn:hover { transform: scale(1.04); }
        .btn:active { transform: scale(0.97); }
        .btn:disabled { opacity: 0.5; cursor: not-allowed; transform: none; }
        .btn-primary { background: linear-gradient(90deg, #e94560, #0f3460); color: #fff; }
        .btn-danger { background: #dc3545; color: #fff; }
        .btn-success { background: #28a745; color: #fff; }
        table { width: 100%; border-collapse: collapse; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid rgba(255,255,255,0.1); }
        th { background: rgba(233,69,96,0.2); color: #e94560; }
        .table-wrap { overflow-x: auto; -webkit-overflow-scrolling: touch; }
        .code-box { background: #1a1a2e; padding: 15px; border-radius: 8px; margin: 10px 0; border-left: 4px solid #e94560; display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 10px; }
        .code { font-size: 1.4em; color: #e94560; font-weight: bold; }
        .result { margin-top: 15px; padding: 10px; border-radius: 8px; animation: fadeIn 0.3s ease; }
        .result.ok { background: rgba(40,167,69,0.2); }
        .result.err { background: rgba(220,53,69,0.2); }
        .hidden { display: none; }
        .loading { opacity: 0.6; pointer-events: none; }
        @media (max-width: 900px) {
            .stats { grid-template-columns: repeat(2, 1fr); }
            .container { padding: 12px; margin: 15px auto; }
            .header h1 { font-size: 1.8em; }
        }
        @media (max-width: 600px) {
            .stats { grid-template-columns: 1fr 1fr; gap: 10px; }
            .stat-card { padding: 14px; }
            .stat-card h3 { font-size: 1.5em; }
            .nav { gap: 6px; }
            .nav button { padding: 10px 14px; font-size: 0.9em; flex: 1 1 auto; text-align: center; }
            .panel { padding: 15px; border-radius: 10px; }
            .btn { padding: 10px 18px; font-size: 0.9em; }
            th, td { padding: 8px 6px; font-size: 0.85em; }
            .header { padding: 15px; }
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>EmailGen</h1>
        <p>Email Automation & Verification Monitor</p>
    </div>
    <div class="container">
        <div class="stats">
            <div class="stat-card"><h3 id="email-count">0</h3><p>Emails</p></div>
            <div class="stat-card"><h3 id="phone-count">0</h3><p>Phones</p></div>
            <div class="stat-card"><h3 id="site-count">0</h3><p>Websites</p></div>
            <div class="stat-card"><h3 id="code-count">0</h3><p>Codes</p></div>
        </div>
        <div class="nav">
            <button class="active" onclick="show('generate', event)">Generate</button>
            <button onclick="show('emails', event)">Emails</button>
            <button onclick="show('phones', event)">Phones</button>
            <button onclick="show('monitor', event)">Monitor</button>
            <button onclick="show('fake', event)">Fake Profiles</button>
            <button onclick="show('autosignup', event)">Auto Signup</button>
        </div>
        
        <div id="generate" class="panel">
            <h2>Generate Emails</h2>
            <div class="form-group">
                <label>Number of emails:</label>
                <input type="number" id="gen-count" value="10" min="1" max="1000">
            </div>
            <button class="btn btn-primary" onclick="generateEmails()">Generate</button>
            <div id="gen-result"></div>
        </div>
        
        <div id="emails" class="panel hidden">
            <h2>Saved Emails</h2>
            <div style="display:flex;gap:10px;flex-wrap:wrap;align-items:center;margin-bottom:12px">
                <button class="btn btn-primary" onclick="loadEmails()">Refresh</button>
                <button class="btn btn-danger" onclick="deleteSelected()">Delete Selected</button>
                <label style="cursor:pointer"><input type="checkbox" id="selectAll" onchange="toggleSelectAll()"> Select All</label>
            </div>
            <div class="table-wrap">
            <table><thead><tr><th></th><th>ID</th><th>Email</th><th>Provider</th><th>Action</th></tr></thead><tbody id="emails-tbody"></tbody></table>
            </div>
        </div>
        
        <div id="phones" class="panel hidden">
            <h2>Saved Phones</h2>
            <button class="btn btn-primary" onclick="loadPhones()" style="margin-bottom:12px">Refresh</button>
            <div class="table-wrap">
            <table><thead><tr><th>ID</th><th>Phone</th><th>Country</th><th>Action</th></tr></thead><tbody id="phones-tbody"></tbody></table>
            </div>
        </div>
        
        <div id="monitor" class="panel hidden">
            <h2>Monitor Inboxes</h2>
            <div class="form-group">
                <label>Website URL to monitor:</label>
                <input type="text" id="mon-url" placeholder="https://example.com">
            </div>
            <button class="btn btn-primary" onclick="addMonitor()">Add Site</button>
            <h3>Monitored Sites</h3>
            <div id="mon-sites"></div>
            <h3>Detected Codes</h3>
            <div id="mon-codes"></div>
            <button class="btn btn-success" onclick="startMonitor()">Start Monitoring</button>
        </div>
        
        <div id="autosignup" class="panel hidden">
            <h2>Auto Signup</h2>
            <div class="form-group"><input type="text" id="signup-url" placeholder="Signup URL"></div>
            <div class="form-group"><input type="number" id="signup-count" value="5"></div>
            <button class="btn btn-success" onclick="doSignup()">Start</button>
            <div id="signup-result"></div>
        </div>
        
        <div id="fake" class="panel hidden">
            <h2>Fake Profile Generator</h2>
            <div class="form-group">
                <label>Number of profiles:</label>
                <input type="number" id="fake-count" value="10" min="1" max="100">
            </div>
            <button class="btn btn-primary" onclick="generateFakes()">Generate</button>
            <div id="fake-result"></div>
        </div>
    </div>
    <script>
    function show(id, event) {
        document.querySelectorAll('.panel').forEach(function(p) { p.classList.add('hidden'); });
        document.querySelectorAll('.nav button').forEach(function(b) { b.classList.remove('active'); });
        var el = document.getElementById(id);
        if (el) el.classList.remove('hidden');
        if (event && event.target) event.target.classList.add('active');
        if (id === 'emails') loadEmails();
        if (id === 'phones') loadPhones();
        if (id === 'monitor') loadMonitor();
        stats();
    }
    function apiCall(url, opts) {
        return fetch(url, opts || {}).then(function(r) {
            if (!r.ok) throw new Error('API error: ' + r.status);
            return r;
        }).catch(function(err) {
            console.error('Fetch failed:', url, err);
            throw err;
        });
    }
    function stats() {
        apiCall('/api/stats').then(function(r) { return r.json(); }).then(function(d) {
            document.getElementById('email-count').innerText = d.emails || 0;
            document.getElementById('phone-count').innerText = d.phones || 0;
            document.getElementById('site-count').innerText = d.sites || 0;
            document.getElementById('code-count').innerText = d.codes || 0;
        }).catch(function() {});
    }
    function generateEmails() {
        var btn = event.target; btn.disabled = true; btn.innerText = 'Generating...';
        var n = document.getElementById('gen-count').value;
        apiCall('/api/generate?count=' + n).then(function(r) { return r.json(); }).then(function(d) {
            document.getElementById('gen-result').innerHTML = '<div class="result ok">Generated ' + d.count + ' emails!</div>';
            stats();
        }).catch(function() {
            document.getElementById('gen-result').innerHTML = '<div class="result err">Failed to generate emails.</div>';
        }).finally(function() { btn.disabled = false; btn.innerText = 'Generate'; });
    }
    function loadEmails() {
        apiCall('/api/emails').then(function(r) { return r.json(); }).then(function(d) {
            var html = '';
            for (var i = 0; i < d.length; i++) {
                var e = d[i];
                html += '<tr><td><input type="checkbox" class="email-select" value="' + e.id + '"></td><td>' + e.id + '</td><td>' + e.email + '</td><td>' + e.provider + '</td><td><button class="btn btn-danger" onclick="delEmail(' + e.id + ')">X</button></td></tr>';
            }
            document.getElementById('emails-tbody').innerHTML = html;
        }).catch(function() {
            document.getElementById('emails-tbody').innerHTML = '<tr><td colspan="5" style="text-align:center;color:#e94560">Failed to load emails</td></tr>';
        });
    }
    function toggleSelectAll() {
        var checked = document.getElementById('selectAll').checked;
        document.querySelectorAll('.email-select').forEach(function(c) { c.checked = checked; });
    }
    function deleteSelected() {
        var ids = [];
        document.querySelectorAll('.email-select:checked').forEach(function(c) { ids.push(c.value); });
        if (ids.length === 0) { alert('Select emails first!'); return; }
        if (!confirm('Delete ' + ids.length + ' email(s)?')) return;
        apiCall('/api/bulk_delete?ids=' + ids.join(','), { method: 'DELETE' }).then(function() {
            loadEmails();
            stats();
        }).catch(function() { alert('Failed to delete emails.'); });
    }
    function delEmail(id) {
        apiCall('/api/delete_email/' + id, { method: 'DELETE' }).then(function() {
            loadEmails();
            stats();
        }).catch(function() { alert('Failed to delete email.'); });
    }
    function loadPhones() {
        apiCall('/api/phones').then(function(r) { return r.json(); }).then(function(d) {
            var html = '';
            for (var i = 0; i < d.length; i++) {
                var p = d[i];
                html += '<tr><td>' + p.id + '</td><td>' + p.phone + '</td><td>' + p.country + '</td><td><button class="btn btn-danger" onclick="delPhone(' + p.id + ')">X</button></td></tr>';
            }
            document.getElementById('phones-tbody').innerHTML = html;
        }).catch(function() {
            document.getElementById('phones-tbody').innerHTML = '<tr><td colspan="4" style="text-align:center;color:#e94560">Failed to load phones</td></tr>';
        });
    }
    function delPhone(id) {
        apiCall('/api/delete_phone/' + id, { method: 'DELETE' }).then(function() {
            loadPhones();
            stats();
        }).catch(function() { alert('Failed to delete phone.'); });
    }
    function addMonitor() {
        var url = document.getElementById('mon-url').value;
        if (!url) { alert('Enter a URL first!'); return; }
        apiCall('/api/add_monitor?url=' + encodeURIComponent(url)).then(function() {
            document.getElementById('mon-url').value = '';
            loadMonitor();
            stats();
        }).catch(function() { alert('Failed to add monitor.'); });
    }
    function loadMonitor() {
        apiCall('/api/sites').then(function(r) { return r.json(); }).then(function(d) {
            var html = '';
            for (var i = 0; i < d.length; i++) {
                var s = d[i];
                html += '<div class="code-box">' + s.name + ' (' + s.domain + ') <button class="btn btn-danger" onclick="remMonitor(' + s.id + ')">X</button></div>';
            }
            document.getElementById('mon-sites').innerHTML = html || '<p style="opacity:0.5">No sites monitored</p>';
        }).catch(function() {});
        apiCall('/api/codes').then(function(r) { return r.json(); }).then(function(d) {
            var html = '';
            for (var i = 0; i < d.length; i++) {
                var c = d[i];
                html += '<div class="code-box"><strong>' + c.email + '</strong><br><span class="code">' + c.code + '</span></div>';
            }
            document.getElementById('mon-codes').innerHTML = html || '<p style="opacity:0.5">No codes detected</p>';
        }).catch(function() {});
    }
    function remMonitor(id) {
        apiCall('/api/remove_monitor/' + id, { method: 'DELETE' }).then(function() {
            loadMonitor();
            stats();
        }).catch(function() { alert('Failed to remove monitor.'); });
    }
    function startMonitor() {
        var btn = event.target; btn.disabled = true; btn.innerText = 'Monitoring...';
        apiCall('/api/monitor_inboxes').then(function(r) { return r.json(); }).then(function(d) {
            loadMonitor();
            stats();
        }).catch(function() {
            alert('Monitoring failed.');
        }).finally(function() { btn.disabled = false; btn.innerText = 'Start Monitoring'; });
    }
    function copyAll() {
        apiCall('/api/codes').then(function(r) { return r.json(); }).then(function(d) {
            var text = d.map(function(c) { return c.email + ' | ' + c.code; }).join('\n');
            navigator.clipboard.writeText(text);
            alert('Copied to clipboard!');
        }).catch(function() { alert('Failed to copy.'); });
    }
    function generateFakes() {
        var btn = event.target; btn.disabled = true; btn.innerText = 'Generating...';
        var n = document.getElementById('fake-count').value;
        apiCall('/api/fake_profiles?count=' + n).then(function(r) { return r.json(); }).then(function(d) {
            document.getElementById('fake-result').innerHTML = '<div class="result ok">Generated ' + d.count + ' fake profiles!</div>';
            stats();
        }).catch(function() {
            document.getElementById('fake-result').innerHTML = '<div class="result err">Failed to generate profiles.</div>';
        }).finally(function() { btn.disabled = false; btn.innerText = 'Generate'; });
    }
    function doSignup() {
        var btn = event.target; btn.disabled = true; btn.innerText = 'Signing up...';
        var url = document.getElementById('signup-url').value;
        var count = document.getElementById('signup-count').value;
        if (!url) { alert('Enter a signup URL first!'); btn.disabled = false; btn.innerText = 'Start'; return; }
        apiCall('/api/autosignup?url=' + encodeURIComponent(url) + '&count=' + count).then(function(r) { return r.json(); }).then(function(d) {
            document.getElementById('signup-result').innerHTML = '<div class="result ' + (d.success > 0 ? 'ok' : 'err') + '">' + d.success + '/' + d.total + ' signups successful</div>';
            stats();
        }).catch(function() {
            document.getElementById('signup-result').innerHTML = '<div class="result err">Signup failed.</div>';
        }).finally(function() { btn.disabled = false; btn.innerText = 'Start'; });
    }
    // Init
    stats();
    </script>
</body>
</html>"""

class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/' or self.path == '/index.html':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(HTML.encode())
        elif self.path.startswith('/api/'):
            self.handle_api()
        else:
            super().do_GET()
    
    def do_DELETE(self):
        if self.path.startswith('/api/'):
            self.handle_api()
        else:
            self.send_error(501)
    
    def handle_api(self):
        # Extract path without query string
        path = self.path.split('?')[0][5:]
        
        if path == 'stats':
            self.json_response({
                'emails': storage.get_email_count(),
                'phones': storage.get_phone_count(),
                'sites': len(monitor.get_monitored_sites()),
                'codes': len(monitor.detected_codes)
            })
        
        elif path == 'emails':
            emails = storage.get_all_emails()
            self.json_response([{'id': e.id, 'email': e.email, 'provider': e.provider} for e in emails])
        
        elif path == 'phones':
            phones = storage.get_all_phones()
            self.json_response([{'id': p.id, 'phone': p.phone, 'country': p.country} for p in phones])
        
        elif path == 'sites':
            sites = monitor.get_monitored_sites()
            self.json_response([{'id': s.id, 'name': s.name, 'domain': s.domain} for s in sites])
        
        elif path == 'monitor_inboxes':
            # Monitor all email inboxes
            from utils import extract_verification_codes
            emails = storage.get_all_emails()
            results = []
            for email_entry in emails:
                try:
                    inbox = reader.check_inbox(email_entry.email)
                    for msg in inbox:
                        search_text = f"{msg.subject} {msg.body}"
                        codes = extract_verification_codes(search_text)
                        if codes:
                            results.append({
                                'email': email_entry.email,
                                'code': codes[0],
                                'subject': msg.subject,
                                'from_addr': msg.from_addr
                            })
                except Exception as e:
                    pass
            self.json_response({'checked': len(emails), 'codes_found': len(results)})
        
        elif path == 'codes':
            # Get all messages from all inboxes
            from utils import extract_verification_codes
            emails = storage.get_all_emails()
            all_messages = []
            for email_entry in emails:
                try:
                    inbox = reader.check_inbox(email_entry.email)
                    for msg in inbox:
                        search_text = f"{msg.subject} {msg.body}"
                        codes = extract_verification_codes(search_text)
                        code = codes[0] if codes else 'N/A'
                        all_messages.append({
                            'email': email_entry.email,
                            'code': code,
                            'subject': msg.subject,
                            'from_addr': msg.from_addr,
                            'body': msg.body[:200] if msg.body else ''
                        })
                except Exception as e:
                    pass
            self.json_response(all_messages)
        
        elif path.startswith('generate'):
            from urllib.parse import urlparse
            qs = urlparse(self.path).query
            from urllib.parse import parse_qs
            params = parse_qs(qs)
            count = int(params.get('count', [1])[0]) if params.get('count') else 1
            for i in range(count):
                email = generator.generate_single()
                storage.add_email(email.email, email.password, email.provider)
            self.json_response({'count': count})
        
        elif path.startswith('fake_profiles'):
            qs = urlparse(self.path).query
            params = parse_qs(qs)
            count = int(params.get('count', ['1'])[0])
            from utils.helpers import generate_fake_profile
            profiles = []
            for i in range(count):
                profile = generate_fake_profile()
                profiles.append(profile)
                storage.add_email(profile['email'], profile['password'], 'fake')
            self.json_response({'count': count, 'profiles': profiles})
        
        elif path.startswith('add_monitor'):
            qs = urlparse(self.path).query
            params = parse_qs(qs)
            url = params.get('url', [''])[0]
            if url:
                monitor.add_site(url, None)
            self.json_response({'ok': True})
        
        elif path == 'start_monitor':
            results = monitor.monitor_all(max_duration=30)
            self.json_response({'codes': len(results)})
        
        elif path.startswith('autosignup'):
            qs = urlparse(self.path).query
            params = parse_qs(qs)
            url = params.get('url', [''])[0]
            count = int(params.get('count', ['1'])[0])
            if url:
                emails = storage.get_all_emails()[:count]
                email_list = [e.email for e in emails]
                res = auto_signup.bulk_signup(url, email_list, 1)
                success = sum(1 for r in res if r['success'])
                self.json_response({'success': success, 'total': len(res)})
            else:
                self.json_response({'success': 0, 'total': 0})
        
        elif path.startswith('delete_email/'):
            eid = int(path.split('/')[-1])
            storage.delete_email_by_id(eid)
            self.json_response({'ok': True})
        
        elif path.startswith('delete_phone/'):
            pid = int(path.split('/')[-1])
            storage.delete_phone_by_id(pid)
            self.json_response({'ok': True})
        
        elif path.startswith('bulk_delete'):
            qs = urlparse(self.path).query
            params = parse_qs(qs)
            ids = params.get('ids', [''])[0]
            if ids:
                for id_str in ids.split(','):
                    try:
                        storage.delete_email_by_id(int(id_str))
                    except:
                        pass
            self.json_response({'ok': True})
        
        elif path.startswith('remove_monitor/'):
            mid = int(path.split('/')[-1])
            monitor.remove_site(mid)
            self.json_response({'ok': True})
        
        else:
            self.json_response({'error': 'Unknown endpoint'})
    
    def json_response(self, data):
        import json
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())


class ThreadingTCPServer(ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = True

def run_server(port=8000):
    with ThreadingTCPServer(("", port), Handler) as httpd:
        print(f"\n[OK] EmailGen Web Interface")
        print(f"[OK] Server: http://localhost:{port}")
        print(f"[OK] Opening browser...")
        webbrowser.open(f"http://localhost:{port}")
        print("\n[INFO] Press Ctrl+C to stop\n")
        httpd.serve_forever()


if __name__ == "__main__":
    run_server(PORT)
