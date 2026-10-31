import test from 'node:test';
import assert from 'node:assert/strict';
import {fixture,BASE} from './helpers.mjs';
import {base64url,verifyGoogleToken,hash} from '../src/security.mjs';

test('Google login uses state, nonce, PKCE and a safe return URL',async()=>{
  const f=await fixture();const response=await f.request(`${BASE}auth/login?returnTo=https://attacker.test`,{role:null});
  const location=new URL(response.headers.get('Location'));
  assert.equal(location.origin,'https://accounts.google.com');assert.equal(location.searchParams.get('code_challenge_method'),'S256');
  assert.equal(location.searchParams.get('scope'),'openid email profile');
  const attempt=f.db.sqlite.prepare('SELECT * FROM oauth_attempts').get();
  assert.equal(attempt.return_to,`${BASE}learn/`);assert.equal(await hash(attempt.verifier),location.searchParams.get('code_challenge'));
  assert.match(response.headers.get('Set-Cookie'),/HttpOnly; SameSite=Lax/);assert.match(response.headers.get('Set-Cookie'),/Secure/);
});
test('callback rejects absent, mismatched, expired and replayed state',async()=>{
  const f=await fixture();assert.equal((await f.request(`${BASE}auth/callback?state=bad&code=x`,{role:null})).status,401);
  const login=await f.request(`${BASE}auth/login`,{role:null});const state=new URL(login.headers.get('Location')).searchParams.get('state');
  f.advance(600001);
  assert.equal((await f.request(`${BASE}auth/callback?state=${state}&code=x`,{role:null,headers:{Cookie:`gyanhq_training_oauth=${state}`}})).status,401);
});
test('returning registered learner gets a hashed session without changing their chosen name',async()=>{
  const f=await fixture({fetcher:async()=>Response.json({id_token:'token'}),verify:async()=>({sub:'learner',email:'learner@gmail.com',name:'Google name'})});
  const start=await f.request(`${BASE}auth/login`,{role:null});const state=new URL(start.headers.get('Location')).searchParams.get('state');
  const path=`${BASE}auth/callback?state=${state}&code=x`,opts={role:null,headers:{Cookie:`gyanhq_training_oauth=${state}`}};
  const response=await f.request(path,opts);assert.equal(response.status,303);
  const cookie=response.headers.get('Set-Cookie').match(/gyanhq_training_session=([^;]+)/)[1];
  assert.equal(f.db.sqlite.prepare('SELECT sub FROM sessions WHERE token_hash=?').get(await hash(cookie)).sub,'learner');
  assert.equal(f.db.sqlite.prepare('SELECT name FROM identities WHERE sub=?').get('learner').name,'learner');
  assert.equal((await f.request(path,opts)).status,401);
});
test('revoked and differently bound Google accounts cannot obtain sessions',async()=>{
  for(const claims of [{sub:'learner',email:'learner@gmail.com'},{sub:'imposter',email:'learner@gmail.com'}]){
    const f=await fixture({fetcher:async()=>Response.json({id_token:'token'}),verify:async()=>claims});
    if(claims.sub==='learner')f.db.sqlite.prepare('UPDATE approvals SET active=0').run();
    const start=await f.request(`${BASE}auth/login`,{role:null});const state=new URL(start.headers.get('Location')).searchParams.get('state');
    const response=await f.request(`${BASE}auth/callback?state=${state}&code=x`,{role:null,headers:{Cookie:`gyanhq_training_oauth=${state}`}});
    assert.equal(response.status,403);assert.equal(f.db.sqlite.prepare('SELECT COUNT(*) n FROM sessions').get().n,3);
  }
});
test('Google token verification checks signature and identity claims',async()=>{
  const pair=await crypto.subtle.generateKey({name:'RSASSA-PKCS1-v1_5',modulusLength:2048,publicExponent:new Uint8Array([1,0,1]),hash:'SHA-256'},true,['sign','verify']);
  const jwk=await crypto.subtle.exportKey('jwk',pair.publicKey);jwk.kid='test-key';
  const clock=()=>1800000000000;
  const original={iss:'https://accounts.google.com',aud:'client',sub:'123',email:'a@gmail.com',email_verified:true,nonce:'nonce',iat:1800000000,exp:1800000600};
  const token=async claims=>{
    const text=[{alg:'RS256',kid:'test-key'},claims].map(o=>base64url(new TextEncoder().encode(JSON.stringify(o)))).join('.');
    return text+'.'+base64url(await crypto.subtle.sign('RSASSA-PKCS1-v1_5',pair.privateKey,new TextEncoder().encode(text)));
  };
  const options={clientId:'client',nonce:'nonce',clock,fetcher:async()=>Response.json({keys:[jwk]})};
  assert.equal((await verifyGoogleToken(await token(original),options)).sub,'123');
  for(const change of [{iss:'attacker'},{aud:'other'},{azp:'other'},{email_verified:false},{nonce:'wrong'},{exp:1799999999},{sub:''},{iat:1900000000}])await assert.rejects(()=>token({...original,...change}).then(t=>verifyGoogleToken(t,options)),{status:401});
  const good=await token(original);await assert.rejects(()=>verifyGoogleToken(good.slice(0,-20)+'AAAAAAAAAAAAAAAAAAAA',options),{status:401});
});
