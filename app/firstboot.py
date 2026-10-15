#!/usr/bin/python3
"""Generate unique credentials/certificate per card on first boot."""
import grp
import hashlib
import json
import os
import secrets
import subprocess
from pathlib import Path
STATE=Path('/etc/hamspot')
STATE.mkdir(exist_ok=True)
gid=grp.getgrnam('hamspot').gr_gid
if not (STATE/'auth.json').exists():
    password=secrets.token_urlsafe(18);salt=secrets.token_hex(16)
    auth={'salt':salt,'hash':hashlib.pbkdf2_hmac('sha256',password.encode(),bytes.fromhex(salt),200000).hex()}
    (STATE/'auth.json').write_text(json.dumps(auth))
    login=f'HamSpot\nOpen https://hamspot.local:8443 or https://<Pi-IP>:8443\nUsername: admin\nPassword: {password}\nThe certificate is generated on this Pi; a browser certificate warning is expected.\nKeep this login private.\n'
    for target in [Path('/boot/firmware/HAMSPOT-LOGIN.txt'),STATE/'login.txt']:
        target.write_text(login)
    print(login)
if not (STATE/'tls.key').exists():
    subprocess.run(['openssl','req','-x509','-newkey','rsa:3072','-nodes','-keyout',str(STATE/'tls.key'),'-out',str(STATE/'tls.crt'),'-days','3650','-subj','/CN=hamspot.local','-addext','subjectAltName=DNS:hamspot.local,DNS:hamspot'],check=True)
for p in STATE.iterdir():
    if p.is_file():
        os.chmod(p,0o640);os.chown(p,0,gid)
