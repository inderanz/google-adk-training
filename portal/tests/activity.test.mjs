import test from 'node:test';
import assert from 'node:assert/strict';
import {fixture,BASE,lesson} from './helpers.mjs';
import {ActivityClock} from '../public/tracking-core.js';
import {csv} from '../src/security.mjs';
const id='12345678-1234-1234-1234-123456789012';
const update=(f,sequence,activeMs,role='learner')=>f.request(`${BASE}api/activity`,{role,method:'POST',body:{id,page:lesson,sequence,activeMs}});

test('activity is cumulative, deduplicated, server bounded, and bound to the authenticated learner',async()=>{
  const f=await fixture();f.release();await update(f,0,0);f.advance(60000);await update(f,1,60000);
  await update(f,1,60000);await update(f,0,0);await update(f,2,60000,'other');
  let visit=f.db.sqlite.prepare('SELECT * FROM visits WHERE id=?').get(id);
  assert.equal(visit.active_ms,60000);assert.equal(visit.sub,'learner');
  f.advance(1000);await update(f,2,1000000);visit=f.db.sqlite.prepare('SELECT * FROM visits WHERE id=?').get(id);
  assert.equal(visit.active_ms,61000);
});
test('revoked learners cannot track pages; admin browsing is excluded',async()=>{
  const f=await fixture();f.db.sqlite.prepare('UPDATE approvals SET active=0').run();assert.equal((await update(f,0,0)).status,403);
  assert.deepEqual(await(await update(f,0,0,'owner')).json(),{ignored:true});
  assert.equal(f.db.sqlite.prepare('SELECT COUNT(*) n FROM visits').get().n,0);
});
test('reports filter and summarize; learner cannot read reports; deletion preserves approval',async()=>{
  const f=await fixture();f.release();await update(f,0,0);f.advance(60000);await update(f,1,60000);
  const response=await f.request(`${BASE}api/admin/reports?email=learner%40gmail.com`,{role:'owner'});
  const report=await response.json();assert.equal(report.summary.visits,1);assert.equal(report.summary.active_ms,60000);assert.equal(report.visits[0].active_minutes,1);
  assert.equal((await f.request(`${BASE}api/admin/reports`)).status,403);
  const empty=await(await f.request(`${BASE}api/admin/reports?email=nobody%40gmail.com`,{role:'owner'})).json();assert.equal(empty.summary.visits,0);
  const exported=await f.request(`${BASE}api/admin/reports?format=csv`,{role:'owner'});assert.match(await exported.text(),/learner@gmail.com/);
  await f.request(`${BASE}api/admin/reports`,{role:'owner',method:'DELETE',body:{email:'learner@gmail.com'}});
  assert.equal(f.db.sqlite.prepare('SELECT COUNT(*) n FROM visits').get().n,0);
  assert.equal(f.db.sqlite.prepare('SELECT active FROM approvals WHERE email=?').get('learner@gmail.com').active,1);
});
test('90-day cleanup expires activity and sessions but keeps access and release settings',async()=>{
  const f=await fixture();f.release();await update(f,0,0);f.advance(91*86400000);
  await f.app.scheduled({},f.env);
  assert.equal(f.db.sqlite.prepare('SELECT COUNT(*) n FROM visits').get().n,0);
  assert.equal(f.db.sqlite.prepare('SELECT COUNT(*) n FROM sessions').get().n,0);
  assert.equal(f.db.sqlite.prepare('SELECT COUNT(*) n FROM approvals').get().n,2);
  assert.equal(f.db.sqlite.prepare('SELECT COUNT(*) n FROM releases').get().n,1);
});
test('activity clock pauses when hidden, unfocused, or idle and bounds throttled timers',()=>{
  const c=new ActivityClock(0);
  assert.equal(c.step(1000,true),1000);assert.equal(c.step(2000,false),1000);
  assert.equal(c.step(300001,true),1000);c.touch(300001);
  assert.equal(c.step(301001,true),2000);assert.equal(c.step(310001,true),3500);
});
test('CSV safely quotes data and neutralizes spreadsheet formulas',()=>{
  const output=csv([{name:'=SUM(1,2)',value:'a"b\nc'}],['name','value']);
  assert.match(output,/"'=SUM\(1,2\)"/);assert.match(output,/a""b\nc/);
});
test('date and offset validation rejects ambiguous report ranges',async()=>{
  const f=await fixture();for(const query of ['from=bad','from=2026-02-30','offset=-1','offset=0.5','from=2026-10-03&to=2026-10-01'])assert.equal((await f.request(`${BASE}api/admin/reports?${query}`,{role:'owner'})).status,400);
});
