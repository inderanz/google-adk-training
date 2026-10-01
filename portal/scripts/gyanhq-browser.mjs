import {createServer} from 'node:http';
import {readFile,stat} from 'node:fs/promises';
import path from 'node:path';
import assert from 'node:assert/strict';
import {chromium} from 'playwright';

const root=process.argv[2];
if(!root)throw new Error('Usage: node scripts/gyanhq-browser.mjs /path/to/gyanhq');
const base=path.resolve(root),origin='http://localhost:8898';
const server=createServer(async(req,res)=>{
  let filename=path.resolve(base,'.'+decodeURIComponent(new URL(req.url,origin).pathname));
  if(!filename.startsWith(base+path.sep)&&filename!==base){res.writeHead(404);res.end();return;}
  try{
    if((await stat(filename)).isDirectory())filename=path.join(filename,'index.html');
    const contents=await readFile(filename);
    const type={'.html':'text/html','.js':'text/javascript','.css':'text/css','.svg':'image/svg+xml','.md':'text/plain','.jpg':'image/jpeg','.png':'image/png'}[path.extname(filename)]||'application/octet-stream';
    res.writeHead(200,{'Content-Type':type});res.end(contents);
  }catch{res.writeHead(404);res.end('Not found');}
});
await new Promise(resolve=>server.listen(8898,'localhost',resolve));
let browser;const passed=[];
function check(ok,label){assert.ok(ok,label);passed.push(label);}
try{
  const channel=process.env.PLAYWRIGHT_CHANNEL||'chrome';
  browser=await chromium.launch({headless:true,...(channel==='chromium'?{}:{channel})});
  const context=await browser.newContext();const page=await context.newPage();
  await page.route('**/api/**',route=>route.fulfill({json:route.request().url().includes('comments')?[]:{likes:0,dislikes:0}}));
  const errors=[];page.on('pageerror',error=>errors.push(error.message));
  for(const route of ['/','/program.html','/instructor.html','/blogs.html','/privacy.html']){
    for(const width of [390,900,1440]){
      await page.setViewportSize({width,height:900});await page.goto(origin+route);
      const nav=page.locator('.main-nav');
      if(width===390)await page.locator('.site-nav-toggle').click();
      check(await nav.getByRole('link',{name:'ADK Training',exact:true}).isVisible(),`Training link visible ${route} ${width}`);
      check(await nav.getByRole('link',{name:'ADK Training',exact:true}).getAttribute('href')==='/adk-training/',`Training target ${route} ${width}`);
      check(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),`No horizontal overflow ${route} ${width}`);
    }
  }
  await page.goto(origin+'/');await page.locator('.preview-cta').click();
  check(await page.locator('#s30-name').isVisible(),'registration dialog still opens');await page.keyboard.press('Escape');
  await page.goto(origin+'/blogs.html');check(await page.locator('#blogs-grid .blog-card').count()>100,'blog catalogue remains populated');
  await page.goto(origin+'/blog.html?doc=docs/ai-architecture/ai-stack-7-layers.md');await page.locator('.blog-body').waitFor();
  check(await page.locator('.blog-body').innerText().then(t=>t.length>100),'blog article remains readable');
  await page.goto(origin+'/privacy.html');check(await page.getByRole('heading',{name:'ADK Training Portal'}).isVisible(),'portal privacy notice present');
  check(errors.length===0,`No runtime errors: ${errors.join('; ')}`);
  console.log(JSON.stringify({passed:passed.length,checks:passed},null,2));
}finally{await browser?.close();await new Promise(resolve=>server.close(resolve));}
