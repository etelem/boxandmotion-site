// node short_frames.js page.html framesDir FROM TO SPEEDS
// Renders 1080x1920 PNG frames of a deep-dive animation (any page with ?short=1 and window.__A = {render, total}).
// The animation plays once per entry in SPEEDS (e.g. "1,0.45": normal, then a slow-motion replay with a label),
// then holds the last frame for 1.2 s. Frames FROM..TO (exclusive) of that sequence are written.
const {chromium} = require('/opt/npm-tools/node_modules/playwright');
const [,, page, dir, from, to, speedsArg] = process.argv;
const FPS = 30, HOLD = process.env.HOLD != null ? +process.env.HOLD : 1.2; // HOLD=0 for looping Shorts
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({viewport: {width: 540, height: 960}, deviceScaleFactor: 2});
  await p.goto('file://' + page + '?short=1'); await p.waitForTimeout(1200);
  const total = await p.evaluate(() => { window.__hold = true; const w = document.querySelector('.wrap'); document.body.replaceChildren(w); document.body.style.margin = 0; w.style.position = 'relative';
    const tag = document.createElement('div'); tag.id = 'slowtag'; tag.textContent = 'SLOW MOTION';
    Object.assign(tag.style, {position: 'absolute', right: '28px', top: '24px', font: "500 14px 'IBM Plex Mono',monospace", letterSpacing: '.16em', padding: '6px 10px', borderRadius: '999px', border: '1.5px solid currentColor', color: '#FF5A1F', display: 'none'});
    w.appendChild(tag); return window.__A.total; });
  const speeds = (speedsArg || '1').split(',').map(Number);
  const seq = []; // [animTime, slow]
  speeds.forEach((sp) => { const n = Math.round(total / sp * FPS); for (let i = 0; i < n; i++) seq.push([i / FPS * sp, sp !== 1]); });
  for (let i = 0; i < HOLD * FPS; i++) seq.push([total, false]);
  if (+from === 0) console.log('frames', seq.length);
  const el = p.locator('.wrap');
  for (let i = +from; i < Math.min(+to, seq.length); i++) {
    await p.evaluate(([t, slow]) => { window.__A.render(t); document.getElementById('slowtag').style.display = slow ? 'block' : 'none'; }, seq[i]);
    await el.screenshot({path: `${dir}/f${String(i).padStart(4, '0')}.png`});
  }
  await b.close();
})();
