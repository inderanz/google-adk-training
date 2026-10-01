(async function(){
  'use strict';
  const base='/adk-training/';
  let me, nextOffset=null, reportParams=new URLSearchParams();
  const $=id=>document.getElementById(id);
  const el=(tag,text,className)=>{const node=document.createElement(tag);if(text!==undefined)node.textContent=text;if(className)node.className=className;return node;};
  const status=text=>{if($('status'))$('status').textContent=text;};
  async function api(path,method='GET',data){
    const response=await fetch(base+path,{method,cache:'no-store',headers:{...(data?{'Content-Type':'application/json'}:{}),...(method!=='GET'?{'X-CSRF-Token':me?.csrf}: {})},...(data?{body:JSON.stringify(data)}:{})});
    if(!response.ok){let message='Request failed';try{message=(await response.json()).error||message;}catch{}throw new Error(message);}
    return response.status===204?null:response.json();
  }
  function action(label,fn,className){
    const button=el('button',label,className);button.type='button';
    button.onclick=async()=>{button.disabled=true;try{await fn();}catch(error){status(error.message);}finally{button.disabled=false;}};
    return button;
  }
  function table(headers,rows){
    const wrap=el('div',undefined,'table-wrap'),t=el('table'),head=el('thead'),hr=el('tr'),body=el('tbody');
    headers.forEach(h=>hr.append(el('th',h)));head.append(hr);t.append(head);
    rows.forEach(row=>{const tr=el('tr');row.forEach(value=>{const td=el('td');if(value instanceof Node)td.append(value);else td.textContent=String(value??'');tr.append(td);});body.append(tr);});
    t.append(body);wrap.append(t);return wrap;
  }
  async function showUsers(){
    const data=await api('api/admin/users');
    const rows=data.users.map(u=>{
      const actions=el('div');
      actions.append(action(u.active?'Revoke':'Approve',async()=>{await api('api/admin/users',u.active?'DELETE':'POST',{email:u.email});status('Access updated');await showUsers();},'secondary'));
      actions.append(action('Delete activity',async()=>{if(!confirm(`Delete retained activity for ${u.email}? Access approval will not change.`))return;await api('api/admin/reports','DELETE',{email:u.email});status('Learner activity deleted');await showReports();},'danger'));
      actions.append(action('View activity',async()=>{$('report-filters').elements.email.value=u.email;setReportFilters();await showReports();}));
      return[u.email,u.active?'Approved':'Revoked',actions];
    });
    $('users').replaceChildren(table(['Email','Access','Actions'],rows));
  }
  async function showReleases(){
    const data=await api('api/admin/modules');$('releases').replaceChildren();
    for(const m of data.modules){
      const card=el('section'),title=el('h3',m.title),form=el('form');
      const lessons=el('input'),solutions=el('input');lessons.type=solutions.type='checkbox';lessons.checked=m.lessons;solutions.checked=m.solutions;solutions.disabled=!m.lessons;
      const a=el('label','Release lessons and labs','check'),b=el('label','Release solutions','check');a.prepend(lessons);b.prepend(solutions);
      lessons.onchange=()=>{solutions.disabled=!lessons.checked;if(!lessons.checked)solutions.checked=false;};
      form.append(a,b,action('Save release',async()=>{await api('api/admin/modules','PUT',{id:m.id,lessons:lessons.checked,solutions:solutions.checked});status(`Release saved: ${m.title}`);}));
      const preview=el('a','Preview content');preview.href=m.path;card.append(title,form,preview);$('releases').append(card);
    }
  }
  function setReportFilters(){
    reportParams=new URLSearchParams();for(const [key,value]of new FormData($('report-filters')))if(value)reportParams.set(key,value);
  }
  async function showReports(offset=0){
    const params=new URLSearchParams(reportParams);params.set('offset',offset);
    const data=await api(`api/admin/reports?${params}`);
    $('report-summary').textContent=`${data.summary.visits} visits · ${(data.summary.active_ms/60000).toFixed(1)} active minutes · Last activity: ${data.summary.last_at?new Date(data.summary.last_at).toLocaleString():'none'}. Date filters use UTC.`;
    const rows=data.visits.map(v=>[v.email,v.page,new Date(v.started_at).toLocaleString(),new Date(v.last_at).toLocaleString(),v.active_minutes]);
    if(offset===0)$('reports').replaceChildren();
    $('reports').append(table(['Learner','Page','Visit','Last activity','Active minutes'],rows));
    nextOffset=data.nextOffset;$('more').hidden=nextOffset===null;
  }
  try{
    me=await api('api/me');
    if($('admin-link'))$('admin-link').hidden=!me.admin;
    if($('identity'))$('identity').textContent=`Signed in as ${me.email}`;
    if($('logout')){$('logout').hidden=false;$('logout').onclick=async()=>{try{await api('auth/logout','POST');location.assign(base);}catch(error){status(error.message);}};}
    if($('catalog')){
      const data=await api('api/catalog');
      for(const m of data.modules){
        const card=el('article',undefined,'module'),title=el('h2',m.title);title.append(el('span',m.available?'Available':'Locked','badge'));card.append(title);
        const list=el('ul');
        for(const p of m.pages){const li=el('li');if(p.available){const a=el('a',p.title);a.href=p.path;li.append(a);}else li.append(el('span',`${p.title} — not released`,'locked'));list.append(li);}
        card.append(list);$('catalog').append(card);
      }
    }
    if($('approve')){
      await Promise.all([showUsers(),showReleases(),showReports()]);
      $('approve').onsubmit=async event=>{event.preventDefault();try{await api('api/admin/users','POST',{email:event.target.elements.email.value});event.target.reset();status('Learner approved');await showUsers();}catch(error){status(error.message);}};
      $('report-filters').onsubmit=async event=>{event.preventDefault();setReportFilters();try{await showReports();}catch(error){status(error.message);}};
      $('more').onclick=()=>showReports(nextOffset).catch(e=>status(e.message));
      $('export').onclick=async()=>{
        setReportFilters();const params=new URLSearchParams(reportParams);params.set('format','csv');
        try{const response=await fetch(`${base}api/admin/reports?${params}`,{cache:'no-store'});if(!response.ok)throw new Error((await response.json()).error);const url=URL.createObjectURL(await response.blob()),a=el('a');a.href=url;a.download='training-activity.csv';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);}catch(error){status(error.message);}
      };
    }
  }catch(error){status(error.message);}
  addEventListener('pageshow',event=>{if(event.persisted)location.reload();});
}());
