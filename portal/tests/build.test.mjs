import test from 'node:test';
import assert from 'node:assert/strict';
import {existsSync,readFileSync,readdirSync,statSync} from 'node:fs';
import path from 'node:path';
import policy from '../build/policy.cjs';

test('build permissions retain decimal modules and distinguish solutions',()=>{
  assert.deepEqual(policy.sourcePolicy('/x/training/module13_5-firestore-persistence/lab-solution.md'),{module:'module13_5-firestore-persistence',solution:true});
  assert.deepEqual(policy.sourcePolicy('/x/training/module13_5-firestore-persistence/lab.md'),{module:'module13_5-firestore-persistence',solution:false});
});
test('mixed lesson/solution and cross-module bundles fail the build',()=>{
  const lesson={module:'module01',solution:false};
  assert.throws(()=>policy.isolatedPolicy([lesson,{module:'module01',solution:true}],'chunk'),/Mixed content/);
  assert.throws(()=>policy.isolatedPolicy([lesson,{module:'module02',solution:false}],'chunk'),/Mixed content/);
  assert.deepEqual(policy.isolatedPolicy([null,lesson,lesson],'chunk'),lesson);
});
test('generated manifest covers real course HTML and stays within free asset limits',{skip:!existsSync(new URL('../generated/site.json',import.meta.url))},()=>{
  const site=JSON.parse(readFileSync(new URL('../generated/site.json',import.meta.url),'utf8'));
  assert.ok(site.modules.length>=40);
  assert.ok(site.modules.some(m=>m.id==='module13_5-firestore-persistence'));
  for(const module of site.modules)for(const page of module.pages)assert.ok(site.pages[page.path],`Noncanonical catalogue link: ${page.path}`);
  for(const [url,p]of Object.entries(site.pages)){
    assert.ok(site.assets[url],`Missing ${url}`);
    assert.deepEqual(site.assets[url].policy,p.policy);
    if(url.includes('/lab-solution/'))assert.equal(p.policy.solution,true);
  }
  assert.ok(Object.entries(site.assets).some(([file,p])=>file.endsWith('.js')&&p.policy?.solution));
  assert.ok(Object.entries(site.assets).some(([file,p])=>file.endsWith('.js')&&p.policy&&!p.policy.solution));
  const walk=dir=>readdirSync(dir,{withFileTypes:true}).flatMap(item=>item.isDirectory()?walk(path.join(dir,item.name)):[path.join(dir,item.name)]);
  const files=walk(new URL('../dist/',import.meta.url).pathname);assert.ok(files.length<20000);
  for(const file of files){assert.ok(statSync(file).size<=25*1024*1024,`Oversized ${file}`);assert.ok(!file.endsWith('.map'));}
});
