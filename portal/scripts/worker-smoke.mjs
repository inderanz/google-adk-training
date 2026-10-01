import {spawn,spawnSync} from 'node:child_process';
import {mkdir,writeFile} from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
import assert from 'node:assert/strict';
import os from 'node:os';
import path from 'node:path';
import site from '../generated/site.mjs';
import {hash,randomToken} from '../src/security.mjs';

const cwd=fileURLToPath(new URL('../',import.meta.url));
const cli=fileURLToPath(new URL('../node_modules/wrangler/bin/wrangler.js',import.meta.url));
const env={...process.env,WRANGLER_SEND_METRICS:'false',XDG_CONFIG_HOME:process.env.XDG_CONFIG_HOME||path.join(os.tmpdir(),'gyanhq-wrangler')};
const persist='generated/worker-smoke-state',port=8791,origin=`http://localhost:${port}`,base='/adk-training/';
function run(args){
  const result=spawnSync(process.execPath,[cli,...args],{cwd,env,encoding:'utf8'});
  if(result.status!==0)throw new Error(result.stderr+result.stdout);
}
await mkdir(new URL('../generated/',import.meta.url),{recursive:true});
run(['d1','migrations','apply','gyanhq-training-local','--local','--env','local','--persist-to',persist]);
const token=randomToken(),tokenHash=await hash(token),time=Date.now();
const sql=`DELETE FROM sessions; DELETE FROM approvals; DELETE FROM identities; DELETE FROM releases;
INSERT INTO identities VALUES ('smoke','smoke@example.com','Local test',${time});
INSERT INTO approvals VALUES ('smoke@example.com',1,'smoke',${time},${time});
INSERT INTO sessions VALUES ('${tokenHash}','smoke','smoke@example.com','smoke-csrf',${time+3600000});
INSERT INTO releases VALUES ('${site.modules[0].id}',1,0,${time});`;
await writeFile(new URL('../generated/worker-smoke.sql',import.meta.url),sql);
run(['d1','execute','gyanhq-training-local','--local','--env','local','--persist-to',persist,'--file','generated/worker-smoke.sql']);
const child=spawn(process.execPath,[cli,'dev','--env','local','--port',String(port),'--var',`ORIGIN:${origin}`,'--persist-to',persist],{cwd,env,stdio:['ignore','pipe','pipe']});
let logs='';child.stdout.on('data',b=>logs+=b);child.stderr.on('data',b=>logs+=b);
const checks=[];
try{
  let ready=false;
  for(let i=0;i<100;i++){
    try{if((await fetch(origin+base)).ok){ready=true;break;}}catch{}
    await new Promise(resolve=>setTimeout(resolve,200));
  }
  assert.ok(ready,logs);
  const request=(path,auth=false)=>fetch(origin+path,{headers:auth?{Cookie:`gyanhq_training_session=${token}`}:{},redirect:'manual'});
  async function check(path,expected,auth,label){const response=await request(path,auth);assert.equal(response.status,expected,`${label}: ${await response.text()}`);checks.push(label);return response;}
  await check(base,200,false,'real Worker public landing');
  await check(base+'portal/ui.js',200,false,'real static asset binding serves portal JS');
  const lesson=site.modules[0].path;
  await check(lesson,401,false,'real Worker denies anonymous course access');
  const response=await check(lesson,200,true,'real D1 session and release authorize actual HTML');
  assert.equal(response.headers.get('Cache-Control'),'private, no-store');
  const chunk=Object.entries(site.assets).find(([p,a])=>p.endsWith('.js')&&a.policy?.module===site.modules[0].id&&!a.policy.solution);
  await check(chunk[0],200,true,'real static asset binding serves permitted lesson chunk');
  const solution=site.modules[0].pages.find(p=>p.solution).path;
  await check(solution,403,true,'real Worker denies unreleased solution');
  await check(base+'api/admin/users',403,true,'real Worker denies learner admin API');
  await check(base+'unclassified-secret.json',404,true,'real Worker denies unclassified files');
  console.log(JSON.stringify({passed:checks.length,checks},null,2));
}finally{
  child.kill('SIGTERM');
  await new Promise(resolve=>{child.once('exit',resolve);setTimeout(()=>{child.kill('SIGKILL');resolve();},2000).unref();});
}
