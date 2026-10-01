export const BASE = '/adk-training/';
export class HttpError extends Error {
  constructor(status, message) { super(message); this.status = status; }
}
export const fail = (status, message) => { throw new HttpError(status, message); };
export const now = () => Date.now();
export const emailKey = value => String(value || '').trim().toLowerCase();
export function validEmail(value) {
  return typeof value === 'string' && value.length <= 254 && /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value);
}
export function base64url(bytes) {
  return btoa(String.fromCharCode(...new Uint8Array(bytes))).replaceAll('+', '-').replaceAll('/', '_').replace(/=+$/, '');
}
export function randomToken() { return base64url(crypto.getRandomValues(new Uint8Array(32))); }
export async function hash(value) {
  return base64url(await crypto.subtle.digest('SHA-256', new TextEncoder().encode(value)));
}
export function cookies(request) {
  return Object.fromEntries((request.headers.get('Cookie') || '').split(';').map(s => s.trim().split(/=(.*)/s).slice(0,2)).filter(p => p.length === 2));
}
export function cookie(name, value, maxAge, env) {
  const local = env.LOCAL_DEV === 'true' && /^http:\/\/(localhost|127\.0\.0\.1):\d+$/.test(env.ORIGIN);
  return `${name}=${value}; Path=${BASE}; HttpOnly; SameSite=Lax; Max-Age=${maxAge}${local ? '' : '; Secure'}`;
}
export function secure(response) {
  const headers = new Headers(response.headers);
  headers.set('Cache-Control', 'private, no-store');
  headers.set('X-Content-Type-Options', 'nosniff');
  headers.set('Referrer-Policy', 'same-origin');
  headers.set('X-Frame-Options', 'DENY');
  headers.set('X-Robots-Tag', 'noindex, nofollow, noarchive');
  headers.set('Permissions-Policy', 'camera=(), microphone=(), geolocation=()');
  headers.set('Content-Security-Policy', "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com; img-src 'self' data: https:; connect-src 'self'; frame-ancestors 'none'; base-uri 'self'; form-action 'self'; object-src 'none'");
  return new Response(response.body, {status: response.status, headers});
}
export function json(body, status = 200) {
  return new Response(JSON.stringify(body), {status, headers: {'Content-Type': 'application/json; charset=utf-8'}});
}
export function redirect(path, status = 303, headers = {}) {
  return new Response(null, {status, headers: {...headers, Location: path}});
}
export async function body(request) {
  if (!request.headers.get('Content-Type')?.startsWith('application/json')) fail(415, 'JSON body required');
  const reader = request.body?.getReader();
  if (!reader) fail(400, 'JSON body required');
  let length = 0;
  const chunks = [];
  while (true) {
    const {done, value} = await reader.read();
    if (done) break;
    length += value.length;
    if (length > 16384) { await reader.cancel(); fail(413, 'Request too large'); }
    chunks.push(value);
  }
  const bytes = new Uint8Array(length);
  let offset = 0;
  for (const c of chunks) { bytes.set(c, offset); offset += c.length; }
  try {
    const value = JSON.parse(new TextDecoder().decode(bytes));
    if (!value || Array.isArray(value) || typeof value !== 'object') fail(400, 'JSON object required');
    return value;
  } catch { fail(400, 'Invalid JSON object'); }
}
export function csrf(request, session, origin) {
  if (request.headers.get('Origin') !== origin || request.headers.get('X-CSRF-Token') !== session.csrf) fail(403, 'Invalid request origin or CSRF token');
}
export function allow(policy, identity, releases) {
  if (identity.admin) return true;
  if (!policy) return true;
  const release = releases.get(policy.module);
  return !!release?.lessons && (!policy.solution || !!release.solutions);
}
export function allowAsset(asset, identity, releases) {
  return asset.anyOf?.length ? asset.anyOf.some(p => allow(p, identity, releases)) : allow(asset.policy, identity, releases);
}
export function csv(rows, columns) {
  const escape = value => {
    let text = String(value ?? '');
    if (/^[=+@\-\t\r\n]/.test(text)) text = `'${text}`;
    return `"${text.replaceAll('"', '""')}"`;
  };
  return [columns, ...rows.map(row => columns.map(c => row[c]))].map(row => row.map(escape).join(',')).join('\r\n');
}

let keyCache = {keys: [], expires: 0};
function decode(part) {
  const normalized = part.replaceAll('-', '+').replaceAll('_', '/');
  return Uint8Array.from(atob(normalized), c => c.charCodeAt(0));
}
export async function verifyGoogleToken(token, {clientId, nonce, fetcher = fetch, clock = now}) {
  try {
    if (typeof token !== 'string' || token.length > 20000) fail(401, 'Invalid Google identity');
    const parts = token.split('.');
    if (parts.length !== 3) fail(401, 'Invalid Google identity');
    const header = JSON.parse(new TextDecoder().decode(decode(parts[0])));
    const claims = JSON.parse(new TextDecoder().decode(decode(parts[1])));
    if (header.alg !== 'RS256' || typeof header.kid !== 'string') fail(401, 'Invalid Google identity');
    if (keyCache.expires <= clock() || !keyCache.keys.some(k => k.kid === header.kid)) {
      const response = await fetcher('https://www.googleapis.com/oauth2/v3/certs');
      if (!response.ok) fail(503, 'Google sign-in temporarily unavailable');
      const data = await response.json();
      if (!Array.isArray(data.keys)) fail(503, 'Google sign-in temporarily unavailable');
      keyCache = {keys: data.keys, expires: clock() + 3600000};
    }
    const jwk = keyCache.keys.find(k => k.kid === header.kid && k.kty === 'RSA');
    if (!jwk) fail(401, 'Invalid Google identity');
    const publicKey = await crypto.subtle.importKey('jwk', jwk, {name: 'RSASSA-PKCS1-v1_5', hash: 'SHA-256'}, false, ['verify']);
    const valid = await crypto.subtle.verify('RSASSA-PKCS1-v1_5', publicKey, decode(parts[2]), new TextEncoder().encode(`${parts[0]}.${parts[1]}`));
    if (!valid || !['https://accounts.google.com', 'accounts.google.com'].includes(claims.iss)
      || claims.aud !== clientId || (claims.azp && claims.azp !== clientId)
      || !Number.isFinite(claims.exp) || claims.exp * 1000 <= clock()
      || !Number.isFinite(claims.iat) || claims.iat * 1000 > clock() + 60000
      || claims.nonce !== nonce || claims.email_verified !== true
      || !validEmail(claims.email) || typeof claims.sub !== 'string' || !claims.sub || claims.sub.length > 255) fail(401, 'Invalid Google identity');
    return claims;
  } catch (error) {
    if (error instanceof HttpError) throw error;
    fail(401, 'Invalid Google identity');
  }
}
