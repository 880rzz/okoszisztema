from pathlib import Path
import json

members_path = Path('member-organizations.json')
press_path = Path('member-press-evidence.json')

members_doc = json.loads(members_path.read_text(encoding='utf-8'))
press_doc = json.loads(press_path.read_text(encoding='utf-8'))
press_by_id = {entry['memberId']: entry for entry in press_doc['entries']}

for member in members_doc['members']:
    evidence = press_by_id.get(member['id'])
    if not evidence:
        member.pop('pressSummary', None)
        member.pop('pressEvidence', None)
        continue
    member['pressSummary'] = evidence['verifiedSummary']
    member['pressEvidence'] = evidence['evidence']

members_doc['pressResearch'] = {
    'lastResearched': press_doc['lastResearched'],
    'sourcePriority': press_doc['sourcePriority'],
    'evidenceFile': 'https://okoszisztema.kozpontiszovetseg.at/member-press-evidence.json',
    'rule': 'Press evidence supplements the official member directory. It may enrich activity/history descriptions but must not override official legal identity, ZVR or membership status without an authoritative organization source.'
}

members_path.write_text(json.dumps(members_doc, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

# Validation
out = json.loads(members_path.read_text(encoding='utf-8'))
assert len(out['members']) == 28
assert sum(out['regions'].values()) == 28
covered = [m for m in out['members'] if m.get('pressEvidence')]
assert len(covered) == len(press_doc['entries'])
for member in covered:
    assert member['pressSummary']
    assert all(x.get('publisher') in {'ORF Magyarok', 'Rólunk.at'} for x in member['pressEvidence'])

print(f"OK: merged press evidence into {len(covered)} of 28 member entries")
