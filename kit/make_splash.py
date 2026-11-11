"""Signature move: Steph Curry's jumper ("The Splash"), 9:16 Short and site embed.
Usage (from the repo root): python3 kit/make_splash.py [kit/moves/steph-splash.json] -> src/anim/<out>
Then: bash kit/short_mp4.sh src/anim/<out> kit/out/<name>.mp4 1
Order: the shot at full speed (one motion, released on the way up, high arc, he turns away, the net splashes),
then a slow breakdown with three numbered beats, then the end card. Original illustration, not traced, not to scale."""
import os, sys, json, html
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from make_reel import team_palette
src = open(os.path.join(HERE, 'make_playshort.py')).read()
HEAD = src[src.index('HTML = r"""') + 11: src.index('__FIGURE_REAL__') + len('__FIGURE_REAL__')]
base = open(os.path.join(HERE, 'base-reel.html')).read().split('\n')
start = next(i for i, l in enumerate(base) if l.startswith('  const POSES = {'))
end = next(i for i in range(start, len(base)) if base[i] == '  }' and i > start + 12)
FIGURE = '\n'.join(base[start:end + 1])
FIGURE_REAL = open(os.path.join(HERE, 'figure-real.js')).read()
CFG = json.load(open(sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'moves', 'steph-splash.json')))
PAL = team_palette(CFG['team'])
KIT = CFG['kit']
KITCSS = f".fig-kit-phi{{stroke:{KIT['jersey']};fill:{KIT['jersey']}}}\n.fig-num{{fill:{KIT['number']}}}\n.fig-band{{stroke:{KIT['number']}}}"

