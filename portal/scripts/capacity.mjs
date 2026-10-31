// Local functional workload, not an estimate of Cloudflare edge CPU or billing.
import {performance} from 'node:perf_hooks';
import {mkdir,writeFile} from 'node:fs/promises';
import {createApp} from '../src/app.mjs';
import {hash} from '../src/security.mjs';
import {D1} from '../tests/helpers.mjs';
import site from '../generated/site.mjs';

const db=new D1();let time=Date.now();
const env={DB:db,ORIGIN:'https://gyanhq.com',ADMIN_EMAIL:'owner@gmail.com'};
const app=createApp(site,{clock:()=>time});
for(const module of site.modules)db.sqlite.prepare('INSERT INTO releases VALUES(?,?,?,?)').run(module.id,1,0,time);
const users=50,minutes=240,page=site.modules[0].path;
for(let i=0;i<users;i++){
  const sub=`load-${i}`,email=`load-${i}@example.com`;
  db.sqlite.prepare('INSERT INTO identities VALUES(?,?,?,?)').run(sub,email,sub,time);
  db.sqlite.prepare('INSERT INTO approvals VALUES(?,?,?,?,?)').run(email,1,sub,time,time);
  db.sqlite.prepare('INSERT INTO registrations VALUES(?,?,?)').run(sub,'2026-10-30',time);
  db.sqlite.prepare('INSERT INTO sessions VALUES(?,?,?,?,?)').run(await hash(sub),sub,email,sub,time+43200000);
}
let requests=0,failures=0;
const latencies=[],start=performance.now();
for(let minute=0;minute<=minutes;minute++){
  if(minute)time+=60000;
  for(let i=0;i<users;i++){
    const sub=`load-${i}`,before=performance.now();
    const request=new Request('https://gyanhq.com/adk-training/api/activity',{method:'POST',headers:{Cookie:`gyanhq_training_session=${sub}`,Origin:env.ORIGIN,'X-CSRF-Token':sub,'Content-Type':'application/json'},body:JSON.stringify({id:`capacity-visit-${String(i).padStart(5,'0')}`,page,sequence:minute,activeMs:minute*60000})});
    const response=await app.fetch(request,env);requests++;if(!response.ok)failures++;latencies.push(performance.now()-before);
  }
}
latencies.sort((a,b)=>a-b);
const stored=db.sqlite.prepare('SELECT COUNT(*) visits,SUM(active_ms) active_ms FROM visits').get();
const result={users,minutes,requests,failures,storedVisits:stored.visits,totalActiveHours:stored.active_ms/3600000,localElapsedMs:Math.round(performance.now()-start),localRequestP95Ms:latencies[Math.floor(latencies.length*.95)],note:'In-memory SQLite/Node wall times only. Not Cloudflare CPU, D1 rows scanned/written, or account-wide quota measurements.'};
await mkdir(new URL('../generated/',import.meta.url),{recursive:true});
await writeFile(new URL('../generated/capacity.json',import.meta.url),JSON.stringify(result,null,2));
console.log(JSON.stringify(result,null,2));db.sqlite.close();
if(failures || stored.visits!==users || stored.active_ms!==users*minutes*60000)process.exitCode=1;
