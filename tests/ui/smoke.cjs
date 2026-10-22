const {chromium} = require('playwright-core');
const path=require('path'); const fs=require('fs');
(async()=>{
 const browser=await chromium.launch({executablePath:process.env.CHROME_EXECUTABLE,headless:true,args:['--no-sandbox','--disable-dev-shm-usage']});
 const page=await browser.newPage({viewport:{width:1440,height:1100},deviceScaleFactor:1});
 const errors=[];const requests=[];page.on('pageerror',x=>errors.push(x.message));page.on('request',r=>requests.push(r.url()));
 await page.emulateMedia({reducedMotion:'reduce'});
 const entrypoints=['index.html','demo/index.html','demo/IRProof.html'];
 for(const entrypoint of entrypoints){
  await page.goto('file://'+path.resolve(entrypoint));await page.evaluate(()=>document.fonts.ready);
  if(await page.locator('[data-case]').count()!==35)throw new Error('Missing cases in '+entrypoint);
 }
 
 if(await page.locator('[data-case]').count()!==35)throw new Error('Missing cases');
 await page.locator('[data-filter=refuted]').click();if(await page.locator('[data-case]').count()!==9)throw new Error('Refuted filter');
 await page.locator('#case-search').fill('nsw');if(await page.locator('[data-case]').count()<1)throw new Error('Search');
 await page.locator('[data-action=counterexample]').click();await page.locator('[data-tab=raw]').first().click();
 if(!(await page.locator('.terminal').innerText()).includes('Value mismatch'))throw new Error('Raw evidence missing');
 await page.locator('[data-tab=provenance]').click();if(!(await page.locator('.hash-table').innerText()).includes('5.3.1'))throw new Error('Provenance');
 await page.locator('[data-route=graphs]').click();if(await page.locator('.graph-node').count()!==4)throw new Error('Graph nodes');
 await page.locator('[data-node=b1]').click();if(!(await page.locator('.graph-info').innerText()).includes('immediate dominator'))throw new Error('Graph selection');
 await page.locator('#graph-scenario').selectOption('loop');if(await page.locator('.backedge').count()!==1)throw new Error('Loop edge');
 
 await page.locator('[data-graph-mode=dataflow]').click();if(await page.locator('.graph-node').count()<8)throw new Error('Dataflow');
 await page.locator('[data-route=verification]').click();
 await page.locator('#lab-width').selectOption('128');await page.locator('#lab-x').fill('-170141183460469231731687303715884105728');
 if(await page.locator('.lab-error').count())throw new Error('128-bit lab');
 const downloadEvent=page.waitForEvent('download');await page.locator('[data-action=export]').click();const dl=await downloadEvent;const file=await dl.path();const exp=JSON.parse(fs.readFileSync(file));if(exp.cases.length!==35)throw new Error('Export');
 await page.locator('[data-action=counterexample]').click();await page.locator('[data-tab=comparison]').first().focus();await page.keyboard.press('ArrowRight');if(!(await page.locator('[role=tab][aria-selected=true]').innerText()).includes('Validator'))throw new Error('Keyboard tabs');
 await page.locator('[data-case="sdiv-32-8"]').click();await page.locator('[data-tab=comparison]').click();
 await page.locator('#lab-width').selectOption('32');await page.locator('#lab-x').fill('-3');
 await page.setViewportSize({width:390,height:844});await page.evaluate(()=>scrollTo(0,0));
 
 const dims=await page.evaluate(()=>({w:innerWidth,sw:document.documentElement.scrollWidth}));const railRight=await page.locator('.rail').evaluate(el=>el.getBoundingClientRect().right);if(railRight>1)throw new Error('Mobile navigation did not hide');if(dims.sw>dims.w)throw new Error('Mobile overflow '+JSON.stringify(dims));
 await page.locator('[data-action=menu]').click();await page.locator('[data-route=notes]').click();if(!(await page.locator('h1').innerText()).includes('What each result'))throw new Error('Mobile navigation');
 if(errors.length)throw new Error(JSON.stringify(errors));
 if(requests.some(u=>/^https?:/.test(u)))throw new Error('Offline export made an external request');
 const result={status:'passed',browser:await browser.version(),entrypoints,viewports:[{width:1440,height:1100},{width:390,height:844}],cases:35,refutedFilter:9,checks:['search','captured validator output','provenance','CFG node selection','loop backedge','SSA graph','128-bit arithmetic input','JSON download','keyboard tabs','mobile navigation','no horizontal page overflow','no external requests','no page errors']};
 fs.writeFileSync('evidence/ui-validation.json',JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify(result));
 await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});
