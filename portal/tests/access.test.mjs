import test from 'node:test';
import assert from 'node:assert/strict';
import {fixture,BASE,lesson,solution,second,moduleId} from './helpers.mjs';

test('landing is public; protected HTML and bundles require a session',async()=>{
  const f=await fixture();assert.equal((await f.request(BASE,{role:null})).status,200);
  for(const path of [lesson,solution,`${BASE}assets/main.js`,`${BASE}assets/solution.js`])assert.equal((await f.request(path,{role:null})).status,401);
  assert.equal(f.assetCalls(),0);
});
test('all modules default locked; releasing lessons does not release solutions or other modules',async()=>{
  const f=await fixture();assert.equal((await f.request(lesson)).status,403);f.release();
  assert.equal((await f.request(lesson)).status,200);
  assert.equal((await f.request(`${lesson}index.html`)).status,200);
  for(const path of [solution,second,`${BASE}assets/solution.js`,`${BASE}assets/solution.pdf`])assert.equal((await f.request(path)).status,403);
  assert.equal((await f.request(`${BASE}assets/lesson.js`)).status,200);
  f.release(true,true);assert.equal((await f.request(solution)).status,200);
  assert.equal((await f.request(`${BASE}assets/solution.pdf`)).status,200);
});
test('administrator previews locked material, learners cannot access administration',async()=>{
  const f=await fixture();assert.equal((await f.request(solution,{role:'owner'})).status,200);
  for(const path of ['admin/','api/admin/users','api/admin/modules','api/admin/reports'])assert.equal((await f.request(BASE+path)).status,403);
  assert.equal((await f.request(`${BASE}admin/`,{role:'owner'})).status,200);
  assert.equal(f.db.sqlite.prepare('SELECT COUNT(*) n FROM audit').get().n,1);
});
test('revocation invalidates sessions; reapproval does not restore old sessions',async()=>{
  const f=await fixture();f.release();
  assert.equal((await f.request(`${BASE}api/admin/users`,{role:'owner',method:'DELETE',body:{email:'learner@gmail.com'}})).status,200);
  assert.equal((await f.request(lesson)).status,401);
  assert.equal((await f.request(`${BASE}api/admin/users`,{role:'owner',method:'POST',body:{email:'LEARNER@gmail.com'}})).status,200);
  assert.equal((await f.request(lesson)).status,401);
});
test('approval is rechecked even when session remains',async()=>{
  const f=await fixture();f.release();f.db.sqlite.prepare('UPDATE approvals SET active=0 WHERE email=?').run('learner@gmail.com');
  assert.equal((await f.request(lesson)).status,403);
});
test('expired sessions, unknown files, alternate origins and unavailable DB fail closed',async()=>{
  const f=await fixture();f.release();
  assert.equal((await f.request(lesson,{origin:'https://alternate.workers.dev'})).status,404);
  assert.equal((await f.request(`${BASE}assets/unknown.js`)).status,404);
  assert.equal((await f.request(`${BASE}assets/lesson.js.map`)).status,404);
  assert.equal((await f.request(`${BASE}docs%2fmodule01-intro/`)).status,404);
  f.advance(43200001);assert.equal((await f.request(lesson)).status,401);
  f.env.DB=null;assert.equal((await f.request(lesson)).status,503);
  assert.equal(f.assetCalls(),0);
});
test('cached/range requests are authorized and get private no-store responses',async()=>{
  const f=await fixture();f.release();
  const response=await f.request(lesson,{headers:{'If-None-Match':'cached',Range:'bytes=0-50'}});
  assert.equal(response.status,200);assert.equal(response.headers.get('Cache-Control'),'private, no-store');
  f.release(false,false);assert.equal((await f.request(lesson,{headers:{'If-None-Match':'cached'}})).status,403);
});
test('mutations require origin and CSRF, logout is POST-only',async()=>{
  const f=await fixture();
  for(const headers of [{'X-CSRF-Token':'wrong'},{Origin:'https://attacker.test'}]){
    assert.equal((await f.request(`${BASE}api/admin/users`,{role:'owner',method:'POST',body:{email:'new@gmail.com'},headers})).status,403);
  }
  assert.equal((await f.request(`${BASE}auth/logout`)).status,405);
  assert.equal((await f.request(`${BASE}auth/logout`,{method:'POST'})).status,204);
  assert.equal((await f.request(`${BASE}api/me`)).status,401);
});
test('relocking a module locks solutions and writes an audit entry',async()=>{
  const f=await fixture();f.release(true,true);
  const response=await f.request(`${BASE}api/admin/modules`,{role:'owner',method:'PUT',body:{id:moduleId,lessons:false,solutions:true}});
  assert.equal(response.status,200);assert.equal((await f.request(solution)).status,403);
  assert.equal(f.db.sqlite.prepare('SELECT solutions FROM releases WHERE module_id=?').get(moduleId).solutions,0);
  assert.equal(f.db.sqlite.prepare('SELECT COUNT(*) n FROM audit').get().n,1);
});
test('catalogue lists locked content without including lesson bodies',async()=>{
  const f=await fixture();const data=await(await f.request(`${BASE}api/catalog`)).json();
  assert.equal(data.modules[0].available,false);assert.equal(data.modules[0].pages[1].available,false);
  f.release();const released=await(await f.request(`${BASE}api/catalog`)).json();
  assert.equal(released.modules[0].pages[0].available,true);assert.equal(released.modules[0].pages[1].available,false);
});
test('legacy course links redirect to their protected canonical pages',async()=>{
  const f=await fixture();
  const response=await f.request(`${BASE}${moduleId}/lab-solution`);
  assert.equal(response.status,308);assert.equal(response.headers.get('Location'),solution);
  assert.equal((await f.request(response.headers.get('Location'))).status,403);
  assert.equal((await f.request(`${BASE}not-a-course-page`)).status,404);
});
test('input validation rejects malformed, oversized and invalid administrative data',async()=>{
  const f=await fixture();
  for(const email of ['bad','owner@gmail.com','a'.repeat(17000)])assert.notEqual((await f.request(`${BASE}api/admin/users`,{role:'owner',method:'POST',body:{email}})).status,200);
  assert.equal((await f.request(`${BASE}api/admin/modules`,{role:'owner',method:'PUT',body:{id:'unknown',lessons:true,solutions:true}})).status,400);
  assert.equal((await f.request(`${BASE}api/admin/users`,{role:'owner',method:'POST',body:null})).status,400);
});
