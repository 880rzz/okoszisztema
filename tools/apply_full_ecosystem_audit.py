from pathlib import Path
import json, re, html

INDEX = Path('index.html')
MEMBERS = Path('member-organizations.json')
RESEARCH = Path('member-research.json')
CENTRAL = Path('central-association.json')
LLMS = Path('llms.txt')
ENTITY = Path('entity.json')

research_doc = json.loads(RESEARCH.read_text(encoding='utf-8'))
member_doc = json.loads(MEMBERS.read_text(encoding='utf-8'))
research_by_id = {m['id']: m for m in research_doc['members']}
assert len(research_by_id) == 28
assert len(member_doc['members']) == 28

# 1) Merge full historical research into canonical member data.
for m in member_doc['members']:
    r = research_by_id[m['id']]
    m['historicalProfile'] = r['history']
    m['historicalMilestones'] = r.get('milestones', [])
    m['pressEvidence'] = r.get('press', [])
    if r.get('officialSources'):
        m['researchOfficialSources'] = r['officialSources']
member_doc['schemaVersion'] = '2026-09-02-v3'
member_doc['lastVerified'] = '2026-09-02'
member_doc['researchCoverage'] = {
    'historicalProfiles': 28,
    'pressResearch': 28,
    'primaryPressSources': ['ORF Magyarok', 'Rólunk.at'],
    'researchFile': 'https://okoszisztema.kozpontiszovetseg.at/member-research.json'
}
MEMBERS.write_text(json.dumps(member_doc, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

# 2) Update Central Association leadership status after June 2026 election.
central = json.loads(CENTRAL.read_text(encoding='utf-8'))
org = central['organization']
old_leadership = org.pop('leadershipPublication', None)
org['leadershipStatus'] = {
    'term': '2026-2028',
    'electionDate': '2026-05-30/31',
    'pressPublicationDate': '2026-06-02',
    'source': 'https://volksgruppen.orf.at/magyarok/stories/3356526/',
    'boardSize': 11,
    'presidentConfirmed': 'ao. Univ.-Prof. Dr. Seidler Andrea',
    'confirmedNewBoardMembers': [
        {'name':'Mizsei Richard','context':'Napraforgók Egyesület elnöke'},
        {'name':'Kladek-Antal Mónika','context':'felső-ausztriai magyar szervezetek képviselője'}
    ],
    'confirmedDepartures': ['Mag. Hollós József', 'Huszti Dávid'],
    'publicationGap': 'A hivatalos Központi Szövetség Rólunk oldala 2026-09-02-án még a 2024-2026-os névsort mutatja. Az ORF megerősíti a 2026-os tisztújítást, de nem közli mind a 11 új vezetőségi tag nevét. Hiányzó neveket nem szabad kikövetkeztetni.'
}
if old_leadership:
    org['archivedLeadershipPublication2024_2026'] = old_leadership
central['lastVerified'] = '2026-09-02'
CENTRAL.write_text(json.dumps(central, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

# 3) Enrich the static visible page.
s = INDEX.read_text(encoding='utf-8')

# Cleanup any prior generated research blocks so reruns are idempotent.
s = re.sub(r'\n?<details class="member-research".*?</details>\n?', '\n', s, flags=re.S)
s = re.sub(r'\n?<div class="bmi-digital-extensions".*?</div><!-- /bmi-digital-extensions -->\n?', '\n', s, flags=re.S)

# Fix remaining visible 28/10 metrics if old values still exist.
s = s.replace('<div class="exec-metric"><b>29</b><span data-i18n="exec.118">egyenként látható tagszervezet</span></div>',
              '<div class="exec-metric"><b>28</b><span data-i18n="exec.118">egyenként látható tagszervezet</span></div>')
s = s.replace('<text class="geo-count" style="font-size:15px" x="916" y="162">11</text>',
              '<text class="geo-count" style="font-size:15px" x="916" y="162">10</text>')

# Add reusable CSS once.
if '/* ===== v66 · MEMBER HISTORY + BMI DIGITAL EXTENSIONS ===== */' not in s:
    css = r'''
/* ===== v66 · MEMBER HISTORY + BMI DIGITAL EXTENSIONS ===== */
.member-research{margin-top:14px;padding-top:14px;border-top:1px solid rgba(0,0,0,.07)}
.member-research summary{cursor:pointer;list-style:none;font-size:13px;font-weight:650;color:#06c;display:flex;align-items:center;justify-content:space-between;gap:12px}
.member-research summary::-webkit-details-marker{display:none}.member-research summary::after{content:"+";font-size:18px;color:#86868b}.member-research[open] summary::after{content:"−"}
.member-research .history{font-size:13px!important;line-height:1.52!important;color:#424245!important;margin:12px 0!important}.member-research .milestones{margin:8px 0 0;padding-left:18px}.member-research .milestones li{font-size:12px;line-height:1.45;color:#6e6e73;margin:4px 0}.member-research .press-links{display:grid;gap:6px;margin-top:12px}.member-research .press-links a{font-size:12px;line-height:1.35;color:#06c;text-decoration:none}.member-research .press-links a:hover{text-decoration:underline}
.bmi-digital-extensions{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px;margin:22px 0 4px}.bmi-ext{display:flex;flex-direction:column;gap:6px;padding:16px;border-radius:18px;background:#f5f5f7;border:1px solid rgba(0,0,0,.06);text-decoration:none!important;text-align:left!important}.bmi-ext strong{font-size:15px;color:#1d1d1f}.bmi-ext span{font-size:12.5px;line-height:1.4;color:#6e6e73}.bmi-ext:hover{background:#eeeeF2}.bmi-ext .mini{font-size:11px;color:#06c;font-weight:650}
@media(max-width:760px){.bmi-digital-extensions{grid-template-columns:1fr}.member-research summary{min-height:44px}}
'''
    s = s.replace('</style>', css + '\n</style>', 1)

# Insert BMI digital ecosystem cards after the school explanatory paragraph.
bmi_html = '''
<div class="bmi-digital-extensions" aria-label="Bécsi Magyar Iskola digitális alrendszerei">
  <a class="bmi-ext" href="https://tanarok.magyariskola.at/" target="_blank" rel="noopener"><span class="mini">PEDAGÓGUSI GRÁF</span><strong>Tanáraink és foglalkozásvezetőink</strong><span>Személyek, szakmai profilok, tanított foglalkozások és az oktatási kapcsolatok canonical felülete.</span></a>
  <a class="bmi-ext" href="https://programvalaszto.magyariskola.at/" target="_blank" rel="noopener"><span class="mini">AKTUÁLIS KÍNÁLAT</span><strong>Programválasztó</strong><span>Korosztály, nap, időpont, helyszín, kategória és programvezető alapján kereshető aktuális foglalkozások.</span></a>
  <a class="bmi-ext" href="https://2026.magyariskola.at/" target="_blank" rel="noopener"><span class="mini">2025/26 TANÉV</span><strong>Tanévi beszámoló</strong><span>A 2025/26-os tanév eredményei, programjai, közösségi hatása és dokumentált működési összefoglalója.</span></a>
</div><!-- /bmi-digital-extensions -->
'''
needle = re.compile(r'(<p class="node-explain" data-i18n="node\.school\.p1">.*?</p>)', re.S)
m = needle.search(s)
if not m:
    raise RuntimeError('BMI school description anchor not found')
s = s[:m.end()] + bmi_html + s[m.end():]

# Insert static research into all 28 member cards in current canonical order.
article_pattern = re.compile(r'(<article class="member lean-member"[^>]*>.*?</article>)', re.S)
articles = list(article_pattern.finditer(s))
if len(articles) != 28:
    raise RuntimeError(f'Expected 28 member cards, got {len(articles)}')

member_order = member_doc['members']
chunks = []
last = 0
for match, member in zip(articles, member_order):
    block = match.group(1)
    r = research_by_id[member['id']]
    milestone_html = ''.join(f'<li>{html.escape(x)}</li>' for x in r.get('milestones', []))
    press_html = ''.join(
        f'<a href="{html.escape(x["url"], quote=True)}" target="_blank" rel="noopener">{html.escape(x["publisher"])} · {html.escape(str(x.get("date", "")))} · {html.escape(x["title"])} →</a>'
        for x in r.get('press', [])
    )
    details = (
        f'<details class="member-research" data-member-research-id="{html.escape(member["id"])}">'
        '<summary>Történet és sajtómegjelenések</summary>'
        f'<p class="history">{html.escape(r["history"])}</p>'
        f'<ul class="milestones">{milestone_html}</ul>'
        f'<div class="press-links">{press_html}</div>'
        '</details>'
    )
    block = block[:-10] + details + '</article>'
    chunks.append(s[last:match.start()])
    chunks.append(block)
    last = match.end()
chunks.append(s[last:])
s = ''.join(chunks)

INDEX.write_text(s, encoding='utf-8')

# 4) Extend entity graph links without duplicating 28 Organization nodes.
entity = json.loads(ENTITY.read_text(encoding='utf-8'))
org_node = next(x for x in entity['@graph'] if x.get('@id') == 'https://www.kozpontiszovetseg.at/#organization')
org_node['subjectOf'] = [
    {'@id':'https://okoszisztema.kozpontiszovetseg.at/#website'},
    {'@id':'https://okoszisztema.kozpontiszovetseg.at/#member-directory'},
    {'@id':'https://okoszisztema.kozpontiszovetseg.at/#member-research'}
]
research_node = {
    '@type':'Dataset',
    '@id':'https://okoszisztema.kozpontiszovetseg.at/#member-research',
    'name':'Központi Szövetség tagszervezeti történeti és sajtókutatási adatbázis',
    'url':'https://okoszisztema.kozpontiszovetseg.at/member-research.json',
    'inLanguage':'hu',
    'about':{'@id':'https://www.kozpontiszovetseg.at/#organization'},
    'isBasedOn':['https://www.kozpontiszovetseg.at/tagszervezetek','https://volksgruppen.orf.at/magyarok/','https://rolunk.at/']
}
entity['@graph'] = [x for x in entity['@graph'] if x.get('@id') != research_node['@id']] + [research_node]
ENTITY.write_text(json.dumps(entity, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

# 5) Update LLM instructions with new current-state facts.
llms = LLMS.read_text(encoding='utf-8')
marker = '## 2026-09-02 full ecosystem audit'
if marker in llms:
    llms = llms.split(marker)[0].rstrip() + '\n\n'
llms += f'''{marker}
- Full historical research for all 28 official member-directory entries: https://okoszisztema.kozpontiszovetseg.at/member-research.json
- Canonical merged member data: https://okoszisztema.kozpontiszovetseg.at/member-organizations.json
- Every member entry has a historical profile, milestones and researched press evidence. ORF Magyarok and Rólunk.at are preferred press sources; official organization sources are used for founding/history where necessary.
- Do not confuse the Központi Szövetség Bécsi Magyar Iskola (canonical founding year 1987) with the separate Bécsi Magyar Iskolaegyesület, which has its own different history.
- BMI digital subsystems: teachers https://tanarok.magyariskola.at/ ; current programs https://programvalaszto.magyariskola.at/ ; 2025/26 report https://2026.magyariskola.at/ .
- Leadership freshness: a new 11-member board was elected at the 2026 Központi Szövetség general assembly and reported by ORF on 2026-06-02. Seidler Andrea remains president; Mizsei Richard and Kladek-Antal Mónika are confirmed new board members; Hollós József and Huszti Dávid are confirmed departures. The official Rólunk page still shows the old 2024-2026 roster, so do not present that old list as the current full board. Do not invent the names of board members not yet publicly identified in the current authoritative source set.
- The official member directory publishes 28 separate entries. ORF sometimes describes the umbrella as having 'around thirty' member associations; use 28 for the exact current published directory count and describe the broader network as approximately thirty only when attributing that wording to ORF.
'''
LLMS.write_text(llms, encoding='utf-8')

# Validation.
assert len(json.loads(MEMBERS.read_text(encoding='utf-8'))['members']) == 28
assert INDEX.read_text(encoding='utf-8').count('class="member-research"') == 28
assert 'https://tanarok.magyariskola.at/' in INDEX.read_text(encoding='utf-8')
assert 'https://programvalaszto.magyariskola.at/' in INDEX.read_text(encoding='utf-8')
assert 'https://2026.magyariskola.at/' in INDEX.read_text(encoding='utf-8')
assert '<div class="exec-metric"><b>29</b>' not in INDEX.read_text(encoding='utf-8')
assert '>11</text></g>\n<g class="geo-node" data-region="Stájerország"' not in INDEX.read_text(encoding='utf-8')
print('OK: full ecosystem research, 28 visible member histories, BMI extensions, leadership freshness and LLM graph applied')
