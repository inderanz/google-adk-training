// Disposable integration server: real Worker handler + real SQLite + built
// assets. Seeded sessions exist only here; there is no dev-login Worker route.
import {createServer} from 'node:http';
import {readFile,mkdir} from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
import path from 'node:path';
import assert from 'node:assert/strict';
import {chromium} from 'playwright';
import {D1} from '../tests/helpers.mjs';
import {createApp} from '../src/app.mjs';
import {hash,randomToken} from '../src/security.mjs';
import site from '../generated/site.mjs';

const base='/adk-training/',origin='http://localhost:8899';
const dist=fileURLToPath(new URL('../dist/',import.meta.url));
const artifacts=fileURLToPath(new URL('../generated/browser/',import.meta.url));
await mkdir(artifacts,{recursive:true});
const db=new D1(),tokens={owner:randomToken(),learner:randomToken()};
for(const [sub,token]of Object.entries(tokens)){
  const email=`${sub}@gmail.com`;
  db.sqlite.prepare('INSERT INTO identities VALUES(?,?,?,?)').run(sub,email,sub,Date.now());
  db.sqlite.prepare('INSERT INTO sessions VALUES(?,?,?,?,?)').run(await hash(token),sub,email,`csrf-${sub}`,Date.now()+43200000);
  if(sub==='learner')db.sqlite.prepare('INSERT INTO approvals VALUES(?,?,?,?,?)').run(email,1,sub,Date.now(),Date.now());
}
const env={DB:db,ORIGIN:origin,ADMIN_EMAIL:'owner@gmail.com',LOCAL_DEV:'true',ASSETS:{async fetch(request){
  const filename=path.resolve(dist,'.'+decodeURIComponent(new URL(request.url).pathname));
  if(!filename.startsWith(dist))return new Response('Not found',{status:404});
  try{
    const bytes=await readFile(filename);
    const type={'.html':'text/html','.js':'text/javascript','.css':'text/css','.svg':'image/svg+xml','.png':'image/png','.jpg':'image/jpeg','.json':'application/json','.txt':'text/plain'}[path.extname(filename)]||'application/octet-stream';
    return new Response(bytes,{headers:{'Content-Type':type}});
  }catch{return new Response('Not found',{status:404});}
}}};
const app=createApp(site);
const server=createServer(async(req,res)=>{
  try{
    const chunks=[];for await(const chunk of req)chunks.push(chunk);
    const request=new Request(origin+req.url,{method:req.method,headers:req.headers,...(chunks.length?{body:Buffer.concat(chunks)}:{})});
    const response=await app.fetch(request,env);res.writeHead(response.status,Object.fromEntries(response.headers));res.end(Buffer.from(await response.arrayBuffer()));
  }catch(error){res.writeHead(500);res.end(error.message);}
});
await new Promise(resolve=>server.listen(8899,'localhost',resolve));
let browser;
const checks=[];
const check=(ok,label)=>{assert.ok(ok,label);checks.push(label);};
try{
  const channel=process.env.PLAYWRIGHT_CHANNEL||'chrome';
  browser=await chromium.launch({headless:true,...(channel==='chromium'?{}:{channel})});
  const context=await browser.newContext({viewport:{width:1440,height:1000}});
  const page=await context.newPage(),errors=[];
  page.on('pageerror',error=>errors.push(error.message));
  await page.goto(origin+base);
  check(await page.getByRole('link',{name:'Sign in with Google'}).isVisible(),'public sign-in page');
  await context.addCookies([{name:'gyanhq_training_session',value:tokens.owner,url:origin+base,httpOnly:true,sameSite:'Lax'}]);
  await page.goto(origin+base+'admin/');
  await page.getByText('learner@gmail.com',{exact:true}).first().waitFor();
  check(await page.locator('#releases section').count()===site.modules.length,'all modules shown in admin');
  check(await page.locator('#releases input:checked').count()===0,'everything starts locked');
  await page.locator('#approve input').fill('new@gmail.com');await page.getByRole('button',{name:'Approve email',exact:true}).click();
  await page.locator('#users').getByText('new@gmail.com',{exact:true}).waitFor();check(true,'manual learner approval UI');
  const selected=site.modules.find(m=>m.id==='module13_5-firestore-persistence');
  const moduleCard=page.locator('#releases section').filter({has:page.getByRole('heading',{name:selected.title,exact:true})});
  await moduleCard.getByLabel('Release lessons and labs').check();await moduleCard.getByRole('button',{name:'Save release'}).click();
  await page.getByRole('status').filter({hasText:'Release saved'}).waitFor();
  check(db.sqlite.prepare('SELECT lessons FROM releases WHERE module_id=?').get(selected.id).lessons===1,'module release UI persists');
  const learnerContext=await browser.newContext({viewport:{width:390,height:844}});
  await learnerContext.addCookies([{name:'gyanhq_training_session',value:tokens.learner,url:origin+base,httpOnly:true,sameSite:'Lax'}]);
  const learner=await learnerContext.newPage();learner.on('pageerror',error=>errors.push(error.message));
  await learner.goto(origin+base+'learn/');await learner.locator('#catalog article').first().waitFor();
  check(await learner.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),'mobile catalogue fits viewport');
  const learnerCard=learner.locator('#catalog article').filter({has:learner.getByRole('heading',{name:new RegExp(selected.title.replace(/[.*+?^${}()|[\]\\]/g,'\\$&'))})});
  check(await learnerCard.getByText(/not released/).count()>0,'solutions remain visibly locked');
  const protectedSolution=selected.pages.find(p=>p.solution);
  check((await learner.request.get(origin+protectedSolution.path)).status()===403,'solution URL denied');
  const solutionChunk=Object.entries(site.assets).find(([p,v])=>p.endsWith('.js')&&v.policy?.module===selected.id&&v.policy.solution);
  check((await learner.request.get(origin+solutionChunk[0])).status()===403,'solution JS denied');
  const lessonResponse=await learner.goto(origin+selected.path);check(lessonResponse.status()===200,'released lesson loads');
  await learner.getByRole('button',{name:'Sign out',exact:true}).first().waitFor();
  await learner.waitForTimeout(2500);
  check(await learner.locator('pre').count()>0,'course code blocks preserved');
  // Module 4 contains diagrams in both the committed and edited curricula.
  const diagramModule=site.modules.find(m=>m.id==='module04-agent-deep-dive');
  db.sqlite.prepare('INSERT OR REPLACE INTO releases VALUES(?,?,?,?)').run(diagramModule.id,1,0,Date.now());
  await learner.goto(origin+diagramModule.path);
  const mermaid=learner.locator('svg[id^="mermaid"], .docusaurus-mermaid-container svg, .mermaid svg');
  await mermaid.first().waitFor({timeout:30000});check(await mermaid.count()>0,'Mermaid diagrams render');
  check(await learner.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),'mobile lesson fits viewport');
  await learner.screenshot({path:path.join(artifacts,'lesson-mobile.png'),fullPage:false});
  check(db.sqlite.prepare('SELECT COUNT(*) n FROM visits').get().n>=1,'learner visit recorded');
  await learner.goto(origin+base+'learn/');
  await page.bringToFront();await moduleCard.getByLabel('Release solutions').check();await moduleCard.getByRole('button',{name:'Save release'}).click();
  await page.waitForFunction(()=>document.getElementById('status').textContent.startsWith('Release saved'));
  await page.waitForTimeout(150);
  check((await learner.request.get(origin+protectedSolution.path)).status()===200,'solution release takes effect');
  await page.locator('#report-filters input[name=email]').fill('learner@gmail.com');await page.getByRole('button',{name:'View report',exact:true}).click();
  await page.locator('#reports').getByText('learner@gmail.com',{exact:true}).first().waitFor();check(true,'admin learner report');
  const downloadEvent=page.waitForEvent('download');await page.getByRole('button',{name:'Export CSV'}).click();const download=await downloadEvent;await download.saveAs(path.join(artifacts,'activity.csv'));check(true,'CSV download');
  const userRow=page.locator('#users tr').filter({has:page.getByText('learner@gmail.com',{exact:true})});
  await userRow.getByRole('button',{name:'Revoke',exact:true}).click();await page.getByRole('status').filter({hasText:'Access updated'}).waitFor();
  check((await learner.request.get(origin+selected.path)).status()===401,'revocation invalidates browser session');
  await page.setViewportSize({width:390,height:844});check(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),'mobile admin fits viewport');
  await page.screenshot({path:path.join(artifacts,'admin-mobile.png'),fullPage:false});
  check(errors.length===0,`no browser runtime errors: ${errors.join('; ')}`);
  console.log(JSON.stringify({passed:checks.length,checks,artifacts},null,2));
}finally{await browser?.close();await new Promise(resolve=>server.close(resolve));db.sqlite.close();}
