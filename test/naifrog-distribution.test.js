'use strict';
const {test} = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const prefs = require('../src/prefs');
const loader = require('../src/theme-loader');
const pkg = require('../package.json');

test('fresh profiles select the complete bundled Naifrog theme; saved choices persist', () => {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'naifrog-default-'));
  try {
    const file = path.join(dir, 'prefs.json');
    const fresh = prefs.load(file).snapshot;
    assert.equal(fresh.theme, 'naifrog');
    loader.init(path.join(__dirname, '../src'), dir);
    const theme = loader.loadTheme(fresh.theme, {strict:true});
    assert.equal(theme._id, 'naifrog');
    assert.equal(theme.version, pkg.version);
    assert.deepEqual(theme.states.idle, ['idle.webp']);
    assert.equal(theme.timings.minDisplay.attention,12000);
    assert.equal(theme.sounds.confirm,'confirm.mp3');
    const ctx = loader.createThemeContext(theme);
    for(const files of Object.values(theme.states)) for(const name of files)
      assert(fs.existsSync(ctx.resolveAssetPath(name)), name);
    fs.writeFileSync(file, JSON.stringify({...fresh,theme:'calico'}));
    assert.equal(prefs.load(file).snapshot.theme,'calico');
  } finally {fs.rmSync(dir,{recursive:true,force:true});}
});

test('approved Naifrog tiers, sleep timings and retained media survive packaging', () => {
  const crypto = require('node:crypto');
  const resolver = require('../src/state-visual-resolver');
  const dir = path.join(__dirname, '../themes/naifrog');
  const theme = JSON.parse(fs.readFileSync(path.join(dir, 'theme.json')));
  const approved = JSON.parse(fs.readFileSync(path.join(dir, 'approved-assets.json')));
  for (const a of approved.assets) {
    const bytes = fs.readFileSync(path.join(dir, 'assets', a.file));
    assert.equal(crypto.createHash('sha256').update(bytes).digest('hex'), a.sha256, a.file);
  }
  for (const [count, expected] of [[1,'working.webp'],[2,'work-headphones.webp'],[3,'work-building.webp'],[8,'work-building.webp']]) {
    const sessions = new Map(Array.from({length:count}, (_, i) => [i, {state:'working'}]));
    assert.equal(resolver.getWorkingSvg({sessions,theme,stateSvgs:theme.states}), expected);
  }
  for (const count of [1,2,8]) {
    const sessions = new Map(Array.from({length:count}, (_, i) => [i, {state:'juggling'}]));
    assert.equal(resolver.getJugglingSvg({sessions,theme,stateSvgs:theme.states}), 'work-headphones.webp');
  }
  assert.deepEqual(theme.states.roam, {files:[],fallbackTo:'idle'});
  assert.equal(fs.existsSync(path.join(dir,'assets/roam.webp')), false);
  assert.deepEqual(theme.states.dozing,theme.states.sleeping);
  assert.deepEqual(theme.states.collapsing,theme.states.sleeping);
  assert.equal(theme.timings.yawnDuration,approved.assets.find(a=>a.file==='yawning.webp').durationMs);
  assert.equal(theme.timings.wakeDuration,approved.assets.find(a=>a.file==='waking.webp').durationMs);
  assert.deepEqual(theme.idleAnimations,[{file:'bubble.webp',duration:8000}]);
  assert.equal(approved.assets.find(a=>a.file==='idle.webp').sha256,'3b523f08a7c3fbae1bba5c6ec50e276216e0e2dab3c2a564a96bd932926ed2a9');
  assert.equal(approved.assets.find(a=>a.file==='happy.webp').durationMs,12000);
});

test('distribution identity, update endpoints and URL registration remain separate', () => {
  assert.equal(pkg.name,'naifrog-on-desk');
  assert.equal(pkg.build.appId,'io.github.noboru2utokyo.naifrog-on-desk');
  assert.equal(pkg.build.productName,'Naifrog on Desk');
  assert.deepEqual(pkg.build.publish,[{provider:'github',owner:'Noboru2UTokyo',repo:'naifrog-on-desk'}]);
  assert.deepEqual(pkg.build.protocols,[]);
  const updater=fs.readFileSync(path.join(__dirname,'../src/updater.js'),'utf8');
  assert(!updater.includes('rullerzhou-afk/clawd-on-desk'));
  assert(updater.includes('/repos/Noboru2UTokyo/naifrog-on-desk/releases/latest'));
});
