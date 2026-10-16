#!/usr/bin/env node
'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const crypto=require('node:crypto');
const asar=require('@electron/asar');
const args=process.argv.slice(2);
const appRoot=path.resolve(args[args.indexOf('--app-root')+1]||'');
if(!args.includes('--app-root')) throw new Error('--app-root is required');
const resources=fs.existsSync(path.join(appRoot,'Contents/Resources')) ? path.join(appRoot,'Contents/Resources') : path.join(appRoot,'resources');
const archive=path.join(resources,'app.asar');
const pkg=JSON.parse(asar.extractFile(archive,'package.json'));
assert.equal(pkg.name,'naifrog-on-desk');
assert.equal(pkg.version,require('../package.json').version);
if (fs.existsSync(path.join(appRoot,'Contents/Info.plist'))) {
  const readPlist = (key) => require('node:child_process').execFileSync('/usr/bin/plutil',['-extract',key,'raw','-o','-',path.join(appRoot,'Contents/Info.plist')],{encoding:'utf8'}).trim();
  assert.equal(readPlist('CFBundleIdentifier'),'io.github.noboru2utokyo.naifrog-on-desk');
  assert.equal(readPlist('CFBundleShortVersionString'),pkg.version);
  assert.equal(readPlist('CFBundleExecutable'),'Naifrog on Desk');
}
const prefsSource=asar.extractFile(archive,'src/prefs.js').toString();
assert.match(prefsSource,/theme: \{ type: "string", default: "naifrog" \}/);
const updaterSource=asar.extractFile(archive,'src/updater.js').toString();
assert(!updaterSource.includes('rullerzhou-afk/clawd-on-desk'));
assert(updaterSource.includes('/repos/Noboru2UTokyo/naifrog-on-desk/releases/latest'));
const packedTheme=path.join(resources,'app.asar.unpacked/themes/naifrog');
const sourceTheme=path.resolve(__dirname,'../themes/naifrog');
const files=[];
function visit(dir){for(const e of fs.readdirSync(dir,{withFileTypes:true})){const p=path.join(dir,e.name);if(e.isDirectory())visit(p);else files.push(path.relative(sourceTheme,p));}}
visit(sourceTheme);
for(const file of files) assert.deepEqual(fs.readFileSync(path.join(packedTheme,file)),fs.readFileSync(path.join(sourceTheme,file)),file);
const manifest=JSON.parse(fs.readFileSync(path.join(packedTheme,'theme.json')));
assert.equal(manifest.version,'1.3.2');
assert.deepEqual(manifest.states.idle,['idle.webp']);
assert.equal(manifest.sounds.confirm,'confirm.mp3');
assert.equal(manifest.timings.minDisplay.attention,12000);
const updateConfig=fs.readFileSync(path.join(resources,'app-update.yml'),'utf8');
assert.match(updateConfig,/owner: Noboru2UTokyo/);assert.match(updateConfig,/repo: naifrog-on-desk/);
for(const file of ['NOTICE.md','LICENSE']) assert(asar.extractFile(archive,file).length>0);
const result={ok:true,version:pkg.version,theme:manifest.version,defaultTheme:'naifrog',verifiedThemeFiles:files.length,updateRepository:'Noboru2UTokyo/naifrog-on-desk',asarSha256:crypto.createHash('sha256').update(fs.readFileSync(archive)).digest('hex')};
const artifactIndex=args.indexOf('--artifact-root');
if (artifactIndex>=0) {
  const artifactRoot=path.resolve(args[artifactIndex+1]);
  const metadata=require('js-yaml').load(fs.readFileSync(path.join(artifactRoot,'latest-mac.yml'),'utf8'));
  const base=`Naifrog-on-Desk-${pkg.version}-arm64`;
  assert.equal(metadata.version,pkg.version);
  assert.deepEqual(metadata.files.map(f=>f.url).sort(),[`${base}.dmg`,`${base}.zip`]);
  assert.equal(metadata.path,`${base}.zip`);
  result.artifacts=[];
  for(const file of metadata.files) {
    const bytes=fs.readFileSync(path.join(artifactRoot,file.url));
    assert.equal(bytes.length,file.size);
    assert.equal(crypto.createHash('sha512').update(bytes).digest('base64'),file.sha512);
    const blockmap=JSON.parse(require('node:zlib').gunzipSync(fs.readFileSync(path.join(artifactRoot,file.url+'.blockmap'))));
    assert.equal(typeof blockmap.version,'string');
    assert(Array.isArray(blockmap.files)&&blockmap.files.length>0);
    result.artifacts.push({name:file.url,bytes:bytes.length,sha256:crypto.createHash('sha256').update(bytes).digest('hex')});
  }
  assert.equal(metadata.sha512,metadata.files.find(f=>f.url===metadata.path).sha512);
  result.updaterMetadataVerified=true;
}
const outputIndex=args.indexOf('--output');if(outputIndex>=0)fs.writeFileSync(args[outputIndex+1],JSON.stringify(result,null,2)+'\n');
console.log(JSON.stringify(result,null,2));
