// node kit/learn_posters.js [anim.html ...]
// Tall (9:16) cover images for the Learn cards (the owner, Nov 15: "New in the library should be vertical and big").
// Opens each src/anim page the way the Shorts are rendered (?short=1, 540x960), draws one frame mid-motion and saves
// src/posters/learn-v/<name>.jpg (540x960). With no arguments it does every page that has a 2:1 poster in src/posters/learn/.
// Frame: POSTER_AT (0..1 through the loop, default 0.62). A page can pin its own frame with window.__A.poster = seconds.
const {chromium} = require('/opt/npm-tools/node_modules/playwright');
const fs = require('fs'), path = require('path');
const ROOT = path.resolve(__dirname, '..'), OUT = path.join(ROOT, 'src/posters/learn-v');
const AT = process.env.POSTER_AT != null ? +process.env.POSTER_AT : 0.62;
let pages = process.argv.slice(2);
if (!pages.length) pages = fs.readdirSync(path.join(ROOT, 'src/posters/learn')).filter((f) => f.endsWith('.jpg')).map((f) => f.replace(/\.jpg$/, '.html'));
fs.mkdirSync(OUT, {recursive: true});
(async () => {
  const b = await chromium.launch();
  for (const name of pages) {
    const file = path.join(ROOT, 'src/anim', path.basename(name));
    if (!fs.existsSync(file)) { console.log('skip (no page)', name); continue; }
    const p = await b.newPage({viewport: {width: 540, height: 960}, deviceScaleFactor: 1});
    await p.goto('file://' + file + '?short=1'); await p.waitForTimeout(1500);
    const ok = await p.evaluate((at) => {
      const A = window.__A, w = document.querySelector('.wrap'); if (!A || !w) return false;
      window.__hold = true; document.body.replaceChildren(w); document.body.style.margin = 0; w.style.position = 'relative';
      const L = A.loop && !A.loop.native ? A.loop : {start: 0, cut: A.total};
      const t = A.poster != null ? A.poster : L.start + (L.cut - L.start) * at;
      A.render(t); return true;
    }, AT);
    if (!ok) { console.log('skip (no window.__A)', name); await p.close(); continue; }
    await p.waitForTimeout(300);
    const out = path.join(OUT, path.basename(name).replace(/\.html$/, '.jpg'));
    await p.screenshot({path: out, type: 'jpeg', quality: 82});
    console.log('wrote', path.relative(ROOT, out));
    await p.close();
  }
  await b.close();
})();
