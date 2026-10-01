import {ActivityClock} from './tracking-core.js';

const base='/adk-training/';
const clock=new ActivityClock(performance.now());
let user, sequence=0, stopped=false, ownsLock=false, releaseLock, pendingLock=false;
const visit=crypto.randomUUID(), tab=crypto.randomUUID();
const leaseKey='gyanhq-training-active-tab';
function eligible() {
  return !document.hidden && document.hasFocus() && performance.now()-clock.interaction<300000;
}
function lease() {
  if (navigator.locks) return ownsLock;
  try {
    const current=JSON.parse(localStorage.getItem(leaseKey)||'null');
    if (!current || current.expires<Date.now() || current.tab===tab) {
      localStorage.setItem(leaseKey,JSON.stringify({tab,expires:Date.now()+2500}));
      return true;
    }
    return false;
  } catch { return document.hasFocus(); }
}
function manageLock() {
  if (!navigator.locks) return;
  if (!eligible()) { releaseLock?.(); return; }
  if (ownsLock || pendingLock) return;
  pendingLock=true;
  navigator.locks.request('gyanhq-training-active-tab',{ifAvailable:true},async lock=>{
    pendingLock=false;
    if (!lock || !eligible()) return;
    ownsLock=true;
    await new Promise(resolve=>{releaseLock=resolve;});
    ownsLock=false; releaseLock=undefined;
  }).catch(()=>{pendingLock=false;});
}
async function flush() {
  if (!user || user.admin || stopped) return;
  const update={id:visit,page:location.pathname,sequence:sequence++,activeMs:Math.floor(clock.activeMs)};
  try {
    const response=await fetch(`${base}api/activity`,{method:'POST',credentials:'same-origin',keepalive:true,
      headers:{'Content-Type':'application/json','X-CSRF-Token':user.csrf},body:JSON.stringify(update)});
    if ([401,403].includes(response.status)) { stopped=true; location.assign(`${base}learn/`); }
  } catch { /* Reading continues; the next cumulative update retries elapsed time. */ }
}
for (const name of ['pointerdown','pointermove','keydown','scroll','touchstart']) {
  addEventListener(name,()=>clock.touch(performance.now()),{passive:true});
}
addEventListener('visibilitychange',()=>{manageLock(); if(document.hidden) flush();});
addEventListener('blur',()=>{manageLock();flush();});
addEventListener('pagehide',()=>{releaseLock?.();flush();});
addEventListener('pageshow',event=>{if(event.persisted) location.reload();});

try {
  const response=await fetch(`${base}api/me`,{cache:'no-store'});
  if (response.ok) {
    user=await response.json();
    const bar=document.createElement('div');
    bar.style.cssText='padding:8px 16px;background:#152137;color:#fff;display:flex;gap:16px;align-items:center;flex-wrap:wrap';
    const label=document.createElement('span'); label.textContent=user.email;
    const link=document.createElement('a'); link.href=`${base}learn/`;link.textContent='Course catalogue';link.style.color='#8edbff';
    const logout=document.createElement('button');logout.textContent='Sign out';logout.className='button button--secondary button--sm';
    logout.onclick=async()=>{
      const result=await fetch(`${base}auth/logout`,{method:'POST',headers:{'X-CSRF-Token':user.csrf}});
      if(result.ok || result.status===401 || result.status===403) location.assign(base);
    };
    bar.append(label,link,logout);document.body.prepend(bar);
    if (!user.admin) {
      await flush();
      setInterval(()=>{manageLock();clock.step(performance.now(),eligible() && lease());},1000);
      setInterval(flush,60000);
    }
  } else if ([401,403].includes(response.status)) location.assign(`${base}learn/`);
} catch { /* The server already authorized the page; telemetry is best effort. */ }
