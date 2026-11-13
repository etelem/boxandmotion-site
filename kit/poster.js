// Used by kit/make_posters.py (node kit/poster.js reel.html out.png frac light).
// node poster2.js reel.html out.png frac light(0|1)  -> play-of-the-game frame, header hidden; light=1 re-skins it on a light court
let pw; try { pw = require('playwright'); } catch (e) { pw = require('/opt/npm-tools/node_modules/playwright'); }
const {chromium} = pw;
(async () => { const [,, page, out, fracArg, light] = process.argv; const b = await chromium.launch();
  const p = await b.newPage({viewport: {width: 1000, height: 700}, deviceScaleFactor: 1.5});
  await p.goto('file://' + page + '?embed=1'); await p.waitForTimeout(900);
  await p.evaluate((frac) => { const src = [...document.scripts].map((s) => s.textContent).join('\n');
    const m = src.match(/\{id: 'play'[^}]*t0: ([\d.]+), t1: ([\d.]+)\}/); const t = +m[1] + frac * (+m[2] - +m[1]);
    const s = document.querySelector('input[type=range]'); s.value = t; s.dispatchEvent(new Event('input')); }, +fracArg);
  await p.waitForTimeout(150);
  await p.evaluate((light) => { const stage = document.querySelector('.stage'), st = stage.getBoundingClientRect();
    const all = [...stage.querySelectorAll('svg *')];
    all.forEach((e) => { const r = e.getBoundingClientRect(); const tag = e.tagName;
      if (['text', 'rect', 'image', 'use'].includes(tag) && r.top - st.top < 330 && r.left - st.left < 420 && r.width < 700) e.style.visibility = 'hidden';
      if (r.width > 0 && r.width < 60 && r.top - st.top < 90 && r.left - st.left < 90) e.style.visibility = 'hidden'; });
    if (!light) return;
    stage.style.background = '#f3f3f1'; stage.querySelectorAll('svg').forEach((s) => { s.style.background = 'transparent'; });
    const lum = (c) => { const m = c.match(/rgba?\(([\d.]+),\s*([\d.]+),\s*([\d.]+)/); return m ? 0.299 * m[1] + 0.587 * m[2] + 0.114 * m[3] : -1; };
    all.forEach((e) => { const cs = getComputedStyle(e);
      // full-stage background rects/gradients go away
      const r = e.getBoundingClientRect(); if ((e.tagName === 'rect' || e.tagName === 'path') && r.width > st.width * 0.9 && r.height > st.height * 0.8) { e.style.visibility = 'hidden'; return; }
      if (lum(cs.stroke) > 200) e.style.stroke = '#2a2c31';
      if (lum(cs.fill) > 200 && e.tagName !== 'text') e.style.fill = '#2a2c31';
      if (e.tagName === 'text') { if (/^\+\d$/.test(e.textContent.trim())) e.style.fill = '#16181d'; else e.style.visibility = 'hidden'; }
      if (cs.filter && cs.filter !== 'none') e.style.filter = 'none'; });
  }, light === '1');
  await p.locator('.stage').screenshot({path: out});
  await b.close(); })();
