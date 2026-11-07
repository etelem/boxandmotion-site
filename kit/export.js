// node export.js render-copy.html framesDir FROM TO  -> PNG frames of the portrait reel at 1080x1560 (background from the reel's own palette)
const {chromium}=require('/opt/npm-tools/node_modules/playwright');
const [,, page, dir, from, to] = process.argv;
(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1000,height:1400},deviceScaleFactor:1.2});
await p.goto('file://'+page);await p.waitForTimeout(800);
await p.evaluate(()=>{window.__forceP=true;window.__R.build(true);const s=document.getElementById('reel');document.body.replaceChildren(s);document.body.style.margin=0;s.style.width='900px';s.style.height='1300px';s.style.display='block';const v=(n)=>getComputedStyle(document.documentElement).getPropertyValue(n).trim();s.style.background=`radial-gradient(120% 95% at 12% 0%,${v('--navy-lift')},${v('--navy-mid')} 55%,${v('--navy')})`;});
const el=p.locator('#reel');
for(let i=+from;i<+to;i++){await p.evaluate((t)=>window.__R.render(t),i/30);await el.screenshot({path:`${dir}/f${String(i).padStart(4,'0')}.png`});}
await b.close();})();
