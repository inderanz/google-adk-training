import {BASE, HttpError, fail, emailKey, validEmail, randomToken, hash, cookies, cookie, secure, json, redirect, body, csrf, allow, allowAsset, csv, verifyGoogleToken} from './security.mjs';
import {landing, catalogue, adminPage, errorPage} from './views.mjs';

const SESSION = 'gyanhq_training_session';
const OAUTH = 'gyanhq_training_oauth';
const HOUR = 3600000;
const DAY = 24 * HOUR;
const stmt = (env, sql, ...args) => env.DB.prepare(sql).bind(...args);
const rows = async statement => (await statement.all()).results;
const audit = (env, actor, action, target, time) => stmt(env, 'INSERT INTO audit(actor,action,target,created_at) VALUES(?,?,?,?)', actor, action, target, time);

export function createApp(site, dependencies = {}) {
  const clock = dependencies.clock || Date.now;
  const fetcher = dependencies.fetcher || fetch;
  const verify = dependencies.verify || verifyGoogleToken;
  const policies = new Map(Object.entries(site.pages).map(([p,v]) => [p, v.policy]));
  async function identity(request, env) {
    const token = cookies(request)[SESSION];
    if (!token) fail(401, 'Sign in with your approved Google account');
    const session = await stmt(env, `SELECT s.*, i.name FROM sessions s JOIN identities i ON i.sub=s.sub WHERE token_hash=? AND expires_at>?`, await hash(token), clock()).first();
    if (!session) fail(401, 'Your session has expired. Please sign in again');
    const admin = emailKey(session.email) === emailKey(env.ADMIN_EMAIL);
    if (!admin) {
      const approval = await stmt(env, 'SELECT active,google_sub FROM approvals WHERE email=?', session.email).first();
      if (!approval?.active || approval.google_sub !== session.sub) fail(403, 'Access has not been approved');
    }
    return {...session, admin};
  }
  async function releases(env) { return new Map((await rows(stmt(env, 'SELECT * FROM releases'))).map(r => [r.module_id, r])); }
  function publicIdentity(user) { return {email:user.email, name:user.name, admin:user.admin, csrf:user.csrf}; }
  function permittedReturn(value) {
    return value === `${BASE}admin/` || value === `${BASE}learn/` || policies.has(value) ? value : `${BASE}learn/`;
  }
  function authConfiguration(env) {
    if (!env.GOOGLE_CLIENT_ID || !env.GOOGLE_CLIENT_SECRET) fail(503, 'Google sign-in has not been configured');
  }
  async function login(request, env, url) {
    authConfiguration(env);
    const state = randomToken(), verifier = randomToken(), nonce = randomToken();
    const expiry = clock() + 10 * 60000;
    await stmt(env, 'INSERT INTO oauth_attempts VALUES(?,?,?,?,?)', await hash(state), verifier, nonce, permittedReturn(url.searchParams.get('returnTo')), expiry).run();
    const google = new URL('https://accounts.google.com/o/oauth2/v2/auth');
    google.search = new URLSearchParams({client_id:env.GOOGLE_CLIENT_ID, redirect_uri:`${env.ORIGIN}${BASE}auth/callback`, response_type:'code', scope:'openid email profile', state, nonce, code_challenge:await hash(verifier), code_challenge_method:'S256', prompt:'select_account'}).toString();
    return redirect(google.href, 302, {'Set-Cookie':cookie(OAUTH,state,600,env)});
  }
  async function callback(request, env, url) {
    authConfiguration(env);
    const state = url.searchParams.get('state');
    if (!state || state !== cookies(request)[OAUTH]) fail(401, 'Sign-in request expired or invalid');
    const attempt = await stmt(env, 'DELETE FROM oauth_attempts WHERE state_hash=? AND expires_at>? RETURNING *', await hash(state), clock()).first();
    if (!attempt || !url.searchParams.get('code')) fail(401, 'Sign-in cancelled or expired. Try again');
    const response = await fetcher('https://oauth2.googleapis.com/token', {method:'POST', headers:{'Content-Type':'application/x-www-form-urlencoded'}, body:new URLSearchParams({code:url.searchParams.get('code'), client_id:env.GOOGLE_CLIENT_ID, client_secret:env.GOOGLE_CLIENT_SECRET, redirect_uri:`${env.ORIGIN}${BASE}auth/callback`, grant_type:'authorization_code', code_verifier:attempt.verifier})});
    if (!response.ok) fail(401, 'Google sign-in could not be completed');
    const tokens = await response.json();
    const claims = await verify(tokens.id_token, {clientId:env.GOOGLE_CLIENT_ID, nonce:attempt.nonce, fetcher, clock});
    const email = emailKey(claims.email), time = clock();
    const admin = email === emailKey(env.ADMIN_EMAIL);
    if (!admin) {
      // Bind an email approval to exactly one Google account. Revocation during
      // OAuth is also checked before creating the session and on every request.
      await stmt(env, 'UPDATE approvals SET google_sub=?,updated_at=? WHERE email=? AND active=1 AND (google_sub IS NULL OR google_sub=?)', claims.sub,time,email,claims.sub).run();
      const approval = await stmt(env, 'SELECT * FROM approvals WHERE email=?',email).first();
      if (!approval?.active || approval.google_sub !== claims.sub) fail(403, 'Access has not been approved');
    }
    const token = randomToken(), csrfToken = randomToken();
    await env.DB.batch([
      stmt(env, `INSERT INTO identities VALUES(?,?,?,?) ON CONFLICT(sub) DO UPDATE SET email=excluded.email,name=excluded.name`,claims.sub,email,String(claims.name || '').slice(0,200),time),
      stmt(env, 'INSERT INTO sessions VALUES(?,?,?,?,?)',await hash(token),claims.sub,email,csrfToken,time+12*HOUR),
      ...(admin ? [audit(env,claims.sub,'admin.login',email,time)] : []),
    ]);
    const result = redirect(attempt.return_to);
    result.headers.append('Set-Cookie',cookie(SESSION,token,12*3600,env));
    result.headers.append('Set-Cookie',cookie(OAUTH,'',0,env));
    return result;
  }
  async function activity(request, env, user) {
    if (user.admin) return json({ignored:true});
    const data = await body(request);
    const {id, page, sequence, activeMs} = data;
    if (typeof id !== 'string' || !/^[a-zA-Z0-9-]{16,80}$/.test(id) || !policies.has(page)
      || !Number.isSafeInteger(sequence) || sequence < 0 || !Number.isSafeInteger(activeMs) || activeMs < 0 || activeMs > 12*HOUR) fail(400,'Invalid activity update');
    if (!allow(policies.get(page),user,await releases(env))) fail(403,'This page is not released');
    const time = clock();
    // One row per visit. Cumulative totals + monotonic sequence make retries
    // idempotent. Each update is bounded by elapsed server time and two minutes.
    const changed = await stmt(env, `INSERT INTO visits(id,sub,page,started_at,last_at,active_ms,sequence)
      VALUES(?,?,?,?,?,0,?) ON CONFLICT(id) DO UPDATE SET
      active_ms=visits.active_ms+MAX(0,MIN(excluded.last_at-visits.last_at,120000,?-visits.active_ms)),
      last_at=excluded.last_at,sequence=excluded.sequence
      WHERE visits.sub=excluded.sub AND visits.page=excluded.page AND excluded.sequence>visits.sequence
      RETURNING id`,id,user.sub,page,time,time,sequence,activeMs).first();
    return json({accepted:!!changed});
  }
  async function reports(url, env) {
    const limit = 100;
    const offset = Number(url.searchParams.get('offset') || 0);
    if (!Number.isSafeInteger(offset) || offset < 0 || offset > 100000) fail(400,'Invalid report offset');
    const date = (name,fallback,end=false) => {
      const value = url.searchParams.get(name);
      if (!value) return fallback;
      if (!/^\d{4}-\d{2}-\d{2}$/.test(value)) fail(400,'Use YYYY-MM-DD dates');
      const parsed = Date.parse(`${value}T00:00:00Z`);
      if (!Number.isFinite(parsed) || new Date(parsed).toISOString().slice(0,10) !== value) fail(400,'Invalid date');
      return parsed + (end ? DAY : 0);
    };
    const from = Math.max(clock()-90*DAY,date('from',clock()-90*DAY));
    const to = date('to',clock()+1,true);
    if (to < from) fail(400,'End date must follow start date');
    let where = 'v.started_at>=? AND v.started_at<?';
    const args = [from,to];
    const email = url.searchParams.get('email');
    const page = url.searchParams.get('page');
    if (email) { where += ' AND i.email=?'; args.push(emailKey(email)); }
    if (page) { where += ' AND v.page=?'; args.push(page); }
    const summary = await stmt(env,`SELECT COUNT(*) AS visits,COALESCE(SUM(v.active_ms),0) AS active_ms,MAX(v.last_at) AS last_at FROM visits v JOIN identities i ON i.sub=v.sub WHERE ${where}`,...args).first();
    const exportCSV = url.searchParams.get('format') === 'csv';
    const pageLimit = exportCSV ? 10000 : limit;
    const records = await rows(stmt(env,`SELECT v.id,i.email,v.page,v.started_at,v.last_at,v.active_ms FROM visits v JOIN identities i ON i.sub=v.sub WHERE ${where} ORDER BY v.started_at DESC,v.id LIMIT ? OFFSET ?`,...args,pageLimit,offset));
    const visits = records.map(v => ({...v, started_at:new Date(v.started_at).toISOString(),last_at:new Date(v.last_at).toISOString(),active_minutes:Math.round(v.active_ms/600)/100}));
    if (exportCSV) {
      if (summary.visits > 10000) fail(400,'Export is limited to 10,000 visits. Narrow the dates or learner filter');
      return new Response(csv(visits,['email','page','started_at','last_at','active_minutes']),{headers:{'Content-Type':'text/csv; charset=utf-8','Content-Disposition':'attachment; filename="training-activity.csv"'}});
    }
    return json({summary,visits,nextOffset:offset+visits.length < summary.visits ? offset+visits.length : null});
  }
  async function administrator(request, env, url, user) {
    if (!user.admin) fail(403,'Administrator access required');
    const time=clock(), path=url.pathname;
    if (path === `${BASE}api/admin/users`) {
      if (request.method === 'GET') return json({users:await rows(stmt(env,'SELECT email,active,created_at,updated_at FROM approvals ORDER BY email'))});
      if (!['POST','DELETE'].includes(request.method)) fail(405,'Method not allowed');
      const data=await body(request), email=emailKey(data.email);
      if (!validEmail(email) || email===emailKey(env.ADMIN_EMAIL)) fail(400,'Enter a learner email, not the administrator');
      const statements = request.method === 'POST' ? [
        stmt(env,`INSERT INTO approvals(email,active,created_at,updated_at) VALUES(?,1,?,?) ON CONFLICT(email) DO UPDATE SET active=1,updated_at=excluded.updated_at`,email,time,time),
      ] : [stmt(env,'UPDATE approvals SET active=0,updated_at=? WHERE email=?',time,email),stmt(env,'DELETE FROM sessions WHERE email=?',email)];
      await env.DB.batch([...statements,audit(env,user.sub,request.method==='POST'?'learner.approve':'learner.revoke',email,time)]);
      return json({ok:true});
    }
    if (path === `${BASE}api/admin/modules`) {
      if (request.method === 'GET') {
        const released=await releases(env);
        return json({modules:site.modules.map(m => ({...m,lessons:!!released.get(m.id)?.lessons,solutions:!!released.get(m.id)?.solutions}))});
      }
      if (request.method !== 'PUT') fail(405,'Method not allowed');
      const data=await body(request);
      if (!site.modules.some(m=>m.id===data.id) || typeof data.lessons!=='boolean' || typeof data.solutions!=='boolean') fail(400,'Invalid module release');
      const solutions=data.lessons && data.solutions;
      await env.DB.batch([
        stmt(env,`INSERT INTO releases VALUES(?,?,?,?) ON CONFLICT(module_id) DO UPDATE SET lessons=excluded.lessons,solutions=excluded.solutions,updated_at=excluded.updated_at`,data.id,Number(data.lessons),Number(solutions),time),
        audit(env,user.sub,'module.release',JSON.stringify({id:data.id,lessons:data.lessons,solutions}),time),
      ]);
      return json({ok:true});
    }
    if (path === `${BASE}api/admin/reports`) {
      if (request.method === 'GET') return reports(url,env);
      if (request.method !== 'DELETE') fail(405,'Method not allowed');
      const data=await body(request), email=emailKey(data.email);
      if (!validEmail(email)) fail(400,'Learner email required');
      await env.DB.batch([
        stmt(env,'DELETE FROM visits WHERE sub IN (SELECT sub FROM identities WHERE email=?)',email),
        audit(env,user.sub,'activity.delete',email,time),
      ]);
      return json({ok:true});
    }
    fail(404,'Page not found');
  }
  async function handle(request,env) {
    const url=new URL(request.url), path=url.pathname;
    if (!env.ORIGIN || url.origin!==env.ORIGIN) fail(404,'Page not found');
    if (path===BASE.slice(0,-1)) return redirect(BASE,308);
    if (!path.startsWith(BASE) || /%2f|%5c|%00|\\/i.test(path)) fail(404,'Page not found');
    const method=request.method;
    const publicFiles=new Set(['portal.css','ui.js','tracker.js','tracking-core.js']);
    const publicName=path.slice(`${BASE}portal/`.length);
    if (path.startsWith(`${BASE}portal/`) && publicFiles.has(publicName)) {
      if (!['GET','HEAD'].includes(method)) fail(405,'Method not allowed');
      const target=new URL(request.url); target.pathname=`/portal/${publicName}`;
      return env.ASSETS.fetch(new Request(target,{method}));
    }
    if (path===BASE && ['GET','HEAD'].includes(method)) return landing();
    if (!env.DB || !validEmail(env.ADMIN_EMAIL)) fail(503,'Training portal setup is incomplete');
    if (path===`${BASE}auth/login` && method==='GET') return login(request,env,url);
    if (path===`${BASE}auth/callback` && method==='GET') return callback(request,env,url);
    const user=await identity(request,env);
    if (!['GET','HEAD'].includes(method)) csrf(request,user,env.ORIGIN);
    if (path===`${BASE}auth/logout`) {
      if (method!=='POST') fail(405,'Method not allowed');
      await stmt(env,'DELETE FROM sessions WHERE token_hash=?',user.token_hash).run();
      return new Response(null,{status:204,headers:{'Set-Cookie':cookie(SESSION,'',0,env)}});
    }
    if (path===`${BASE}api/me` && method==='GET') return json(publicIdentity(user));
    if (path===`${BASE}api/catalog` && method==='GET') {
      const released=await releases(env);
      return json({modules:site.modules.map(m=>({...m,available:allow({module:m.id},user,released),pages:m.pages.map(p=>({...p,available:allow({module:m.id,solution:p.solution},user,released)}))}))});
    }
    if (path===`${BASE}api/activity` && method==='POST') return activity(request,env,user);
    if (path.startsWith(`${BASE}api/admin/`)) return administrator(request,env,url,user);
    if (!['GET','HEAD'].includes(method)) fail(405,'Method not allowed');
    if (path===`${BASE}learn/`) return catalogue();
    if (path===`${BASE}admin/`) {
      if (!user.admin) fail(403,'Administrator access required');
      await audit(env,user.sub,'admin.view','dashboard',clock()).run();
      return adminPage();
    }
    // Redirect only known canonical pages, never arbitrary paths.
    if (policies.has(`${path}/`)) return redirect(`${path}/${url.search}`,308);
    const legacy = `${BASE}docs/${path.slice(BASE.length)}`;
    const legacyTarget = legacy.endsWith('/') ? legacy : `${legacy}/`;
    if (!path.startsWith(`${BASE}docs/`) && policies.has(legacyTarget)) return redirect(legacyTarget+url.search,308);
    const asset=site.assets[path];
    if (!asset) fail(404,'Page not found');
    if (!allowAsset(asset,user,await releases(env))) fail(403,'Your instructor has not released this content yet');
    const target=new URL(request.url); target.pathname=asset.file; target.search='';
    // Forward no conditional/range headers: never let a cached 304 bypass checks.
    return env.ASSETS.fetch(new Request(target,{method}));
  }
  return {
    async fetch(request,env) {
      try {
        const response=secure(await handle(request,env));
        return request.method==='HEAD' ? new Response(null,{status:response.status,headers:response.headers}) : response;
      } catch(error) {
        const status=error instanceof HttpError ? error.status : 503;
        const message=error instanceof HttpError ? error.message : 'Training is temporarily unavailable. Please try again later';
        // Do not log tokens, email addresses, OAuth codes, or SQL parameter values.
        if (!(error instanceof HttpError)) console.error('portal_request_failed',error?.name || 'Error');
        const response=new URL(request.url).pathname.includes('/api/') ? json({error:message},status) : errorPage(status,message);
        return secure(response);
      }
    },
    async scheduled(event,env) {
      const time=clock();
      // Bounded cleanup keeps a delayed cron from generating an unbounded write.
      await env.DB.batch([
        stmt(env,'DELETE FROM visits WHERE id IN (SELECT id FROM visits WHERE started_at<? LIMIT 5000)',time-90*DAY),
        stmt(env,'DELETE FROM sessions WHERE token_hash IN (SELECT token_hash FROM sessions WHERE expires_at<? LIMIT 5000)',time),
        stmt(env,'DELETE FROM oauth_attempts WHERE state_hash IN (SELECT state_hash FROM oauth_attempts WHERE expires_at<? LIMIT 5000)',time),
        stmt(env,'DELETE FROM audit WHERE id IN (SELECT id FROM audit WHERE created_at<? LIMIT 5000)',time-90*DAY),
      ]);
    },
  };
}
