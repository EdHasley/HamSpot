"""Authenticated HTTPS dashboard; fixed privileged helper handles radio writes."""
import base64
import hashlib
import hmac
import json
import os
import ssl
import subprocess
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit
from radio import validate
from hosts import HOST_FILES, validate_hosts

ROOT=Path(__file__).resolve().parent
STATE=Path(os.getenv('HAMSPOT_STATE','/etc/hamspot'))

def command(args):
    try:
        p=subprocess.run(args,capture_output=True,text=True,timeout=5)
        return p.stdout.strip() or p.stderr.strip()
    except (OSError,subprocess.TimeoutExpired): return 'unavailable'

def status():
    c=json.loads((STATE/'config.json').read_text())
    units={u:command(['/usr/bin/systemctl','is-active',f'hamspot-{u}.service']) for u in ('radio','gateway')}
    logs=command(['/usr/bin/journalctl','-u','hamspot-radio','-u','hamspot-gateway','-n','80','--no-pager','-o','cat'])
    return {'demo':False,'callsign':c['callsign'],'mode':'DMR','reflector':c['selected_reflector'],'module':c['module'],'talkgroup':c['talkgroup'],'services':units,'serial_exists':Path(c['uart']).exists(),'logs':logs,'network_status':'Check gateway log for login acknowledgement; running alone does not prove connection','bridge':'not installed','nextion':'not installed'}

class Handler(SimpleHTTPRequestHandler):
    def __init__(self,*args,**kwargs): super().__init__(*args,directory=str(ROOT),**kwargs)
    def send_json(self,data,code=200):
        raw=json.dumps(data).encode();self.send_response(code)
        self.send_header('Content-Type','application/json');self.send_header('Cache-Control','no-store')
        self.send_header('Content-Length',str(len(raw)));self.end_headers();self.wfile.write(raw)
    def authenticated(self):
        try:
            auth=json.loads((STATE/'auth.json').read_text())
            scheme,encoded=self.headers.get('Authorization','').split(' ',1)
            if scheme!='Basic': raise ValueError()
            user,password=base64.b64decode(encoded,validate=True).decode().split(':',1)
            actual=hashlib.pbkdf2_hmac('sha256',password.encode(),bytes.fromhex(auth['salt']),200000).hex()
            if hmac.compare_digest(user,'admin') and hmac.compare_digest(actual,auth['hash']): return True
        except (ValueError,UnicodeError,OSError,KeyError): pass
        self.send_response(401);self.send_header('WWW-Authenticate','Basic realm="HamSpot"');self.send_header('Content-Length','0');self.end_headers();return False
    def do_GET(self):
        if not self.authenticated(): return
        if self.path=='/api/status': self.send_json(status())
        elif self.path=='/api/hosts':
            files={}
            for kind,name in HOST_FILES.items():
                path=STATE/name if kind=='dmr' else STATE/'hosts'/name
                files[kind]={'filename':name,'active':kind=='dmr','text':path.read_text() if path.exists() else ''}
            self.send_json(files)
        elif self.path in ('/api/config','/api/backup'):
            self.send_json(json.loads((STATE/'config.json').read_text()))
        elif self.path in ('/','/index.html','/dashboard-v2.html','/settings.html','/hdmi.html','/dashboard.js','/style.css'):
            if self.path in ('/','/index.html'): self.path='/dashboard-v2.html'
            super().do_GET()
        else: self.send_json({'error':'Not found'},404)
    def do_POST(self):
        if not self.authenticated(): return
        # Require same-origin browser requests; reject form-based and cross-site writes.
        origin=urlsplit(self.headers.get('Origin',''))
        if origin.scheme!='https' or origin.netloc!=self.headers.get('Host') or self.headers.get('Content-Type')!='application/json':
            self.send_json({'error':'Same-origin HTTPS JSON request required'},403);return
        try:
            n=int(self.headers.get('Content-Length','0'))
            if not 0<n<=65536: raise ValueError('Invalid request size')
            data=json.loads(self.rfile.read(n))
            if self.path=='/api/config': request={'action':'apply','config':validate(data)}
            elif self.path=='/api/hosts':
                request={'action':'hosts','kind':data['kind'],'text':validate_hosts(data['kind'],data['text'])}
            elif self.path in ('/api/start','/api/stop'): request={'action':self.path.split('/')[-1]}
            else: self.send_json({'error':'Not found'},404);return
            p=subprocess.run(['/usr/bin/sudo','-n','/usr/bin/python3','-I','/opt/hamspot/app/control-entry.py'],input=json.dumps(request),text=True,capture_output=True,timeout=100)
            result=json.loads(p.stdout) if p.stdout else {'ok':False,'error':'Radio helper failed'}
            self.send_json(result,200 if p.returncode==0 else 400)
        except (ValueError,KeyError,TypeError) as e: self.send_json({'error':str(e)},400)
        except (OSError,subprocess.TimeoutExpired): self.send_json({'error':'Service operation timed out; check diagnostics'},503)

if __name__=='__main__':
    httpd=ThreadingHTTPServer((os.getenv('HAMSPOT_HOST','0.0.0.0'),int(os.getenv('HAMSPOT_PORT','8443'))),Handler)
    context=ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.minimum_version=ssl.TLSVersion.TLSv1_2
    context.load_cert_chain(STATE/'tls.crt',STATE/'tls.key')
    httpd.socket=context.wrap_socket(httpd.socket,server_side=True)
    httpd.serve_forever()
