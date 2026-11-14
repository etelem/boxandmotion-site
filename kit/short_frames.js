// node short_frames.js page.html framesDir FROM TO SPEEDS
// Renders 1080x1920 PNG frames of a Short (any page with ?short=1 and window.__A = {render, total, loop?}).
// House standard (Nov 10, 2026; end card added Nov 12): Shorts open mid-motion and LOOP. With one speed ("1") and window.__A.loop = {start, cut}:
// frames run from loop.start to loop.cut (skipping any end card), then a 0.6 s blend back into the opening frame with a slim
// Box & Motion strip, so the last frame matches the first. loop.native = the page already loops itself (render 0..total as is).
// Legacy (several SPEEDS, e.g. "1,0.45"): plays once per speed, slow passes labelled, then holds the last frame HOLD s (default 0).
const {chromium} = require('/opt/npm-tools/node_modules/playwright');
const [,, page, dir, from, to, speedsArg] = process.argv;
const FPS = 30, HOLD = process.env.HOLD != null ? +process.env.HOLD : 0, XF = 0.35, CARD_IN = 0.15, CARD_HOLD = 3.0;
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({viewport: {width: 540, height: 960}, deviceScaleFactor: 2});
  await p.goto('file://' + page + '?short=1'); await p.waitForTimeout(1200);
  const info = await p.evaluate(() => { window.__hold = true; const w = document.querySelector('.wrap'); document.body.replaceChildren(w); document.body.style.margin = 0; w.style.position = 'relative';
    const tag = document.createElement('div'); tag.id = 'slowtag'; tag.textContent = 'SLOW MOTION';
    Object.assign(tag.style, {position: 'absolute', right: '28px', top: '24px', font: "500 14px 'IBM Plex Mono',monospace", letterSpacing: '.16em', padding: '6px 10px', borderRadius: '999px', border: '1.5px solid currentColor', color: '#FF5A1F', display: 'none'});
    w.appendChild(tag);
    // branded end card (the owner, Nov 12, 2026): YouTube handle, site and newsletter, shown for ~1.5 s before the loop-back
    const strip = document.createElement('div'); strip.id = 'bmstrip';
    const row = (k, v) => `<div style="margin-top:22px"><div style="font:500 13px 'IBM Plex Mono',monospace;letter-spacing:.16em;color:#FF5A1F">${k}</div><div style="font:700 25px Archivo,'IBM Plex Sans',sans-serif;color:#fff;margin-top:4px">${v}</div></div>`;
    strip.innerHTML = "<div style=\"font:800 40px/1.05 Archivo,'IBM Plex Sans',sans-serif;color:#fff;letter-spacing:.01em\">BOX &amp; MOTION<br>HOOPS</div>"
      + "<div style=\"width:64px;height:5px;background:#FF5A1F;margin:18px 0 6px\"></div>"
      + "<div style=\"font:600 18px 'IBM Plex Sans',sans-serif;color:#c9ccd2\">Every NBA game, in motion.</div>"
      + row('YOUTUBE', '@boxandmotion') + row('EVERY GAME', 'boxandmotion.com') + row('FREE SUNDAY NEWSLETTER', 'The Sunday Box')
      + "<div style=\"font:600 15px 'IBM Plex Sans',sans-serif;color:#c9ccd2;margin-top:6px\">boxandmotion.beehiiv.com/subscribe</div>"
      + "<div style=\"position:absolute;left:44px;right:44px;bottom:40px;font:400 12px 'IBM Plex Sans',sans-serif;color:#8a8f99\">Unofficial fan content. Not affiliated with the NBA or any team.</div>";
    Object.assign(strip.style, {position: 'absolute', inset: 0, padding: '170px 44px 0', boxSizing: 'border-box', background: '#111214', opacity: 0});
    w.appendChild(strip);
    return {total: window.__A.total, loop: window.__A.loop || null}; });
  const speeds = (speedsArg || '1').split(',').map(Number);
  const seq = []; // [animTime, slow, blend (0..1 toward the opening frame), strip opacity]
  const L = info.loop;
  if (speeds.length === 1 && speeds[0] === 1 && L && !L.native) {
    const n = Math.round((L.cut - L.start) * FPS), nx = Math.round(XF * FPS);
    for (let i = 0; i < n; i++) seq.push([L.start + i / FPS, false, 0, 0]);
    // end card: fade in, hold, then fade out onto the opening frame so the Short still loops
    const fin = Math.round(CARD_IN * FPS), hold = Math.round(CARD_HOLD * FPS);
    for (let i = 1; i <= fin; i++) seq.push([L.cut - 1 / FPS, false, 0, i / fin]);
    for (let i = 0; i < hold; i++) seq.push([L.cut - 1 / FPS, false, 1, 1]);
    for (let i = 1; i <= nx; i++) { const u = i / nx; seq.push([L.cut - 1 / FPS, false, 1, 1 - u * u * (3 - 2 * u)]); }
  } else {
    speeds.forEach((sp) => { const n = Math.round(info.total / sp * FPS); for (let i = 0; i < n; i++) seq.push([i / FPS * sp, sp !== 1, 0, 0]); });
    for (let i = 0; i < HOLD * FPS; i++) seq.push([info.total, false, 0, 0]);
    for (let i = 1; i <= Math.round((CARD_IN + CARD_HOLD) * FPS); i++) seq.push([info.total, false, 0, Math.min(1, i / (CARD_IN * FPS))]);
  }
  if (+from === 0) console.log('frames', seq.length);
  // snapshot of the opening frame, laid over the page during the loop-back blend
  if (L && !L.native) await p.evaluate((st) => { window.__A.render(st); const w = document.querySelector('.wrap');
    const c = w.cloneNode(true); c.id = 'bmopen'; c.querySelectorAll('#slowtag,#bmstrip').forEach((n) => n.remove());
    const cs = getComputedStyle(w), bs = getComputedStyle(document.body), src = (cs.backgroundImage !== 'none' || cs.backgroundColor !== 'rgba(0, 0, 0, 0)') ? cs : bs;
    Object.assign(c.style, {position: 'absolute', left: 0, top: 0, width: w.offsetWidth + 'px', height: w.offsetHeight + 'px', margin: 0, opacity: 0, pointerEvents: 'none',
      backgroundColor: src.backgroundColor === 'rgba(0, 0, 0, 0)' ? '#111214' : src.backgroundColor, backgroundImage: src.backgroundImage, backgroundSize: src.backgroundSize});
    w.insertBefore(c, document.getElementById('slowtag')); }, L.start);
  const el = p.locator('.wrap').first();
  for (let i = +from; i < Math.min(+to, seq.length); i++) {
    await p.evaluate(([t, slow, bl, so]) => { window.__A.render(t); document.getElementById('slowtag').style.display = slow ? 'block' : 'none';
      const o = document.getElementById('bmopen'); if (o) o.style.opacity = bl; document.getElementById('bmstrip').style.opacity = so; }, seq[i]);
    await el.screenshot({path: `${dir}/f${String(i).padStart(4, '0')}.png`});
  }
  await b.close();
})();
