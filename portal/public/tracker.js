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
    bar.className='portal-account-bar';bar.setAttribute('aria-label','Your training account');
    const label=document.createElement('span'); label.textContent=user.email;
    const link=document.createElement('a'); link.href=`${base}learn/`;link.textContent='Course catalogue';
    const logout=document.createElement('button');logout.textContent='Sign out';logout.className='button button--secondary button--sm';
    logout.onclick=async()=>{
      const result=await fetch(`${base}auth/logout`,{method:'POST',headers:{'X-CSRF-Token':user.csrf}});
      if(result.ok || result.status===401 || result.status===403) location.assign(base);
    };
    bar.append(label,link,logout);document.body.prepend(bar);
    initModuleCompletion(user.email);
    initCodeCopyButtons();
    if (!user.admin) {
      await flush();
      setInterval(()=>{manageLock();clock.step(performance.now(),eligible() && lease());},1000);
      setInterval(flush,60000);
    }
  } else if ([401,403].includes(response.status)) location.assign(`${base}learn/`);
} catch { /* The server already authorized the page; telemetry is best effort. */ }

// --- Interactive Code Block Copy Buttons ---
function initCodeCopyButtons() {
  document.querySelectorAll('pre').forEach(pre => {
    if (pre.dataset.hasCopyBtn) return;
    pre.dataset.hasCopyBtn = 'true';
    
    // Create wrapper if not already wrapped
    let wrapper = pre.parentElement;
    if (!wrapper || !wrapper.classList.contains('code-block-wrapper')) {
      wrapper = document.createElement('div');
      wrapper.className = 'code-block-wrapper';
      pre.parentNode.insertBefore(wrapper, pre);
      wrapper.appendChild(pre);
    }
    
    const btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'copy-code-button';
    btn.innerHTML = '<span aria-hidden="true">📋</span> Copy';
    btn.setAttribute('aria-label', 'Copy code to clipboard');
    
    btn.onclick = async (e) => {
      e.stopPropagation();
      const code = pre.querySelector('code')?.innerText || pre.innerText;
      try {
        await navigator.clipboard.writeText(code);
        btn.innerHTML = '<span aria-hidden="true">✓</span> Copied!';
        btn.classList.add('copied');
        setTimeout(() => {
          btn.innerHTML = '<span aria-hidden="true">📋</span> Copy';
          btn.classList.remove('copied');
        }, 2000);
      } catch (err) {
        btn.textContent = 'Failed';
      }
    };
    wrapper.appendChild(btn);
  });
}

// --- Interactive 'Mark as Completed' Progress Tracker ---
function initModuleCompletion(userEmail) {
  const currentPath = location.pathname;
  const match = currentPath.match(//docs/([^/]+)/);
  if (!match) return;
  const moduleId = match[1];
  
  const storageKey = 'gyanhq_completed_modules_' + (userEmail || 'anonymous');
  let completed = [];
  try {
    completed = JSON.parse(localStorage.getItem(storageKey) || '[]');
  } catch {}
  
  const isDone = completed.includes(moduleId);
  
  const bar = document.querySelector('.portal-account-bar');
  if (!bar || bar.querySelector('.module-completion-widget')) return;
  
  const widget = document.createElement('div');
  widget.className = 'module-completion-widget';
  
  const btn = document.createElement('button');
  btn.type = 'button';
  btn.className = 'completion-toggle-btn' + (isDone ? ' completed' : '');
  btn.innerHTML = isDone ? '<span>✓ Completed</span>' : '<span>Mark as Completed</span>';
  
  btn.onclick = () => {
    try {
      let list = JSON.parse(localStorage.getItem(storageKey) || '[]');
      if (list.includes(moduleId)) {
        list = list.filter(id => id !== moduleId);
        btn.classList.remove('completed');
        btn.innerHTML = '<span>Mark as Completed</span>';
      } else {
        list.push(moduleId);
        btn.classList.add('completed');
        btn.innerHTML = '<span>✓ Completed</span>';
      }
      localStorage.setItem(storageKey, JSON.stringify(list));
    } catch {}
  };
  
  widget.appendChild(btn);
  // Insert before sign out button
  const logoutBtn = bar.querySelector('button');
  if (logoutBtn) bar.insertBefore(widget, logoutBtn);
  else bar.appendChild(widget);
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    initCodeCopyButtons();
  });
} else {
  initCodeCopyButtons();
}
