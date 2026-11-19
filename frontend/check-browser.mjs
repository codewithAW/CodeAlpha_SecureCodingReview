import {chromium} from 'playwright-core'
import assert from 'node:assert/strict'
import {resolve} from 'node:path'
import {pathToFileURL} from 'node:url'
const url=pathToFileURL(resolve('dist/Open-CodeGuard.html')).href
const browser=await chromium.launch({executablePath:process.env.BROWSER_PATH,timeout:15000,args:['--use-angle=swiftshader','--enable-unsafe-swiftshader']})
try {
 const page=await browser.newPage({viewport:{width:1366,height:900}})
 const errors=[];page.on('pageerror',e=>errors.push(e.message))
 await page.goto(url)
 await page.getByRole('heading',{name:'Audit overview'}).waitFor()
 await page.keyboard.press('Tab')
 assert.equal(await page.locator(':focus').textContent(),'Skip to content')
 await page.locator('.visualFoot span').filter({hasText:'Inspection'}).waitFor({timeout:30000})
 await page.getByRole('button',{name:'Pause animation'}).click()
 await page.getByRole('button',{name:'Play animation'}).waitFor()
 await page.getByRole('link',{name:'Explore Security Audit'}).click()
 await page.getByPlaceholder('Title, ID or component').fill('CG-001')
 assert.equal(await page.locator('.row').count(),1)
 await page.locator('.row').click()
 await page.getByRole('heading',{name:'Owner check missing'}).waitFor()
 await page.getByRole('link',{name:'Code comparison',exact:true}).click()
 await page.locator('select').selectOption('CG-004')
 await page.getByText('Read the role from the database and deny unauthorized access.').waitFor()
 await page.getByRole('link',{name:'Developer lab'}).click()
 await page.getByRole('button',{name:'ID and session user',exact:true}).click()
 await page.reload()
 await page.getByRole('status').filter({hasText:'Correct'}).waitFor()
 await page.setViewportSize({width:390,height:844})
 for(const route of ['/','/findings','/compare','/analysis','/reports','/remediation','/lab']){
  await page.goto(url+'#'+route);await page.locator('main h1').waitFor()
  assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),route)
 }
 await page.emulateMedia({reducedMotion:'reduce'})
 await page.goto(url+'#/')
 await page.locator('.visualFoot span').filter({hasText:'Verified shield'}).waitFor()
 await page.addInitScript(()=>{const old=HTMLCanvasElement.prototype.getContext;HTMLCanvasElement.prototype.getContext=function(t,...args){return t==='webgl'?null:old.call(this,t,...args)}})
 await page.reload();await page.locator('.fallback').waitFor()
 assert.deepEqual(errors,[])
 console.log('PASS: portable launch, keyboard skip link, WebGL transition and pause, finding search and detail, comparison, persistent lab answers, seven mobile routes, reduced motion, WebGL fallback and zero page errors.')
} finally {await browser.close()}