BODY = r"""
  // shooting poses (facing right); y is up-negative from the floor
  POSES.set = {head: [8, -224], neck: [6, -200], hip: [-2, -124], lk: [14, -64], lf: [10, 0], rk: [-14, -64], rf: [-22, 0], le: [26, -152], lh: [36, -128], re: [32, -150], rh: [44, -122]};
  POSES.dip = {head: [12, -204], neck: [9, -180], hip: [-8, -106], lk: [22, -58], lf: [10, 0], rk: [-6, -58], rf: [-22, 0], le: [28, -142], lh: [40, -150], re: [34, -140], rh: [46, -148]};
  POSES.rise = {head: [4, -238], neck: [2, -214], hip: [-2, -134], lk: [8, -70], lf: [4, -6], rk: [-10, -70], rf: [-16, -6], le: [28, -214], lh: [26, -256], re: [32, -220], rh: [30, -262]};
  POSES.rel = {head: [4, -240], neck: [2, -216], hip: [-2, -136], lk: [6, -72], lf: [2, -8], rk: [-12, -72], rf: [-18, -8], le: [20, -222], lh: [26, -250], re: [26, -262], rh: [46, -304]};
  POSES.hold = {head: [6, -226], neck: [4, -202], hip: [-4, -124], lk: [12, -64], lf: [8, 0], rk: [-10, -64], rf: [-18, 0], le: [22, -190], lh: [30, -206], re: [26, -250], rh: [44, -290]};
  POSES.walk1 = {head: [4, -226], neck: [2, -202], hip: [0, -126], lk: [20, -66], lf: [30, 0], rk: [-14, -64], rf: [-32, 0], le: [-6, -162], lh: [-4, -132], re: [14, -238], rh: [18, -284]};
  POSES.walk2 = {head: [4, -226], neck: [2, -202], hip: [0, -126], lk: [-14, -64], lf: [-32, 0], rk: [20, -66], rf: [30, 0], le: [-6, -162], lh: [-4, -132], re: [14, -238], rh: [18, -284]};
  POSES.close = {head: [-10, -226], neck: [-8, -202], hip: [0, -124], lk: [-22, -66], lf: [-36, 0], rk: [20, -66], rf: [30, 0], le: [-30, -184], lh: [-44, -206], re: [26, -184], rh: [44, -204]};

  const svg = document.getElementById('sv');
  const W = 900, H = 1600, M = 56, k = 1.32, GOLD = C.gold;
  const floor = 1180, hoopX = W - M - 24, rimY = floor - 240 * k * 1.62, rimR = 30 * k;
  // timeline: full-speed shot, slow breakdown in two parts, end card
  const P0 = 0.5, PLAY = 4.9, B0 = 5.8, B_FROM = 0.65, B_MID = 1.6, B_SPD1 = 0.3, B_TO = 3.4, B_SPD2 = 0.6;
  const COLD = !!C.cold_open; // start mid-motion, short loop-back ending instead of the 3.5 s end card
  const CO_PT = 0.95, CO_P0 = -CO_PT, CO_B0 = 3.8;
  const _B0 = COLD ? CO_B0 : B0;
  const B1 = _B0 + (B_MID - B_FROM) / B_SPD1, B2 = B1 + (B_TO - B_MID) / B_SPD2, END0 = B2 + 1.4;
  const RW0 = B2, RW1 = B2 + .45, LOOP_END = RW1 + .85; // rewind to the opening frame, brand strip, loop
  const TOTAL = COLD ? LOOP_END : 19.5;

  const defs = S('defs', {}, svg);
  const glow = S('filter', {id: 'glow', x: '-50%', y: '-50%', width: '200%', height: '200%'}, defs);
  S('feGaussianBlur', {stdDeviation: 6, result: 'b'}, glow);
  const mg = S('feMerge', {}, glow); S('feMergeNode', {in: 'b'}, mg); S('feMergeNode', {in: 'SourceGraphic'}, mg);

  const play = S('g', {}, svg);
  T(play, M, 92, C.kicker, 'k', 26);
  if (C.cold_open) { T(play, M, 178, C.hook[0], 'd', 74); T(play, M, 252, C.hook[1], 'd', 74); }
  else { T(play, M, 196, C.hook[0], 'd', 96); T(play, M, 256, C.hook[1], 'b m', 40); }
  const slowTag = S('g', {opacity: 0}, play);
  S('rect', {x: W - M - 250, y: 300, width: 250, height: 52, rx: 26, fill: 'none', stroke: 'var(--red)', 'stroke-width': 2.5}, slowTag);
  T(slowTag, W - M - 125, 335, 'SLOW MOTION', 'k', 24, 'middle').style.fill = 'var(--red)';
  // court
  const court = S('g', {class: 's-silver', 'stroke-width': 3, 'stroke-linecap': 'round', opacity: .9}, play);
  S('line', {x1: -20, x2: W + 20, y1: floor, y2: floor}, court);
  S('line', {x1: hoopX + 40 * k, x2: hoopX + 40 * k, y1: rimY - 120 * k, y2: floor}, court);
  const arcX = 340; S('line', {x1: arcX, x2: arcX, y1: floor - 6, y2: floor + 16}, court);
  T(play, arcX, floor + 44, '3-point line', 'b m', 22, 'middle');
  S('rect', {x: hoopX + 26 * k, y: rimY - 150 * k, width: 12 * k, height: 170 * k, rx: 3, fill: 'var(--silver)'}, play);
  // the splash: rings on the "water" at the rim, droplets thrown out of the net
  const rings = [0, 1, 2].map(() => S('ellipse', {cx: hoopX, cy: rimY + 4, rx: 0, ry: 0, fill: 'none', stroke: GOLD, 'stroke-width': 3, opacity: 0}, play));
  const drops = Array.from({length: 16}, (_, i) => ({a: -Math.PI / 2 + (i / 15 - .5) * 2.6, v: 260 + (i * 53) % 170, r: 7 + (i * 7) % 6, n: S('circle', {r: 6, fill: i % 3 ? '#cfe6ff' : GOLD, opacity: 0}, play)}));
  const net = S('g', {class: 's-silver', 'stroke-width': 2.4, opacity: .85}, play);
  const netL = Array.from({length: 5}, () => S('line', {}, net));
  const netX = Array.from({length: 2}, () => S('path', {fill: 'none'}, net));
  S('line', {x1: hoopX - rimR, x2: hoopX + 26 * k, y1: rimY, y2: rimY, class: 's-red', 'stroke-width': 6, 'stroke-linecap': 'round'}, play);
  const drawNet = (snap) => { // snap 0..1: the net whips down and settles
    const L = 44 * k * (1 + .55 * snap);
    netL.forEach((l, i) => { const tp = hoopX - rimR + i * rimR / 2, bt = hoopX - rimR * (.55 - .18 * snap) + i * rimR * (1.1 - .36 * snap) / 4; l.setAttribute('x1', tp); l.setAttribute('y1', rimY); l.setAttribute('x2', bt); l.setAttribute('y2', rimY + L); });
    [0.45, 0.8].forEach((f, j) => { const y = rimY + L * f, w = rimR * (1 - f * (.45 + .2 * snap)); netX[j].setAttribute('d', `M${hoopX - w} ${y}L${hoopX + w} ${y}`); });
  };
  // figures
  const defender = figure(play, 'opp', k); defender.g.setAttribute('opacity', .85);
  const ghosts = [0, 1, 2, 3].map(() => { const gh = figureReal(play, 'phi', k, C.number, C.build); gh.g.style.opacity = 0; return gh; }).reverse();
  const star = figureReal(play, 'phi', k, C.number, C.build);
  const ribbon = S('path', {fill: 'none', stroke: GOLD, 'stroke-width': 7, 'stroke-linecap': 'round', opacity: 0, filter: 'url(#glow)'}, play);
  const trail = S('path', {fill: 'none', stroke: GOLD, 'stroke-width': 5, 'stroke-linecap': 'round', opacity: .75, filter: 'url(#glow)'}, play);
  const sparks = Array.from({length: 14}, () => S('circle', {r: 3.5, fill: GOLD, opacity: 0}, play));
  const ballG = S('g', {}, play);
  S('circle', {r: 13 * k, class: 'f-ink', filter: 'url(#glow)'}, ballG);
  const seam = S('path', {d: `M${-13 * k} 0L${13 * k} 0M0 ${-13 * k}Q${7 * k} 0 0 ${13 * k}`, stroke: 'rgba(17,18,20,.55)', 'stroke-width': 2.4, fill: 'none'}, ballG);
  const stamp = T(play, hoopX - 46, rimY - 150, 'SPLASH', 'd', 92, 'end'); stamp.style.fill = GOLD;
  // step captions under the floor
  const capG = S('g', {}, play);
  const cap = C.steps.map((s, i) => { const g = S('g', {opacity: 0}, capG); const n = T(g, M, floor + 150, `${i + 1}`, 'd', 64); n.style.fill = GOLD; T(g, M + 62, floor + 150, s[0], 'd', 54); T(g, M, floor + 212, s[1], 'b m', 36); return g; });
  T(play, M, H - 56, 'Original illustration · not traced from footage, not to scale', 'b m', 22);

  // ---- the shot, as a function of play-time pt (0..PLAY) ----
  const x0 = 240, tD = 0.75, tU = 1.1, tR = 1.32, tL = 1.85, tTurn = 2.15, tM = 3.05;
  const liftAt = (pt) => pt < tU ? 0 : pt < tL ? 46 * Math.sin(Math.PI * clamp((pt - tU) / (tL - tU))) : 0;
  const starAt = (pt) => {
    let pose, x = x0, dir = 1;
    if (pt < tD) { const c = (pt * 2.6) % 1; pose = mixPose(POSES.set, POSES.dip, c < .5 ? 0 : 0); } // squared up, ball at the hip
    if (pt < tD) pose = POSES.set;
    else if (pt < tU) pose = mixPose(POSES.set, POSES.dip, prog(pt, tD, .25));
    else if (pt < tR) pose = mixPose(POSES.dip, POSES.rise, inout(clamp((pt - tU) / (tR - tU))));
    else if (pt < tR + .1) pose = mixPose(POSES.rise, POSES.rel, prog(pt, tR - .02, .1));
    else if (pt < tTurn) pose = mixPose(POSES.rel, POSES.hold, prog(pt, tL - .15, .3));
    else { dir = -1; const w = pt - tTurn; x = x0 - 135 * k * clamp(w / 2.4); const c = Math.sin(w * 7) * .5 + .5; pose = mixPose(POSES.walk1, POSES.walk2, c); if (w < .25) pose = mixPose(POSES.hold, pose, w / .25); }
    return [pose, x, liftAt(pt), dir];
  };
  const relPt = (() => { const at = star.draw(POSES.rel, x0, floor - liftAt(tR) * k, k, 1); const h = at('rh'); return [h[0] + 10 * k, h[1] - 14 * k]; })();
  const peak = 330;
  const arcAt = (u) => [lerp(relPt[0], hoopX, u), lerp(relPt[1], rimY - 8, u) - 4 * peak * u * (1 - u)];
  const pathTo = (f, u0, u1, n) => 'M' + Array.from({length: n + 1}, (_, i) => f(u0 + (u1 - u0) * i / n)).map(([x, y]) => `${x.toFixed(1)} ${y.toFixed(1)}`).join('L');
  // the "one motion" ribbon: where the ball travels from the hip to the release
  const handBall = (pt) => { const [p, x, l] = starAt(pt); const at = star.draw(p, x, floor - l * k, k, 1); const a = at('rh'), b = at('lh'); return [(a[0] + b[0]) / 2 + 8 * k, (a[1] + b[1]) / 2 - 6 * k]; };
  const ribbonPts = []; for (let q = tD; q <= tR + .001; q += (tR - tD) / 24) ribbonPts.push(handBall(q));

  const drawShot = (pt, slow) => {
    const [pose, x, lift, dir] = starAt(pt);
    const shooting = pt > tD - .1 && pt < tR + .35;
    ghosts.forEach((gh, i) => {
      if (!slow || !shooting) { gh.g.style.opacity = 0; return; }
      const [gp, gx, gl, gd] = starAt(pt - (i + 1) * .07);
      gh.draw(gp, gx, floor - gl * k, k, gd); gh.g.style.opacity = (.36 - i * .08).toFixed(2);
    });
    const at = star.draw(pose, x, floor - lift * k, k, dir);
    // defender closes out from the paint, hand up as the ball leaves
    let dx = lerp(x0 + 300 * k, x0 + 120 * k, prog(pt, .2, 1.0)), dPose = POSES.close, dl = 0;
    if (pt > tU - .1) { dPose = mixPose(POSES.close, POSES.contest, prog(pt, tU - .1, .3)); dl = 30 * Math.sin(Math.PI * clamp((pt - tU) / .7)); }
    if (pt > tL + .2) dPose = mixPose(POSES.contest, POSES.guard, prog(pt, tL + .2, .4));
    defender.draw(dPose, dx, floor - dl * k, k, -1);
    // ball
    let bx, by, spin = 0;
    if (pt < tD) { const a = at('rh'); const ph = (pt * 2.4) % 1, f = ph < .5 ? ph * 2 : (1 - ph) * 2; bx = a[0] + 8 * k; by = lerp(a[1], floor - 13 * k, f * f * (3 - 2 * f)); }
    else if (pt < tR) [bx, by] = handBall(pt);
    else if (pt < tM) { const u = clamp((pt - tR) / (tM - tR)); [bx, by] = arcAt(u); spin = -(pt - tR) * 1440; }
    else { const d = clamp((pt - tM) / .55); bx = hoopX; by = lerp(rimY - 8, floor - 13 * k, d * d); spin = -(tM - tR) * 1440 - (pt - tM) * 600; }
    ballG.setAttribute('transform', `translate(${bx.toFixed(1)} ${by.toFixed(1)})`); seam.setAttribute('transform', `rotate(${spin.toFixed(0)})`);
    // one-motion ribbon (slow breakdown only)
    const rOn = slow && pt > tD && pt < tR + .6;
    if (rOn) { const n = Math.max(1, Math.round(24 * clamp((pt - tD) / (tR - tD)))); ribbon.setAttribute('d', 'M' + ribbonPts.slice(0, n + 1).map(([a, b]) => `${a.toFixed(1)} ${b.toFixed(1)}`).join('L')); }
    ribbon.setAttribute('opacity', rOn ? (.9 * (1 - prog(pt, tR + .3, .3))).toFixed(2) : 0);
    // gold arc trail + sparks falling off it
    const u = pt <= tR ? 0 : clamp((pt - tR) / (tM - tR));
    trail.setAttribute('d', u > 0 ? pathTo(arcAt, 0, u, Math.max(2, Math.round(u * 60))) : 'M0 0');
    trail.setAttribute('opacity', pt < tM ? .75 : (.75 * (1 - prog(pt, tM, .5))).toFixed(2));
    sparks.forEach((s, i) => { const su = (i + .5) / sparks.length, born = tR + su * (tM - tR), age = pt - born;
      if (age < 0 || age > 1.1) { s.setAttribute('opacity', 0); return; }
      const [sx, sy] = arcAt(su); s.setAttribute('cx', sx + Math.sin(i * 2.1) * 10 * age); s.setAttribute('cy', sy + 70 * age * age + 20 * age); s.setAttribute('opacity', (1 - age / 1.1).toFixed(2)); });
    // the splash
    const sp = pt - tM;
    drawNet(sp > 0 ? Math.sin(Math.PI * clamp(sp / .5)) * (sp < .5 ? 1 : 0) + (sp >= .5 ? .25 * Math.sin(Math.PI * clamp((sp - .5) / .4)) : 0) : 0);
    rings.forEach((r, i) => { const a = sp - i * .14; if (a < 0 || a > 1) { r.setAttribute('opacity', 0); return; } const e = ease(a); r.setAttribute('rx', rimR + 150 * e); r.setAttribute('ry', 10 + 34 * e); r.setAttribute('opacity', (1 - a).toFixed(2)); });
    drops.forEach((d, i) => { const a = sp - .02; if (a < 0 || a > 1) { d.n.setAttribute('opacity', 0); return; } d.n.setAttribute('cx', hoopX + Math.cos(d.a) * d.v * a); d.n.setAttribute('cy', rimY + 30 * k + Math.sin(d.a) * d.v * a + 520 * a * a); d.n.setAttribute('r', d.r * (1 - a * .5)); d.n.setAttribute('opacity', (1 - a).toFixed(2)); });
    stamp.style.opacity = sp > 0 ? prog(pt, tM + .05, .2) * (1 - prog(pt, tM + 1.4, .4)) : 0;
    stamp.setAttribute('transform', `translate(0 ${sp > 0 ? -16 * prog(pt, tM, .6) : 0})`);
    slowTag.setAttribute('opacity', slow ? 1 : 0);
  };

  // ---- end card ----
  const endc = S('g', {opacity: 0}, svg);
  S('rect', {width: W, height: H, fill: '#111214'}, endc);
  const lg = S('g', {transform: `translate(${W / 2 - 120} 430)`}, endc);
  S('rect', {x: 0, y: 0, width: 240, height: 240, rx: 44, fill: 'none', stroke: '#fff', 'stroke-width': 26}, lg);
  S('path', {d: 'M58 52 L112 106 M112 52 L58 106', stroke: '#fff', 'stroke-width': 26, 'stroke-linecap': 'round'}, lg);
  [[92, 150], [104, 186], [130, 214]].forEach(([cx, cy]) => S('circle', {cx, cy, r: 12, fill: '#FF5A1F'}, lg));
  S('circle', {cx: 182, cy: 190, r: 34, fill: 'none', stroke: '#FF5A1F', 'stroke-width': 24}, lg);
  T(endc, W / 2, 800, 'BOX & MOTION HOOPS', 'd', 56, 'middle');
  const tg = T(endc, W / 2, 870, 'The box score, in motion.', 'b', 38, 'middle'); tg.style.fill = '#FF5A1F';
  // Shorts links aren't clickable, so the address is big enough to remember (kept above y 1200, clear of the Shorts overlay)
  T(endc, W / 2, 990, 'Signature moves and every game', 'b m', 32, 'middle');
  const url = T(endc, W / 2, 1068, 'boxandmotion.com', 'd', 64, 'middle'); url.style.fill = '#fff';
  S('rect', {x: W / 2 - 150, y: 1090, width: 300, height: 8, rx: 4, fill: '#FF5A1F'}, endc);
  T(endc, W / 2, 1170, 'Free Sunday newsletter: link on our channel', 'b m', 30, 'middle');

  let strip = null, rwTag = null;
  if (C.cold_open) {
    strip = S('g', {opacity: 0}, svg);
    S('rect', {x: 0, y: floor + 96, width: W, height: 150, fill: '#111214', opacity: .92}, strip);
    T(strip, M, floor + 160, 'BOX & MOTION HOOPS', 'd', 44);
    const st = T(strip, M, floor + 208, 'Signature moves at boxandmotion.com', 'b', 30); st.style.fill = '#FF5A1F';
    rwTag = T(svg, W - M, 335, '◀◀ AGAIN', 'k', 26, 'end'); rwTag.style.fill = 'var(--red)'; rwTag.setAttribute('opacity', 0);
  }
  const render = (t) => {
    let pt, slow = false;
    if (t < _B0) pt = Math.max(0, Math.min(PLAY, t - (COLD ? CO_P0 : P0)));
    else if (t < B1) { pt = B_FROM + (t - _B0) * B_SPD1; slow = true; }
    else if (t < B2) { pt = B_MID + (t - B1) * B_SPD2; slow = true; }
    else if (COLD && t < RW1) pt = lerp(B_TO, CO_PT, inout(clamp((t - RW0) / (RW1 - RW0))));
    else pt = COLD ? CO_PT : B_TO;
    drawShot(pt, slow);
    const step = t < _B0 || (COLD && t >= B2) ? -1 : pt < 1.18 ? 0 : pt < 1.95 ? 1 : 2;
    cap.forEach((g, i) => g.setAttribute('opacity', i === step && (COLD || t < END0) ? 1 : 0));
    endc.setAttribute('opacity', !COLD && t >= END0 ? prog(t, END0, .35) : 0);
    if (strip) strip.setAttribute('opacity', COLD && t >= RW0 ? prog(t, RW0, .2) * (1 - prog(t, LOOP_END - .15, .15)) : 0);
    if (rwTag) rwTag.setAttribute('opacity', COLD && t >= RW0 && t < RW1 ? 1 : 0);
  };
  let time = 0, last = null;
  const frame = (now) => { if (last != null) { time += (now - last) / 1000; if (time > TOTAL) time = 0; } last = now; if (!window.__hold) render(time); requestAnimationFrame(frame); };
  render(0); requestAnimationFrame(frame);
  window.__A = {render, build: () => {}, total: TOTAL};
  const postH = () => { try { parent.postMessage({bmH: document.documentElement.scrollHeight}, '*'); } catch (e) {} };
  addEventListener('load', postH); addEventListener('resize', postH);
})();
</script>
</body></html>
"""
out = (HEAD + BODY).replace('__KITCSS__', KITCSS).replace('__PAL__', PAL).replace('__FIGURE__', FIGURE).replace('__FIGURE_REAL__', FIGURE_REAL)
out = out.replace('__TITLE__', html.escape(f"{CFG['name']}: {CFG['hook'][0]}")).replace('__ARIA__', html.escape(CFG['aria'])).replace('__CFG__', json.dumps(CFG, ensure_ascii=False))
dst = os.path.join(ROOT, 'src', 'anim', CFG['out'])
open(dst, 'w').write(out)
print('wrote', os.path.relpath(dst, ROOT))
