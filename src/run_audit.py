#!/usr/bin/env python3
"""Acquire the public episode; instrument the pinned upstream engine; replay it.

No purchased scene is acquired. Original game files remain in the local cache.
The only scene substitution is Episode2: a terminal boundary, not a continuation.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
PIN = '60a6c3ee7393c9ee7e42650b8e1642ae38e3cb6a'
SCENES = ['startup', 'OpeningScene', 'ComingOfAgeParty', 'Masque', 'Tokens',
          'Politics', 'GrandBall', 'Proposals', 'Marriage', 'WrapUp', 'PrepScene', 'Episode2']


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--cache', type=Path, required=True)
    ap.add_argument('--runs', type=int, default=10000)
    ap.add_argument('--seed', type=int, default=0)
    ap.add_argument('--mode', choices=['baseline', 'coy', 'stop'], default='baseline')
    args = ap.parse_args()
    cache = args.cache.resolve()
    cache.mkdir(parents=True, exist_ok=True)
    raw, engine = cache / 'raw', cache / 'engine'
    raw.mkdir(exist_ok=True)
    if not engine.exists():
        subprocess.run(['git', 'clone', '-q', 'https://github.com/dfabulich/choicescript.git', str(engine)], check=True)
    subprocess.run(['git', '-C', str(engine), 'checkout', '-q', PIN], check=True)
    manifest = []
    for name in SCENES:
        p = raw / (name + '.txt')
        url = 'https://www.choiceofgames.com/romance/scenes/' + name + '.txt'
        if not p.exists():
            subprocess.run(['curl', '-fLsS', url, '-o', str(p)], check=True)
        b = p.read_bytes()
        manifest.append(dict(scene=name, url=url, bytes=len(b), sha256=hashlib.sha256(b).hexdigest(),
                             lines=len(b.decode('utf-8-sig').splitlines())))
    mp = ROOT / 'data/source_manifest.json'
    if mp.exists() and json.loads(mp.read_text()) != manifest:
        raise ValueError('Source bytes differ from the frozen research manifest; do not overwrite it.')
    mp.write_text(json.dumps(manifest, indent=2) + '\n')
    game = engine / 'web/auditromance/scenes'
    game.mkdir(parents=True, exist_ok=True)
    for name in SCENES:
        shutil.copy2(raw / (name + '.txt'), game / (name + '.txt'))
    # Do not execute the purchase flow or obtain any paid scene.
    (game / 'Episode2.txt').write_text('*ending\n')
    source = (engine / 'randomtest.js').read_text()
    # All changes are hooks around upstream semantics, except this terminal boundary.
    source = source.replace('var slurps = {}', '''var slurps = {};
var auditEvents = [], auditBoundary = null;
function auditState(s) {
  var out = {};
  Object.keys(s).sort().forEach(function(k) {
    if (s[k] === null || ['string','number','boolean'].indexOf(typeof s[k]) >= 0) out[k] = s[k];
  });
  return out;
}
var auditFd;
''', 1)
    source = source.replace('var item = flattenedOptions[index];', '''
    if (this.name === 'Marriage' && choiceLine + 1 === 1348 && process.env.AUDIT_MODE !== 'baseline') {
      index = process.env.AUDIT_MODE === 'coy' ? 1 : 2;
    }
    var item = flattenedOptions[index];
    auditEvents.push({scene:this.name, menu:choiceLine+1, selected:item.ultimateOption.line,
      options:flattenedOptions.map(function(x){return x.ultimateOption.line;}),
      state: (this.name === 'Marriage' && [1311,1348,1404,1417,1459].indexOf(choiceLine+1)>=0) ? auditState(this.stats) : undefined,
      temps: (this.name === 'Marriage' && [1311,1348,1404,1417,1459].indexOf(choiceLine+1)>=0) ? auditState(this.temps) : undefined});
''', 1)
    source = source.replace("var file = slurpFileCached('web/'+gameName+'/scenes/'+this.name+'.txt');", """
    if (this.name === 'Episode2') auditBoundary = 'Episode2';
    var file = slurpFileCached('web/'+gameName+'/scenes/'+this.name+'.txt');
""", 1)
    source = source.replace('function randomtest() {\n', '''function randomtest() {
  auditFd = fs.openSync(process.env.AUDIT_OUTPUT, 'w');
''', 1)
    source = source.replace('for (var i = 0; i < iterations; i++) {\n    console.log', '''for (var i = 0; i < iterations; i++) {
    auditEvents = []; auditBoundary = null;
    console.log''', 1)
    source = source.replace('if (!stats.choice_feedback_requested) missingFeedback++;', '''
      fs.writeSync(auditFd, JSON.stringify({seed:i+randomSeed, events:auditEvents,
        boundary:auditBoundary || 'WrapUp', final:auditState(stats)})+'\\n');
      if (!stats.choice_feedback_requested) missingFeedback++;''', 1)
    patched = engine / 'audit-randomtest.js'
    patched.write_text(source)
    env = dict(os.environ, AUDIT_MODE=args.mode,
               AUDIT_OUTPUT=str(ROOT / 'results' / (args.mode + '.jsonl')))
    log = ROOT / 'results' / (args.mode + '.log')
    with log.open('w') as f:
        subprocess.run(['node', str(patched), 'num='+str(args.runs), 'seed='+str(args.seed),
                        'game=auditromance', 'showChoices=false', 'showCoverage=false',
                        'avoidUsedOptions=false', 'trial=true'], cwd=engine, env=env,
                       stdout=f, stderr=subprocess.STDOUT, check=True)
    print(log.read_text()[-300:])


if __name__ == '__main__':
    main()
