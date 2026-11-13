// Learn-card thumbnails: node kit/thumb.js src/anim/<page>.html out.png 0.55, then crop (0,30,900,480) -> src/posters/learn/<page>.jpg 720x360.
// node thumb.js anim.html out.png frac
const {chromium} = require('/opt/npm-tools/node_modules/playwright');
(async () => { const [,, page, out, frac] = process.argv; const b = await chromium.launch();
  const p = await b.newPage({viewport: {width: 900, height: 700}, deviceScaleFactor: 1});
  await p.goto('file://' + page + '?embed=1'); await p.waitForTimeout(900);
  const ok = await p.evaluate((f) => { if (!window.__A) return false; window.__hold = true; window.__A.render(window.__A.total * f); return true; }, +frac);
  await p.waitForTimeout(200); await p.screenshot({path: out}); console.log(out, ok); await b.close(); })();
