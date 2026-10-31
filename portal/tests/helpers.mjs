import {DatabaseSync} from 'node:sqlite';
import {readFileSync} from 'node:fs';
import {createApp} from '../src/app.mjs';
import {hash} from '../src/security.mjs';

export const BASE='/adk-training/';
export const moduleId='module01-intro';
export const lesson=`${BASE}docs/${moduleId}/`;
export const solution=`${BASE}docs/${moduleId}/lab-solution/`;
export const second=`${BASE}docs/module02-next/`;
export const site={
  modules:[{id:moduleId,title:'Module 1',path:lesson,pages:[{path:lesson,title:'Lesson',solution:false},{path:solution,title:'Solution',solution:true}]},{id:'module02-next',title:'Module 2',path:second,pages:[{path:second,title:'Second',solution:false}]}],
  pages:{[lesson]:{title:'Lesson',policy:{module:moduleId,solution:false}},[solution]:{title:'Solution',policy:{module:moduleId,solution:true}},[second]:{title:'Second',policy:{module:'module02-next',solution:false}}},
  assets:{
    [lesson]:{file:'/docs/lesson/index.html',policy:{module:moduleId,solution:false}},
    [`${lesson}index.html`]:{file:'/docs/lesson/index.html',policy:{module:moduleId,solution:false}},
    [solution]:{file:'/docs/solution/index.html',policy:{module:moduleId,solution:true}},
    [second]:{file:'/docs/second/index.html',policy:{module:'module02-next',solution:false}},
    [`${BASE}assets/lesson.js`]:{file:'/assets/lesson.js',policy:{module:moduleId,solution:false}},
    [`${BASE}assets/solution.js`]:{file:'/assets/solution.js',policy:{module:moduleId,solution:true}},
    [`${BASE}assets/main.js`]:{file:'/assets/main.js',policy:null},
    [`${BASE}assets/solution.pdf`]:{file:'/assets/solution.pdf',anyOf:[{module:moduleId,solution:true}]},
  },
};
export class D1 {
  constructor(){this.sqlite=new DatabaseSync(':memory:');for(const file of ['0001_portal.sql','0002_registration.sql'])this.sqlite.exec(readFileSync(new URL('../migrations/'+file,import.meta.url),'utf8'));}
  prepare(sql){
    const database=this.sqlite;
    return {bind(...args){
      const prepared=database.prepare(sql);
      return {
        async first(){return prepared.get(...args)||null;},
        async all(){return{results:prepared.all(...args)};},
        async run(){return{meta:prepared.run(...args)};},
      };
    }};
  }
  async batch(statements){
    this.sqlite.exec('BEGIN');
    try{const result=[];for(const s of statements)result.push(await s.run());this.sqlite.exec('COMMIT');return result;}
    catch(error){this.sqlite.exec('ROLLBACK');throw error;}
  }
}
export async function fixture(options={}){
  const db=new D1();let time=Date.parse('2026-10-01T12:00:00Z');let assetCalls=0;
  const env={DB:db,ORIGIN:'https://gyanhq.com',ADMIN_EMAIL:'owner@gmail.com',GOOGLE_CLIENT_ID:'client',GOOGLE_CLIENT_SECRET:'secret',
    ASSETS:{async fetch(request){assetCalls++;return new Response(`asset:${new URL(request.url).pathname}`,{headers:{'Cache-Control':'public,max-age=9999'}});}}};
  const app=createApp(site,{clock:()=>time,...options});
  for(const [sub,email,token]of[['learner','learner@gmail.com','learner-token'],['owner','owner@gmail.com','owner-token'],['other','other@gmail.com','other-token']]){
    db.sqlite.prepare('INSERT INTO identities VALUES(?,?,?,?)').run(sub,email,sub,time);
    db.sqlite.prepare('INSERT INTO registrations VALUES(?,?,?)').run(sub,'2026-10-30',time);
    db.sqlite.prepare('INSERT INTO sessions VALUES(?,?,?,?,?)').run(await hash(token),sub,email,`csrf-${sub}`,time+43200000);
    if(sub!=='owner')db.sqlite.prepare('INSERT INTO approvals VALUES(?,?,?,?,?)').run(email,1,sub,time,time);
  }
  return {app,env,db,advance:ms=>time+=ms,time:()=>time,assetCalls:()=>assetCalls,
    async request(path,{role='learner',method='GET',body,headers={},origin='https://gyanhq.com'}={}){
      const h={...(role?{Cookie:`gyanhq_training_session=${role}-token`}:{}),...(method!=='GET'?{Origin:origin,'X-CSRF-Token':`csrf-${role}`}:{}),...(body!==undefined?{'Content-Type':'application/json'}:{}),...headers};
      return app.fetch(new Request(origin+path,{method,headers:h,...(body!==undefined?{body:JSON.stringify(body)}:{})}),env);
    },
    release(lessons=true,solutions=false,id=moduleId){db.sqlite.prepare('INSERT OR REPLACE INTO releases VALUES(?,?,?,?)').run(id,Number(lessons),Number(solutions),time);},
  };
}
