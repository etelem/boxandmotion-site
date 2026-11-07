const {chromium}=require('/opt/npm-tools/node_modules/playwright');
const [,, page, prefix, portrait, ...times] = process.argv;
(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1000,height:1400},deviceScaleFactor:0.5});
const errs=[];p.on('pageerror',e=>errs.push(e.message));
await p.goto('file://'+page);await p.waitForTimeout(800);
await p.evaluate((P)=>{window.__forceP=P;window.__R.build(P);const s=document.getElementById('reel');document.body.replaceChildren(s);document.body.style.margin=0;s.style.width=P?'900px':'1600px';s.style.height=P?'1300px':'900px';s.style.display='block';s.style.background='#222';},portrait==='1');
const el=p.locator('#reel');
for(const t of times){await p.evaluate((t)=>window.__R.render(t),+t);await el.screenshot({path:`${prefix}-${t}.png`});}
console.log('errors',errs);await b.close();})();
