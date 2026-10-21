// Operator-only local utility. This file is never imported by the Worker.
// Seed a real session in Wrangler's local D1, then hand its HttpOnly cookie to
// the browser over loopback. No development login route exists in the portal.
import {spawnSync} from 'node:child_process';
import {createServer} from 'node:http';
import {mkdtemp, readFile, rm, writeFile} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {BASE, cookie, emailKey, hash, randomToken, validEmail} from '../src/security.mjs';

const cwd = fileURLToPath(new URL('../', import.meta.url));
const cli = path.join(cwd, 'node_modules/wrangler/bin/wrangler.js');
const config = JSON.parse(await readFile(path.join(cwd, 'wrangler.jsonc'), 'utf8'));
const local = config.env.local;
const vars = local.vars;
if (process.argv.length !== 2) throw new Error('This command accepts no arguments; it only uses the local profile.');
if (vars.LOCAL_DEV !== 'true' || !/^http:\/\/(localhost|127\.0\.0\.1):\d+$/.test(vars.ORIGIN)) {
  throw new Error('Preview login requires LOCAL_DEV=true and an HTTP loopback ORIGIN.');
}
const email = emailKey(vars.ADMIN_EMAIL);
if (!validEmail(email)) throw new Error('Set a valid ADMIN_EMAIL in env.local.vars.');
const database = local.d1_databases.find(binding => binding.binding === 'DB')?.database_name;
if (database !== 'gyanhq-training-local') throw new Error('Preview login requires the gyanhq-training-local database.');
const origin = new URL(vars.ORIGIN);
try {
  const response = await fetch(`${origin.origin}${BASE}`, {signal: AbortSignal.timeout(3000), redirect: 'manual'});
  if (response.status !== 200) throw new Error(`Portal returned ${response.status}`);
} catch {
  throw new Error('Start the portal with npm run dev in another terminal, then run npm run preview:login again.');
}
const env = {...process.env, WRANGLER_SEND_METRICS: 'false',
  XDG_CONFIG_HOME: process.env.XDG_CONFIG_HOME || path.join(tmpdir(), 'gyanhq-wrangler')};
function wrangler(args) {
  const result = spawnSync(process.execPath, [cli, ...args, '--local', '--env', 'local'], {cwd, env, encoding: 'utf8'});
  if (result.status !== 0) throw new Error(result.error?.message || result.stderr || result.stdout);
}
const quote = value => `'${String(value).replaceAll("'", "''")}'`;
const temp = await mkdtemp(path.join(tmpdir(), 'gyanhq-preview-'));
async function execute(sql) {
  const filename = path.join(temp, 'session.sql');
  await writeFile(filename, sql, {mode: 0o600});
  wrangler(['d1', 'execute', database, '--file', filename]);
}
const token = randomToken(), tokenHash = await hash(token), time = Date.now();
try {
  wrangler(['d1', 'migrations', 'apply', database]);
  await execute(`
    INSERT INTO identities(sub,email,name,created_at)
      VALUES('local-preview-admin',${quote(email)},'Local preview administrator',${time})
      ON CONFLICT(sub) DO UPDATE SET email=excluded.email,name=excluded.name;
    INSERT INTO sessions(token_hash,sub,email,csrf,expires_at)
      VALUES(${quote(tokenHash)},'local-preview-admin',${quote(email)},${quote(randomToken())},${time + 43200000});
  `);
  // Confirm that the running Worker uses this database and administrator email.
  const response = await fetch(`${origin.origin}${BASE}api/me`, {
    headers: {Cookie: `gyanhq_training_session=${token}`}, signal: AbortSignal.timeout(5000),
  });
  const user = response.ok ? await response.json() : null;
  if (!user?.admin || user.email !== email) {
    await execute(`DELETE FROM sessions WHERE token_hash=${quote(tokenHash)};`);
    throw new Error('Local Worker configuration differs. Restart npm run dev with the local profile and check ADMIN_EMAIL overrides.');
  }
} finally {
  await rm(temp, {recursive: true, force: true});
}

const ticketPath = `/preview/${randomToken()}`;
let helperOrigin, used = false, timeout;
const escape = value => value.replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('"', '&quot;');
const server = createServer((request, response) => {
  const headers = {
    'Cache-Control': 'no-store', 'Referrer-Policy': 'same-origin',
    'X-Content-Type-Options': 'nosniff', 'X-Frame-Options': 'DENY',
    'Content-Security-Policy': `default-src 'none'; style-src 'unsafe-inline'; form-action 'self' ${origin.origin}; frame-ancestors 'none'; base-uri 'none'`,
  };
  if (used || request.headers.host !== new URL(helperOrigin).host || request.url !== ticketPath) {
    response.writeHead(404, headers).end('Not found'); return;
  }
  if (request.method === 'POST') {
    if (request.headers.origin !== helperOrigin) {
      response.writeHead(403, headers).end('Invalid origin'); return;
    }
    used = true;
    response.writeHead(303, {...headers,
      'Set-Cookie': cookie('gyanhq_training_session', token, 43200, vars),
      Location: `${origin.origin}${BASE}learn/`,
    }).end();
    clearTimeout(timeout);
    server.close();
    console.log('Signed in locally. All modules and solutions are available for 12 hours.');
    return;
  }
  if (request.method !== 'GET') {
    response.writeHead(405, {...headers, Allow: 'GET, POST'}).end(); return;
  }
  // GET only displays a confirmation so link previews cannot consume the login.
  response.writeHead(200, {...headers, 'Content-Type': 'text/html; charset=utf-8'}).end(`<!doctype html>
    <html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
    <title>Local preview · GyanHQ</title><style>
    *{box-sizing:border-box}body{margin:0;padding:24px;min-height:100vh;display:grid;place-items:center;background:#f8fafd;color:#202124;font:16px/1.6 system-ui,sans-serif}
    main{width:100%;max-width:480px;padding:32px;background:#fff;border:1px solid #dadce0;border-radius:20px}
    h1{font-size:28px;line-height:1.25}p{overflow-wrap:anywhere}small{color:#5f6368}
    button{border:0;border-radius:24px;background:#1a73e8;color:#fff;padding:14px 22px;font:inherit;cursor:pointer}
    button:focus-visible{outline:3px solid #202124;outline-offset:3px}
    </style></head><body><main><small>GyanHQ · Local preview</small><h1>Your training workspace</h1>
    <p>Continue as <strong>${escape(email)}</strong> to inspect every lesson, lab, playbook, and solution.</p>
    <form method="post" action="${ticketPath}"><button type="submit">Open local workspace</button></form>
    <p><small>This local administrator session lasts 12 hours. Use Sign out in the portal when finished.</small></p>
    </main></body></html>`);
});
await new Promise((resolve, reject) => {
  server.once('error', reject);
  server.listen(0, '127.0.0.1', resolve);
});
helperOrigin = `http://${origin.hostname}:${server.address().port}`;
timeout = setTimeout(() => { console.log('Preview link expired. Run npm run preview:login again.'); server.close(); }, 30 * 60000);
console.log(`\nLocal administrator: ${email}\nOpen this link, then click Open local workspace:\n${helperOrigin}${ticketPath}\n\nThe link expires in 30 minutes. Keep this terminal open until you sign in.\n`);
