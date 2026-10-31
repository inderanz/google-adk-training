import test from 'node:test';
import assert from 'node:assert/strict';
import {fixture,BASE,lesson,solution} from './helpers.mjs';

async function start(){
  const f=await fixture({fetcher:async()=>Response.json({id_token:'test'}),verify:async()=>({sub:'new',email:'new@gmail.com',name:'<New>'})});
  const login=await f.request(BASE+'auth/login',{role:null});
  const state=new URL(login.headers.get('Location')).searchParams.get('state');
  const callback=await f.request(BASE+`auth/callback?state=${state}&code=test`,{role:null,headers:{Cookie:`gyanhq_training_oauth=${state}`}});
  assert.equal(callback.headers.get('Location'),BASE+'register/');
  const cookie=callback.headers.get('Set-Cookie').match(/gyanhq_training_registration=[^;]+/)[0];
  const pending=f.db.sqlite.prepare('SELECT * FROM pending_registrations').get();
  const submit=(data={},headers={})=>f.request(BASE+'register/',{role:null,method:'POST',body:{name:'Chosen name',agree:true,version:'2026-10-30',...data},headers:{Cookie:cookie,'X-CSRF-Token':pending.csrf,...headers}});
  return {f,cookie,pending,submit};
}
test('new Google user must consent before account creation, then gets all content and admin can see registration',async()=>{
  const {f,cookie,submit}=await start();
  assert.equal(f.db.sqlite.prepare("SELECT * FROM identities WHERE sub='new'").get(),undefined);
  assert.equal((await f.request(solution,{role:null,headers:{Cookie:cookie}})).status,401);
  const html=await(await f.request(BASE+'register/',{role:null,headers:{Cookie:cookie}})).text();
  assert.match(html,/&lt;New&gt;/);assert.doesNotMatch(html,/checkbox[^>]*checked/);
  for(const data of [{agree:false},{agree:'true'},{version:'old'},{name:''},{name:'x'.repeat(201)}])assert.equal((await submit(data)).status,400);
  assert.equal((await submit({}, {'X-CSRF-Token':'bad'})).status,403);
  assert.equal((await submit({}, {Origin:'https://evil.test'})).status,403);
  const response=await submit({email:'forged@gmail.com'});assert.equal(response.status,200);
  const session=response.headers.get('Set-Cookie').match(/gyanhq_training_session=[^;]+/)[0];
  for(const path of [lesson,solution])assert.equal((await f.request(path,{role:null,headers:{Cookie:session}})).status,200);
  const identity=f.db.sqlite.prepare("SELECT * FROM identities WHERE sub='new'").get();assert.equal(identity.email,'new@gmail.com');assert.equal(identity.name,'Chosen name');
  const users=await(await f.request(BASE+'api/admin/users',{role:'owner'})).json();const user=users.users.find(u=>u.email==='new@gmail.com');
  assert.equal(user.name,'Chosen name');assert.equal(user.agreement_version,'2026-10-30');assert.equal(user.accepted_at,f.time());
  assert.equal((await submit()).status,401);
});
test('expired and cancelled registration do not create accounts; cleanup deletes temporary data',async()=>{
  const {f,submit}=await start();f.advance(600001);assert.equal((await submit()).status,401);
  await f.app.scheduled({},f.env);assert.equal(f.db.sqlite.prepare('SELECT COUNT(*) n FROM pending_registrations').get().n,0);
  assert.equal(f.db.sqlite.prepare("SELECT * FROM identities WHERE sub='new'").get(),undefined);
});
test('revocation during registration is respected',async()=>{
  const {f,submit}=await start();f.db.sqlite.prepare('INSERT INTO approvals VALUES(?,?,?,?,?)').run('new@gmail.com',0,'new',f.time(),f.time());
  assert.equal((await submit()).status,403);
});
test('legacy learner sessions need agreement; administrator is unaffected',async()=>{
  const f=await fixture();f.db.sqlite.exec('DELETE FROM registrations');
  assert.equal((await f.request(solution)).status,403);assert.equal((await f.request(solution,{role:'owner'})).status,200);
});
