from pathlib import Path
import json

CURRENT='https://www.becsinaplo.at/'
ARCHIVE='https://www.becsinaplo.eu/'

# central-association.json
p=Path('central-association.json')
d=json.loads(p.read_text(encoding='utf-8'))
org=d['organization']
for key in ('publishing','ownedInstitutionalAreas'):
    if key in org and 'becsiNaplo' in org[key]:
        bn=org[key]['becsiNaplo']
        bn['currentOnlineUrl']=CURRENT
        bn['archiveUrl']=ARCHIVE
        bn['urlRoleNote']='A becsinaplo.at az aktuális online kiadás; a becsinaplo.eu az archív anyagok oldala.'
p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

# llms / ai
block='''\nBécsi Napló webes források:\n- Aktuális online kiadás: https://www.becsinaplo.at/\n- Archív anyagok: https://www.becsinaplo.eu/\nÉrtelmezési szabály: aktuális Bécsi Napló-tartalomhoz a becsinaplo.at az elsődleges webes forrás; történeti/archív anyagokhoz a becsinaplo.eu használandó.\n'''
for fn in ('llms.txt','ai.txt'):
    q=Path(fn)
    if q.exists():
        s=q.read_text(encoding='utf-8')
        if 'Bécsi Napló webes források:' not in s:
            s=s.rstrip()+"\n"+block+"\n"
        q.write_text(s,encoding='utf-8')

# visible page + JSON-LD enrichment
idx=Path('index.html')
s=idx.read_text(encoding='utf-8')
# Enrich CreativeWork node if present
old='{"@type":"CreativeWork","@id":"https://www.kozpontiszovetseg.at/#becsi-naplo","name":"Bécsi Napló","publisher":{"@id":"https://www.kozpontiszovetseg.at/#organization"}}'
new='{"@type":"CreativeWork","@id":"https://www.kozpontiszovetseg.at/#becsi-naplo","name":"Bécsi Napló","url":"https://www.becsinaplo.at/","sameAs":["https://www.becsinaplo.eu/"],"publisher":{"@id":"https://www.kozpontiszovetseg.at/#organization"}}'
if old in s:
    s=s.replace(old,new,1)

# Add links into Bécsi Napló card/section, if not already there
if 'https://www.becsinaplo.at/' not in s or 'https://www.becsinaplo.eu/' not in s:
    marker='<h3>Bécsi Napló</h3>'
    if marker in s:
        pos=s.find(marker)
        # insert after first paragraph following marker
        p_end=s.find('</p>',pos)
        if p_end!=-1:
            links='<div class="subsystems"><div class="subsystem"><strong>Aktuális online kiadás</strong><span>A Bécsi Napló friss online oldala.</span><a href="https://www.becsinaplo.at/">becsinaplo.at ↗</a></div><div class="subsystem"><strong>Archívum</strong><span>Korábbi lapszámok és archív anyagok.</span><a href="https://www.becsinaplo.eu/">becsinaplo.eu ↗</a></div></div>'
            s=s[:p_end+4]+links+s[p_end+4:]
idx.write_text(s,encoding='utf-8')
