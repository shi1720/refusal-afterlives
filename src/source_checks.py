#!/usr/bin/env python3
"""Source assertions supporting the exact claim, with no game redistribution."""
import argparse
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
ap=argparse.ArgumentParser(); ap.add_argument('--raw',type=Path,required=True); args=ap.parse_args()
manifest=json.loads((ROOT/'data/source_manifest.json').read_text())
for item in manifest:
    b=(args.raw/(item['scene']+'.txt')).read_bytes()
    assert hashlib.sha256(b).hexdigest()==item['sha256']
m=(args.raw/'Marriage.txt').read_text().splitlines()
def block(line):
    i=line-1
    indent=len(m[i])-len(m[i].lstrip())
    out=[]
    for s in m[i+1:]:
        if not s.strip(): continue
        if len(s)-len(s.lstrip())<=indent: break
        out.append(s.strip())
    return out
assert block(1359)==block(1366)
assert '*set RelKing %+20' in block(1366)
assert '*goto Jewels' in block(1366)
assert '*set accepted_something true' not in block(1366)
assert '*set accepted_something true' not in block(1322)
assert '*set accepted_something true' in block(1313)
assert '*set accepted_something true' in block(1334)
assert '*set accepted_something true' in block(1350)
assert '*if accepted_something' in block(1436)
assert '*goto Offer' in block(1436) and '*goto RD' in block(1436)
assert '*set RelKing %+30' in block(1429)
assert '*set RelKing %+70' in block(1474)
p=(args.raw/'Proposals.txt').read_text().splitlines()
assert p[280].strip()=='*set NoPartTwo true'
assert p[466].strip()=='*set NoPartTwo true'
result={'source_hash_checks':len(manifest),'poem_bodies_identical':True,
        'identity_scope':'response prose, commands, destination; not option labels',
        'game_bytes':sum(x['bytes'] for x in manifest),'game_lines':sum(x['lines'] for x in manifest)}
(ROOT/'results/source_checks.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
