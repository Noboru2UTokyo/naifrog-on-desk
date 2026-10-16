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
    assert.equal(theme.version, '1.3.3');
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
