#!/usr/bin/python3
"""Fixed-operation privileged helper. No paths, commands or shell text from clients."""
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from radio import validate, render
from auth import matches, password_record
from hosts import HOST_FILES, validate_hosts, import_dmr

STATE = Path('/etc/hamspot')
UNITS = ('hamspot-gateway.service','hamspot-radio.service')

def run(*args, check=True):
    return subprocess.run(['/usr/bin/systemctl',*args],check=check,capture_output=True,text=True,timeout=30)

def atomic(path, data):
    fd,name=tempfile.mkstemp(dir=path.parent)
    try:
        with os.fdopen(fd,'w') as f: f.write(data); f.flush(); os.fsync(f.fileno())
        os.chmod(name,0o640)
        import grp
        os.chown(name,0,grp.getgrnam('hamspot').gr_gid)
        os.replace(name,path)
    finally:
        if os.path.exists(name): os.unlink(name)

def apply(c):
    c=validate(c)
    paths={name:STATE/name for name in ['config.json','MMDVM-Host.ini','DMRGateway.ini','XLXHosts.txt']}
    previous={name:p.read_text() if p.exists() else None for name,p in paths.items()}
    active=[u for u in UNITS if run('is-active',u,check=False).returncode==0]
    run('stop',*UNITS)
    try:
        for name,data in dict(render(c),**{'config.json':json.dumps(c,indent=2)+'\n'}).items(): atomic(paths[name],data)
        if c['radio_enabled']:
            if c['network_enabled']: run('start',UNITS[0])
            run('start',UNITS[1])
    except Exception:
        run('stop',*UNITS,check=False)
        for name,data in previous.items():
            if data is not None: atomic(paths[name],data)
            else: paths[name].unlink(missing_ok=True)
        if active: run('start',*active,check=False)
        raise

def change_password(current, new):
    auth = json.loads((STATE/'auth.json').read_text())
    if not isinstance(current, str) or not matches(current, auth):
        raise ValueError('Current password is incorrect')
    record = password_record(new)
    atomic(STATE/'auth.json', json.dumps(record)+'\n')


if __name__=='__main__':
    import fcntl
    STATE.mkdir(exist_ok=True)
    with open('/run/lock/hamspot-control.lock','w') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX)
        try:
            raw=sys.stdin.buffer.read(65537)
            if len(raw)>65536: raise ValueError('Request too large')
            request=json.loads(raw)
            if request['action']=='apply': apply(request['config'])
            elif request['action']=='hosts':
                kind=request['kind'];text=validate_hosts(kind,request['text'])
                if kind=='dmr': apply(import_dmr(json.loads((STATE/'config.json').read_text()),text))
                else:
                    directory=STATE/'hosts';directory.mkdir(exist_ok=True)
                    atomic(directory/HOST_FILES[kind],text)
            elif request['action']=='password': change_password(request['current_password'], request['new_password'])
            elif request['action']=='stop': run('stop',*UNITS)
            elif request['action']=='start': apply(json.loads((STATE/'config.json').read_text()))
            else: raise ValueError('Unknown action')
            print(json.dumps({'ok':True}))
        except Exception as e:
            print(json.dumps({'ok':False,'error':str(e)}));sys.exit(1)
