"""Named host-file editing; never accept a client supplied filesystem path."""
import re
HOST_FILES={'dmr':'XLXHosts.txt','dcs':'DCS_Hosts.txt','xrf':'DExtra_Hosts.txt','ref':'DPlus_Hosts.txt'}

def validate_hosts(kind,text):
    if kind not in HOST_FILES: raise ValueError('Unknown host file')
    if not isinstance(text,str) or len(text.encode())>60000: raise ValueError('Host file must be under 60 KB')
    if any(ord(c)<32 and c not in '\n\r\t' for c in text): raise ValueError('Invalid control character')
    seen=set()
    for number,line in enumerate(text.splitlines(),1):
        line=line.strip()
        if not line or line.startswith('#'): continue
        parts=line.split(';') if kind=='dmr' else line.split()
        if kind=='dmr':
            valid=len(parts)==3 and re.fullmatch('[A-Z0-9]{3}',parts[0]) and parts[2].isdigit() and 4001<=int(parts[2])<=4026
        else:
            prefix={'dcs':'DCS','xrf':'XRF','ref':'REF'}[kind]
            valid=2<=len(parts)<=3 and re.fullmatch(prefix+r'[0-9]{3}',parts[0])
            if len(parts)==3: valid=valid and parts[2] in ('0','1')
        if not valid or not re.fullmatch(r'[a-zA-Z0-9][a-zA-Z0-9.-]{0,79}',parts[1]):
            raise ValueError(f'Invalid host entry on line {number}')
        if parts[0] in seen: raise ValueError(f'Duplicate host on line {number}')
        seen.add(parts[0])
    return text.replace('\r\n','\n').rstrip()+'\n'

def import_dmr(c,text):
    """Import XLX addresses, retaining private ports/passwords set in reflector menu."""
    import copy
    c=copy.deepcopy(c);text=validate_hosts('dmr',text)
    existing={r['id']:r for r in c['reflectors']};entries=[]
    for line in text.splitlines():
        if not line.strip() or line.lstrip().startswith('#'): continue
        ident,host,module=line.strip().split(';')
        r=existing.get(ident,{'id':ident,'label':'XLX'+ident,'port':62030,'password':'passw0rd'})
        r['host']=host;entries.append(r)
        if ident==c['selected_reflector']: c['module']=chr(int(module)-4000+64)
    c['reflectors']=entries
    if c['selected_reflector'] not in {r['id'] for r in entries}:
        c['selected_reflector']='';c['network_enabled']=False
    return c
