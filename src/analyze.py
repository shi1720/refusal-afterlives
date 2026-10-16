#!/usr/bin/env python3
"""Verify the paired intervention and compare engine probes with a second model."""
import collections
import gzip
import hashlib
import itertools
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
R = ROOT / 'results'


def rows(mode):
    p = R / (mode + '.jsonl')
    if p.exists():
        with p.open() as f:
            yield from (json.loads(x) for x in f)
    else:
        with gzip.open(str(p) + '.gz', 'rt') as f:
            yield from (json.loads(x) for x in f)


def at(row, scene, menu):
    return next((i for i,e in enumerate(row['events']) if e['scene']==scene and e['menu']==menu), None)


def plus(x, p):
    # ChoiceScript's integer fairmath uses floor on positive changes.
    x=float(x)
    return min(99,math.floor(x + (100-x)*p/100))


def model(route, score, wealth, reputation):
    wealth, reputation = float(wealth), float(reputation)
    horse, poem, jewels, *rest = route
    accepted = horse != 1
    if horse == 0:
        score, reputation = plus(score,10), math.ceil(reputation*(1-.1))
    elif horse == 1:
        score = plus(score,20)
    else:
        reputation = math.ceil(reputation*(1-.15))
    if poem == 0:
        score, accepted = plus(score,10), True
    else:
        score = plus(score,20)
    if jewels == 1 and not accepted:
        assert not rest
        return 'RD', score, wealth, reputation, accepted
    if jewels == 0:
        wealth = plus(wealth,10)
        invite, *rest = rest
        if invite == 0:
            assert not rest
            return 'Mistress', score, wealth, math.ceil(reputation*.7), accepted
        score = plus(score,30)
    offer, = rest
    if offer == 0:
        return 'Mistress', score, wealth, math.ceil(reputation*.8), accepted
    return 'UncleAdvice', plus(score,70), wealth, reputation, accepted


def main():
    base = list(rows('baseline'))
    counters = collections.Counter(x['boundary'] for x in base)
    reached = [x for x in base if at(x,'Marriage',1348) is not None]
    pairs = mismatches = changed_choices = 0
    arrival_seeds = []
    for a,b in zip(rows('coy'),rows('stop')):
        assert a['seed']==b['seed']
        ia,ib=at(a,'Marriage',1348),at(b,'Marriage',1348)
        assert (ia is None)==(ib is None)
        if ia is None:
            assert a==b
            continue
        pairs+=1
        arrival_seeds.append(a['seed'])
        ea,eb=a['events'][ia],b['events'][ib]
        assert ea['selected']==1359 and eb['selected']==1366
        assert ea['state']==eb['state'] and ea['temps']==eb['temps']
        aftera=a['events'][ia+1:]; afterb=b['events'][ib+1:]
        if (aftera,a['boundary'],a['final']) != (afterb,b['boundary'],b['final']):
            mismatches+=1
        changed_choices += len(aftera)
    assert pairs==len(reached) and mismatches==0
    local=json.loads((R/'local.json').read_text())
    witness=reached[0]
    estate=witness['events'][at(witness,'Marriage',1348)]['state']
    errors=[]
    for x in local:
        want=model(x['route'],x['score'],x['initial_wealth'],x['initial_reputation'])
        got=(x['endpoint'],float(x['relking']),float(x['wealth']),float(x['reputation']),x['accepted'])
        if want!=got: errors.append((x,want))
    assert not errors, errors[:2]
    assert len(local)==43*101*4
    groups=collections.Counter(x['endpoint'] for x in local if x['score']==50 and x['sex']=='female' and x['pref']=='he')
    summaries = {
        'baseline_runs':len(base),'seed_start':base[0]['seed'],'seed_end':base[-1]['seed'],
        'baseline_boundaries':dict(counters),'poem_arrivals':len(reached),
        'paired_runs':pairs,'paired_mismatches':mismatches,
        'downstream_choice_comparisons':changed_choices,
        'paired_total_full_plays':20000,'local_executions':len(local),
        'local_choice_sequences':43,'local_grid_cases':404,
        'local_model_disagreements':len(errors),'local_endpoints_per_case':dict(groups),
        'baseline_poem_choices':dict(collections.Counter(x['events'][at(x,'Marriage',1348)]['selected'] for x in reached)),
        'witness_seed':witness['seed'],
        'witness_pre_poem_state':{k:estate[k] for k in ['sex','he_pref','relking','wealth','reputation']},
        'baseline_terminal_categories':dict(collections.Counter(
            'Torres closure' if x['boundary']=='WrapUp' and x['final']['marriedtorres'] else
            'Mendosa closure' if x['boundary']=='WrapUp' and x['final']['marriedmendosa'] else
            'death closure' if not x['final']['alive'] else
            'other closure' if x['boundary']=='WrapUp' else 'serial boundary' for x in base))
    }
    (R/'summary.json').write_text(json.dumps(summaries,indent=2)+'\n')
    (ROOT/'data/paired_arrival_seeds.json').write_text(json.dumps(arrival_seeds)+'\n')
    # A small complete play witness: menu source locations and scalar states only.
    (ROOT/'data/witness.json').write_text(json.dumps(witness,indent=2)+'\n')
    print(json.dumps(summaries,indent=2))


if __name__=='__main__':
    main()
