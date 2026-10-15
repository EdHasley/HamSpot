"""Validated HamSpot DMR configuration and upstream INI rendering."""
import configparser
import io
import json
import re
from pathlib import Path

TEMPLATES = Path(__file__).resolve().parents[1] / 'radio'

def validate(value):
    defaults = json.loads((TEMPLATES / 'defaults.json').read_text())
    if not isinstance(value, dict) or set(value) != set(defaults):
        raise ValueError('Configuration must contain exactly the documented fields')
    c = dict(value)
    def integer(name, low, high):
        if type(c[name]) is not int or not low <= c[name] <= high:
            raise ValueError(f'{name} must be an integer from {low} to {high}')
    if not isinstance(c['callsign'], str) or not re.fullmatch(r'[A-Z0-9/]{3,12}', c['callsign']):
        raise ValueError('Callsign must use 3–12 uppercase letters, numbers or slash')
    if c['uart'] not in ('/dev/ttyAMA0', '/dev/ttyAMA10', '/dev/serial0', '/dev/ttyACM0', '/dev/ttyUSB0'):
        raise ValueError('Select a supported serial device')
    for name in ('duplex', 'radio_enabled', 'network_enabled'):
        if type(c[name]) is not bool: raise ValueError(f'{name} must be true or false')
    for name, low, high in [('dmr_id',0,999999999),('baud',9600,460800),('color_code',0,15),('slot',1,2),('talkgroup',1,16777215),('rx_offset',-100000,100000),('tx_offset',-100000,100000),('rx_level',0,100),('tx_level',0,100),('rf_level',0,100)]:
        integer(name, low, high)
    for name in ('rx_frequency','tx_frequency'):
        integer(name,0,1000000000)
        if c[name] and not (100000000 <= c[name] <= 1000000000):
            raise ValueError(f'{name} must be in Hz, from 100 MHz to 1 GHz')
    if c['radio_enabled'] and (not c['dmr_id'] or c['callsign'] == 'N0CALL' or not c['rx_frequency'] or not c['tx_frequency']):
        raise ValueError('Set your callsign, DMR ID and both frequencies before enabling the radio')
    if not isinstance(c['module'], str) or not re.fullmatch('[A-Z]',c['module']):
        raise ValueError('Module must be A–Z')
    if not isinstance(c['reflectors'], list) or len(c['reflectors']) > 100:
        raise ValueError('At most 100 saved reflectors are supported')
    ids = set()
    for r in c['reflectors']:
        if not isinstance(r,dict) or set(r) != {'id','label','host','port','password'}:
            raise ValueError('Each reflector needs id, label, host, port and password')
        if not isinstance(r['id'],str) or not re.fullmatch('[A-Z0-9]{3}',r['id']) or r['id'] in ids:
            raise ValueError('Reflector IDs must be unique three-character uppercase IDs')
        ids.add(r['id'])
        if not isinstance(r['label'],str) or not 1 <= len(r['label']) <= 60 or any(ord(x)<32 for x in r['label']):
            raise ValueError('Reflector label must be 1–60 printable characters')
        if not isinstance(r['host'],str) or not re.fullmatch(r'[a-zA-Z0-9][a-zA-Z0-9.-]{0,79}',r['host']):
            raise ValueError('Reflector host must be a hostname or IPv4 address')
        if type(r['port']) is not int or not 1 <= r['port'] <= 65535 or r['port'] in (62031,62032) and r['host'] in ('127.0.0.1','localhost'):
            raise ValueError('Invalid or conflicting reflector port')
        if not isinstance(r['password'],str) or not re.fullmatch(r'[\x21-\x7e]{1,64}',r['password']) or any(x in r['password'] for x in '#;'):
            raise ValueError('Password must contain 1–64 printable non-space characters, excluding # and ;')
    if not isinstance(c['selected_reflector'],str) or c['selected_reflector'] and c['selected_reflector'] not in ids:
        raise ValueError('Select one of the saved reflectors')
    if c['network_enabled'] and (not c['radio_enabled'] or not c['selected_reflector']):
        raise ValueError('Enable the configured radio and select a reflector before enabling networking')
    return c

def render(c, directory='/etc/hamspot'):
    c = validate(c)
    def load(name):
        p = configparser.ConfigParser(interpolation=None, strict=False)
        p.optionxform = str
        p.read(TEMPLATES / name)
        return p
    def put(p, section, **values):
        if not p.has_section(section): p.add_section(section)
        for k,v in values.items(): p.set(section,k,str(int(v) if type(v) is bool else v))
    host = load('MMDVM-Host.ini')
    # Explicitly disable every sample mode and network before enabling DMR.
    for s in ('D-Star','System Fusion','P25','NXDN','POCSAG','FM','DMR Trunking','Transparent Data','CW Id','Remote Control'):
        put(host,s,Enable=0)
    for s in host.sections():
        if s.endswith(' Network'): put(host,s,Enable=0)
    put(host,'General',Callsign=c['callsign'],Id=c['dmr_id'],Duplex=c['duplex'],Daemon=0)
    put(host,'Modem',Protocol='uart',UARTPort=c['uart'],UARTSpeed=c['baud'],RXFrequency=c['rx_frequency'],TXFrequency=c['tx_frequency'],RXOffset=c['rx_offset'],TXOffset=c['tx_offset'],RXLevel=c['rx_level'],TXLevel=c['tx_level'],RFLevel=c['rf_level'])
    put(host,'DMR',Enable=1,ColorCode=c['color_code'])
    put(host,'DMR Network',Enable=c['network_enabled'],LocalAddress='127.0.0.1',LocalPort=62032,GatewayAddress='127.0.0.1',GatewayPort=62031)
    put(host,'DMR Id Lookup',File='/usr/share/hamspot/DMRIds.dat')
    put(host,'NXDN Id Lookup',File='/usr/share/hamspot/NXDN.csv')
    gateway = load('DMRGateway.ini')
    put(gateway,'General',Id=c['dmr_id'],RptAddress='127.0.0.1',RptPort=62032,LocalAddress='127.0.0.1',LocalPort=62031,Daemon=0)
    for s in gateway.sections():
        if s.startswith('DMR Network '): put(gateway,s,Enabled=0)
    put(gateway,'Voice',Enabled=0)
    put(gateway,'Dynamic TG Control',Enable=0)
    put(gateway,'Remote Commands',Enable=0)
    put(gateway,'Info',Callsign=c['callsign'],RXFrequency=c['rx_frequency'],TXFrequency=c['tx_frequency'],ColorCode=c['color_code'],Duplex=c['duplex'],Location='HamSpot',Description='HamSpot DMR hotspot',URL='')
    selected = next((r for r in c['reflectors'] if r['id']==c['selected_reflector']),None)
    put(gateway,'XLX Network',Enabled=c['network_enabled'],File=f'{directory}/XLXHosts.txt',Port=selected['port'] if selected else 62030,Password=selected['password'] if selected else 'passw0rd',Startup=c['selected_reflector'] if selected else '4000',Module=c['module'],Slot=c['slot'],TG=c['talkgroup'],Relink=0,UserControl=0)
    out = {}
    for name,p in [('MMDVM-Host.ini',host),('DMRGateway.ini',gateway)]:
        buf=io.StringIO();p.write(buf,space_around_delimiters=False);out[name]=buf.getvalue()
    out['XLXHosts.txt']=''.join(f"{r['id']};{r['host']};{4000+ord(c['module'])-64}\n" for r in c['reflectors'])
    return out
