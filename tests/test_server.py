import base64
import configparser
import hashlib
import importlib.util
import io
import json
import ssl
import subprocess
import sys
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from pathlib import Path
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'app'))
import radio
import hosts
import server
import control

def default(): return json.loads((ROOT/'radio/defaults.json').read_text())
def enabled():
    c=default();c.update(callsign='N0TEST',dmr_id=1234567,rx_frequency=433200000,tx_frequency=433200000,radio_enabled=True,network_enabled=True,selected_reflector='TST',reflectors=[dict(id='TST',label='Private test',host='reflector.example.org',port=62040,password='passw0rd')]);return c

class RadioTests(unittest.TestCase):
    def test_disabled_first_boot(self):
        c=radio.validate(default());self.assertFalse(c['radio_enabled']);self.assertFalse(c['network_enabled'])
        p=configparser.ConfigParser();p.read_string(radio.render(c)['MMDVM-Host.ini'])
        for mode in ('FM','POCSAG','D-Star','FM Network','DMR Network'): self.assertEqual(p[mode]['Enable'],'0')
    def test_private_host_and_local_port_mapping(self):
        rendered=radio.render(enabled());h=configparser.ConfigParser();h.read_string(rendered['MMDVM-Host.ini']);g=configparser.ConfigParser();g.read_string(rendered['DMRGateway.ini'])
        self.assertEqual(h['Modem']['UARTPort'],'/dev/ttyAMA0');self.assertEqual(h['DMR Network']['GatewayPort'],g['General']['LocalPort']);self.assertEqual(h['DMR Network']['LocalPort'],g['General']['RptPort']);self.assertEqual(g['XLX Network']['Port'],'62040');self.assertEqual(g['XLX Network']['Startup'],'TST');self.assertIn('TST;reflector.example.org;4005',rendered['XLXHosts.txt'])
    def test_reject_invalid_and_injection(self):
        for field,value in [('callsign','N0CALL\nEnable=1'),('dmr_id',True),('uart','/etc/passwd'),('rx_frequency',433.2),('module','AA'),('network_enabled','yes')]:
            with self.subTest(field=field),self.assertRaises(ValueError): radio.validate(dict(enabled(),**{field:value}))
        with self.assertRaises(ValueError):radio.validate(dict(default(),radio_enabled=True))
    def test_host_lists(self):
        for kind,prefix in [('dcs','DCS'),('xrf','XRF'),('ref','REF')]:
            self.assertIn(prefix,hosts.validate_hosts(kind,f'# private\n{prefix}001 reflector.example.org\n'))
        for kind,text in [('dmr','TST;host;9999'),('xrf','../etc host'),('ref','REF001 bad;host'),('dmr','TST;host;4005\nTST;other;4001')]:
            with self.assertRaises(ValueError):hosts.validate_hosts(kind,text)
    def test_dmr_import_keeps_custom_port_and_password(self):
        c=hosts.import_dmr(enabled(),'TST;new.example.org;4002\n')
        self.assertEqual(c['reflectors'][0]['port'],62040);self.assertEqual(c['module'],'B');self.assertEqual(c['reflectors'][0]['host'],'new.example.org')
    def test_apply_rolls_back_on_start_failure(self):
        with tempfile.TemporaryDirectory() as d,patch.object(control,'STATE',Path(d)),patch.object(control,'atomic',lambda p,t:p.write_text(t)):
            old=default()
            for name,text in dict(radio.render(old),**{'config.json':json.dumps(old)}).items():(Path(d)/name).write_text(text)
            def run(*args,**kwargs):
                if args[0]=='start':raise subprocess.CalledProcessError(1,args)
                return subprocess.CompletedProcess(args,1,'','')
            with patch.object(control,'run',run),self.assertRaises(subprocess.CalledProcessError):control.apply(enabled())
            self.assertEqual(json.loads((Path(d)/'config.json').read_text()),old)

class ApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp=tempfile.TemporaryDirectory();cls.state=Path(cls.tmp.name)
        (cls.state/'config.json').write_text(json.dumps(default()))
        salt=b'1234567890123456';(cls.state/'auth.json').write_text(json.dumps({'salt':salt.hex(),'hash':hashlib.pbkdf2_hmac('sha256',b'test-password',salt,200000).hex()}))
        cls.prev=server.STATE;server.STATE=cls.state
        cls.http=server.ThreadingHTTPServer(('127.0.0.1',0),server.Handler)
        cls.url='http://127.0.0.1:'+str(cls.http.server_port)
        cls.thread=threading.Thread(target=cls.http.serve_forever,daemon=True);cls.thread.start()
        cls.auth='Basic '+base64.b64encode(b'admin:test-password').decode()
    @classmethod
    def tearDownClass(cls):
        cls.http.shutdown();cls.http.server_close();cls.thread.join();server.STATE=cls.prev;cls.tmp.cleanup()
    def request(self,path,data=None,origin=None):
        headers={'Authorization':self.auth}
        if data is not None:headers['Content-Type']='application/json'
        if origin:headers['Origin']=origin
        return urllib.request.urlopen(urllib.request.Request(self.url+path,data=None if data is None else json.dumps(data).encode(),headers=headers))
    def test_auth_and_no_static_source_leak(self):
        with self.assertRaises(urllib.error.HTTPError) as cm:urllib.request.urlopen(self.url+'/api/config')
        self.assertEqual(cm.exception.code,401)
        with self.assertRaises(urllib.error.HTTPError) as cm:self.request('/server.py')
        self.assertEqual(cm.exception.code,404)
    def test_config_and_dashboard(self):
        with self.request('/api/config') as r:self.assertEqual(json.load(r),default())
        with self.request('/') as r:self.assertIn(b'XLX Quick Connect',r.read())
    def test_cross_site_rejected(self):
        with self.assertRaises(urllib.error.HTTPError) as cm:self.request('/api/config',default(),'https://evil.example')
        self.assertEqual(cm.exception.code,403)
    def test_helper_failure_reported_and_fixed_command(self):
        host=self.url.split('//')[1]
        with patch.object(server.subprocess,'run',return_value=subprocess.CompletedProcess([],1,json.dumps({'ok':False,'error':'failed'}),'')) as mock:
            with self.assertRaises(urllib.error.HTTPError) as cm:self.request('/api/config',default(),'https://'+host)
            self.assertEqual(cm.exception.code,400)
            self.assertEqual(mock.call_args.args[0],['/usr/bin/sudo','-n','/usr/bin/python3','-I','/opt/hamspot/app/control-entry.py'])
    def test_hosts_no_path_input(self):
        with self.request('/api/hosts') as r:self.assertEqual(set(json.load(r)),{'dmr','dcs','xrf','ref'})

if __name__=='__main__':unittest.main()
