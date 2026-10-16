// Execute the unmodified courtship passage in the pinned upstream engine.
// Usage (from engine directory): node /absolute/path/probe_local.js RAW CACHE_RESULT
const fs = require('fs'), vm = require('vm'), path = require('path');
global.fs = fs; global.path = path;
for (const file of ['web/scene.js','web/navigator.js','web/util.js','headless.js']) {
  vm.runInThisContext(fs.readFileSync(file, 'utf8'), {filename:file});
}
const raw = process.argv[2], target = process.argv[3];
const root = path.resolve(__dirname, '..');
const templates={};
const bp=path.join(root,'results/baseline.jsonl');
const baselineText=fs.existsSync(bp) ? fs.readFileSync(bp,'utf8') : require('zlib').gunzipSync(fs.readFileSync(bp+'.gz')).toString('utf8');
const baseline = baselineText.trim().split('\n');
for (const line of baseline) {
  const row = JSON.parse(line);
  const e = row.events.find(x=>x.scene==='Marriage' && x.menu===1311);
  if (e) {
    const key=e.state.sex+'/'+e.state.he_pref;
    if (!templates[key]) templates[key]={...e,seed:row.seed};
  }
}
if (Object.keys(templates).length!==4) throw Error('Missing character configuration');
const text = fs.readFileSync(path.join(raw,'Marriage.txt'),'utf8');
const parsed = new Scene('Marriage',{},new SceneNavigator(['Marriage']),false);
parsed.loadLines(text);
let route, choices, endpoint;
const oldGoto = Scene.prototype.goto;
Scene.prototype.goto = function(label) {
  if (['Mistress','UncleAdvice','RD'].includes(label)) {
    endpoint=label; this.finished=true; return;
  }
  return oldGoto.call(this,label);
};
Scene.prototype.printLine = function(line) { return this.replaceVariables(line); };
Scene.prototype.page_break = function() { this.finished=false; };
Scene.prototype.save = function() {};
Scene.prototype.paragraph = function() {};
Scene.prototype.choice = function(data) {
  const menu=this.lineNum+1;
  const options=this.parseOptions(this.indent,['choice'],false).filter(x=>!x.unselectable);
  const step=choices.length;
  if (route.length<=step) throw {need: options.length};
  const option=options[route[step]];
  choices.push({menu, selected:option.line, ordinal:route[step]});
  this.standardResolution(option);
};
function primitives(obj) {
  return Object.fromEntries(Object.entries(obj).filter(([k,v])=>v===null || ['string','number','boolean'].includes(typeof v)));
}
const results=[];
function explore(prefix, sex, pref, score) {
  if (prefix.length>8) throw Error('Unexpected route depth '+JSON.stringify(prefix)+' choices '+JSON.stringify(choices));
  route=prefix; choices=[]; endpoint=null;
  const template=templates[sex+'/'+pref];
  const stats=JSON.parse(JSON.stringify(template.state));
  global.stats=stats;
  stats.sex=sex; stats.he_pref=pref; stats.relking=score;
  const scene=new Scene('Marriage',stats,new SceneNavigator(['Marriage']),false);
  scene.lines=parsed.lines; scene.labels=parsed.labels; scene.crc=parsed.crc; scene.loaded=true;
  scene.temps=JSON.parse(JSON.stringify(template.temps));
  scene.goto('Chase');
  try { scene.execute(); }
  catch(e) {
    if (e.need) {
      for(let i=0;i<e.need;i++) explore([...prefix,i],sex,pref,score);
      return;
    }
    throw e;
  }
  if (!endpoint) throw Error('Unexpected nonterminal');
  results.push({sex,pref,score,route:prefix,choices,endpoint,relking:stats.relking,
    wealth:stats.wealth,reputation:stats.reputation,accepted:scene.temps.accepted_something,
    initial_wealth:template.state.wealth,initial_reputation:template.state.reputation,
    template_seed:template.seed});
}
for (const sex of (process.env.AUDIT_GRID_SMALL ? ['female'] : ['female','male'])) for(const pref of (process.env.AUDIT_GRID_SMALL ? ['he'] : ['she','he'])) {
  for(let score=0;score<=(process.env.AUDIT_GRID_SMALL ? 0 : 100);score++) explore([],sex,pref,score);
}
fs.writeFileSync(target,JSON.stringify(results));
console.log('Local terminal executions: '+results.length);
