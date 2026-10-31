import test from 'node:test';
import assert from 'node:assert/strict';
import {fixture,BASE,solution} from './helpers.mjs';
import {verifyAccessToken,base64url} from '../src/security.mjs';

async function accessFixture(claims={sub:'email-user',email:'new@gmail.com'}) {
  const f=await fixture({verifyAccess:async()=>claims});
  Object.assign(f.env,{AUTH_PROVIDER:'cloudflare-access',ACCESS_TEAM_DOMAIN:'https://anzinder.cloudflareaccess.com',ACCESS_AUD:'aud'});
  const response=await f.request(BASE+'auth/login?returnTo=https://evil.test',{role:null});
  const path=response.headers.get('Location');
  const cookie=response.headers.get('Set-Cookie').split(';')[0];
  return {f,path,cookie};
}
test('Access email login requires state and creates registration only after verification',async()=>{
  const {f,path,cookie}=await accessFixture();
  assert.equal((await f.request(path,{role:null})).status,401);
  const opts={role:null,headers:{Cookie:cookie,'Cf-Access-Jwt-Assertion':'signed'}};
  const response=await f.request(path,opts);assert.equal(response.status,303);assert.equal(response.headers.get('Location'),BASE+'register/');
  const pending=f.db.sqlite.prepare('SELECT * FROM pending_registrations').get();
  assert.equal(pending.email,'new@gmail.com');assert.equal(pending.sub,'access:email-user');assert.equal(pending.return_to,BASE+'learn/');
  const registrationCookie=response.headers.get('Set-Cookie').split(';')[0];
  const registered=await f.request(BASE+'register/',{role:null,method:'POST',headers:{Cookie:registrationCookie,'X-CSRF-Token':pending.csrf},body:{name:'Email Learner',agree:true,version:'2026-10-30'}});
  assert.equal(registered.status,200);
  const session=registered.headers.get('Set-Cookie').split(';')[0];
  assert.equal((await f.request(solution,{role:null,headers:{Cookie:session}})).status,200);
  assert.equal((await f.request(path,opts)).status,401);
  assert.equal((await f.request(BASE+'auth/callback',{role:null})).status,401);
});
test('Access admin login and logout; revoked email cannot register again',async()=>{
  const {f,path,cookie}=await accessFixture({sub:'admin',email:'owner@gmail.com'});
  const response=await f.request(path,{role:null,headers:{Cookie:cookie,'Cf-Access-Jwt-Assertion':'signed'}});assert.equal(response.status,303);
  assert.match(response.headers.get('Set-Cookie'),/gyanhq_training_session=/);
  const logout=await f.request(BASE+'auth/logout',{role:'owner',method:'POST'});assert.equal((await logout.json()).redirect,'/cdn-cgi/access/logout');
  const other=await accessFixture({sub:'new-id',email:'learner@gmail.com'});
  other.f.db.sqlite.prepare('UPDATE approvals SET active=0').run();
  assert.equal((await other.f.request(other.path,{role:null,headers:{Cookie:other.cookie,'Cf-Access-Jwt-Assertion':'signed'}})).status,403);
});
test('Access JWT requires valid signature, issuer, audience, lifetime, app type and email',async()=>{
  const pair=await crypto.subtle.generateKey({name:'RSASSA-PKCS1-v1_5',modulusLength:2048,publicExponent:new Uint8Array([1,0,1]),hash:'SHA-256'},true,['sign','verify']);
  const jwk=await crypto.subtle.exportKey('jwk',pair.publicKey);jwk.kid='access-test';
  const claims={iss:'https://test.cloudflareaccess.com',aud:['test-aud'],sub:'test-user',email:'test@gmail.com',type:'app',iat:1800000000,exp:1800000600};
  const sign=async value=>{const text=[{alg:'RS256',kid:jwk.kid},value].map(v=>base64url(new TextEncoder().encode(JSON.stringify(v)))).join('.');return text+'.'+base64url(await crypto.subtle.sign('RSASSA-PKCS1-v1_5',pair.privateKey,new TextEncoder().encode(text)));};
  const options={teamDomain:claims.iss,audience:'test-aud',clock:()=>1800000000000,fetcher:async url=>{assert.equal(url,claims.iss+'/cdn-cgi/access/certs');return Response.json({keys:[jwk]});}};
  assert.equal((await verifyAccessToken(await sign(claims),options)).email,claims.email);
  for(const change of [{iss:'https://evil.test'},{aud:['other']},{exp:1},{iat:1900000000},{nbf:1900000000},{email:''},{sub:''},{type:'service-token'}])await assert.rejects(()=>sign({...claims,...change}).then(t=>verifyAccessToken(t,options)),{status:401});
  await assert.rejects(()=>verifyAccessToken(null,options),{status:401});
  const token=await sign(claims);await assert.rejects(()=>verifyAccessToken(token.slice(0,-20)+'AAAAAAAAAAAAAAAAAAAA',options),{status:401});
});
