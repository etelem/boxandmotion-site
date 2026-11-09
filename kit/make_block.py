"""Signature move: Victor Wembanyama's chase-down block ("Denied by Wemby"), 9:16 Short and site embed.
Usage (from the repo root): python3 kit/make_block.py [kit/moves/wemby-denied.json] -> src/anim/<out>
Then: bash kit/short_mp4.sh src/anim/<out> kit/out/<name>.mp4 1
Order: the block at full speed (long strides, the reach above the rim, the ball stops dead and goes back the other way,
DENIED stamp), a slow breakdown with three numbered beats, then the end card. Original illustration, not traced, not to scale."""
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
CFG = json.load(open(sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'moves', 'wemby-denied.json')))
PAL = team_palette(CFG['team'])
KIT = CFG['kit']
KITCSS = f".fig-kit-phi{{stroke:{KIT['jersey']};fill:{KIT['jersey']}}}\n.fig-num{{fill:{KIT['number']}}}\n.fig-band{{stroke:{KIT['number']}}}"

BODY = r"""
  // Wemby poses (facing right)
  POSES.stride1 = {head: [26, -226], neck: [20, -202], hip: [0, -124], lk: [44, -74], lf: [64, -6], rk: [-34, -60], rf: [-72, -22], le: [-14, -160], lh: [-26, -128], re: [40, -164], rh: [62, -140]};
  POSES.stride2 = {head: [26, -226], neck: [20, -202], hip: [0, -124], lk: [-34, -60], lf: [-72, -22], rk: [44, -74], rf: [64, -6], le: [38, -164], lh: [58, -140], re: [-14, -160], rh: [-26, -128]};
  POSES.load = {head: [22, -198], neck: [16, -174], hip: [-6, -102], lk: [26, -54], lf: [14, 0], rk: [-6, -54], rf: [-22, 0], le: [-20, -142], lh: [-38, -122], re: [32, -152], rh: [48, -172]};
  POSES.block = {head: [12, -246], neck: [8, -222], hip: [-2, -140], lk: [18, -96], lf: [4, -46], rk: [-10, -84], rf: [-24, -30], le: [-18, -200], lh: [-42, -212], re: [30, -266], rh: [58, -322]};
  POSES.wland = {head: [10, -222], neck: [6, -198], hip: [-4, -120], lk: [16, -62], lf: [6, 0], rk: [-14, -62], rf: [-26, 0], le: [-16, -170], lh: [-30, -150], re: [28, -200], rh: [40, -236]};
  POSES.stumble = {head: [-18, -214], neck: [-14, -190], hip: [0, -116], lk: [14, -60], lf: [22, 0], rk: [-20, -60], rf: [-34, 0], le: [-30, -160], lh: [-44, -140], re: [10, -164], rh: [22, -140]};

  const svg = document.getElementById('sv');
  const W = 900, H = 1600, M = 56, k = 1.32, ACC = C.accent;
  const floor = 1180, hoopX = W - M - 24, rimY = floor - 240 * k * 1.62, rimR = 30 * k;
  const TOTAL = 17;
  const P0 = 0.5, PLAY = 3.6, B0 = 4.8;
  const SEGS = [[0.35, 1.6, 0.45], [1.6, 2.06, 0.2], [2.06, 3.2, 0.6]]; // breakdown: [from, to, speed] in play-time
  const segT = []; let acc = B0; SEGS.forEach(([a, b, sp]) => { segT.push([acc, acc + (b - a) / sp, a, sp]); acc += (b - a) / sp; });
  const B_END = acc, END0 = B_END + 1.2;

  const defs = S('defs', {}, svg);
  const glow = S('filter', {id: 'glow', x: '-50%', y: '-50%', width: '200%', height: '200%'}, defs);
  S('feGaussianBlur', {stdDeviation: 6, result: 'b'}, glow);
  const mg = S('feMerge', {}, glow); S('feMergeNode', {in: 'b'}, mg); S('feMergeNode', {in: 'SourceGraphic'}, mg);

  const top = S('g', {}, svg);
  T(top, M, 92, C.kicker, 'k', 26);
  T(top, M, 196, C.hook[0], 'd', 84);
  T(top, M, 256, C.hook[1], 'b m', 40);
  const slowTag = S('g', {opacity: 0}, top);
  S('rect', {x: W - M - 250, y: 300, width: 250, height: 52, rx: 26, fill: 'none', stroke: 'var(--red)', 'stroke-width': 2.5}, slowTag);
  T(slowTag, W - M - 125, 335, 'SLOW MOTION', 'k', 24, 'middle').style.fill = 'var(--red)';
  const play = S('g', {}, svg);
  const court = S('g', {class: 's-silver', 'stroke-width': 3, 'stroke-linecap': 'round', opacity: .9}, play);
  S('line', {x1: -40, x2: W + 40, y1: floor, y2: floor}, court);
  S('line', {x1: hoopX + 40 * k, x2: hoopX + 40 * k, y1: rimY - 120 * k, y2: floor + 40}, court);
  S('rect', {x: hoopX + 26 * k, y: rimY - 150 * k, width: 12 * k, height: 170 * k, rx: 3, fill: 'var(--silver)'}, play);
  const net = S('g', {class: 's-silver', 'stroke-width': 2, opacity: .8}, play);
  for (let i = 0; i <= 4; i++) { const tp = hoopX - rimR + i * rimR / 2, bt = hoopX - rimR * .55 + i * rimR * 1.1 / 4; S('line', {x1: tp, y1: rimY, x2: bt, y2: rimY + 44 * k}, net); }
  S('line', {x1: hoopX - rimR, x2: hoopX + 26 * k, y1: rimY, y2: rimY, class: 's-red', 'stroke-width': 6, 'stroke-linecap': 'round'}, play);
  // rim-height guide (breakdown beat 2)
  const rimLine = S('g', {opacity: 0}, play);
  S('line', {x1: 40, x2: hoopX - rimR - 10, y1: rimY, y2: rimY, stroke: 'var(--ink)', 'stroke-width': 2.5, 'stroke-dasharray': '10 10'}, rimLine);
  T(rimLine, 44, rimY - 14, 'rim height', 'k', 22).style.fill = 'var(--ink)';
  const driver = figure(play, 'opp', k); driver.g.setAttribute('opacity', .9);
  const ghosts = [0, 1, 2].map(() => { const gh = figureReal(play, 'phi', k, C.number, C.build); gh.g.style.opacity = 0; return gh; }).reverse();
  const wemby = figureReal(play, 'phi', k, C.number, C.build);
  const waves = [0, 1, 2].map(() => S('circle', {r: 0, fill: 'none', stroke: 'var(--ink)', 'stroke-width': 5, opacity: 0}, play));
  const shards = Array.from({length: 10}, (_, i) => ({a: (i / 10) * Math.PI * 2 + .3, n: S('line', {stroke: ACC, 'stroke-width': 5, 'stroke-linecap': 'round', opacity: 0}, play)}));
  const btrail = S('path', {fill: 'none', stroke: 'var(--ink)', 'stroke-width': 5, 'stroke-linecap': 'round', opacity: 0, filter: 'url(#glow)'}, play);
  const ballG = S('g', {}, play);
  S('circle', {r: 13 * k, class: 'f-ink', filter: 'url(#glow)'}, ballG);
  const seam = S('path', {d: `M${-13 * k} 0L${13 * k} 0M0 ${-13 * k}Q${7 * k} 0 0 ${13 * k}`, stroke: 'rgba(17,18,20,.55)', 'stroke-width': 2.4, fill: 'none'}, ballG);
  const stampG = S('g', {opacity: 0}, top);
  const st1 = T(stampG, W / 2, floor + 170, 'DENIED', 'd', 132, 'middle'); st1.style.fill = ACC;
  T(stampG, W / 2, floor + 240, 'by Wemby', 'd', 52, 'middle');
  const cap = C.steps.map((s, i) => { const g = S('g', {opacity: 0}, top); const n = T(g, M, floor + 150, `${i + 1}`, 'd', 64); n.style.fill = ACC; T(g, M + 62, floor + 150, s[0], 'd', 54); T(g, M, floor + 212, s[1], 'b m', 36); return g; });
  T(top, M, H - 56, 'Original illustration · not traced from footage, not to scale', 'b m', 22);

  // ---- the play, as a function of play-time pt ----
  const dx0 = 250, dxG = 540, tG = 1.4, tJ = 1.58, tB = 1.95;
  const wx0 = 60, wxL = 390, tW0 = 0.3, tWL = 1.62;
  const driverAt = (pt) => {
    if (pt < tG) { const x = lerp(dx0, dxG, clamp(pt / tG)); const c = Math.sin(pt * 10) * .5 + .5; return [mixPose(POSES.run1, POSES.run2, c), x, 0]; }
    if (pt < tJ) return [mixPose(POSES.run1, POSES.gather, prog(pt, tG, .15)), dxG + 20 * prog(pt, tG, .18), 0];
    if (pt < tB + .02) { const u = clamp((pt - tJ) / (tB - tJ)); return [mixPose(POSES.gather, POSES.float, ease(u)), dxG + 20 + 30 * u, 44 * Math.sin(Math.PI / 2 * u)]; }
    const d = clamp((pt - tB) / .5); return [mixPose(POSES.float, POSES.stumble, ease(d)), dxG + 50 + 20 * d, 44 * (1 - d * d)];
  };
  const wembyAt = (pt) => {
    if (pt < tW0) return [POSES.stride1, wx0, 0];
    if (pt < tWL) { const u = clamp((pt - tW0) / (tWL - tW0)); const x = lerp(wx0, wxL, u); const c = Math.sin((pt - tW0) * 6.5) * .5 + .5; return [mixPose(POSES.stride1, POSES.stride2, c), x, 0]; }
    if (pt < tWL + .1) return [mixPose(POSES.stride1, POSES.load, prog(pt, tWL, .1)), wxL + 10 * prog(pt, tWL, .1), 0];
    if (pt < tB) { const u = clamp((pt - tWL - .1) / (tB - tWL - .1)); return [mixPose(POSES.load, POSES.block, ease(u)), wxL + 10 + 40 * u, 120 * Math.sin(Math.PI / 2 * u)]; }
    const d = clamp((pt - tB - .05) / .5); return [mixPose(POSES.block, POSES.wland, ease(d)), wxL + 50 + 20 * d, 120 * (1 - d * d)];
  };
  const HIT = .14; // hit-stop: the ball stops dead for a beat
  let hitPt = null;
  const drawPlay = (pt, slow) => {
    const frozen = pt > tB && pt < tB + HIT; const fpt = frozen ? tB : pt > tB ? pt - HIT : pt;
    const [dp, dx, dl] = driverAt(fpt), [wp, wx, wl] = wembyAt(fpt);
    const strides = fpt > tW0 && fpt < tWL + .1;
    ghosts.forEach((gh, i) => { if (!strides) { gh.g.style.opacity = 0; return; } const [gp, gx, gl] = wembyAt(fpt - (i + 1) * .06); gh.draw(gp, gx, floor - gl * k, k, 1); gh.g.style.opacity = (.34 - i * .1).toFixed(2); });
    const ad = driver.draw(dp, dx, floor - dl * k, k, 1);
    const aw = wemby.draw(wp, wx, floor - wl * k, k, 1);
    // ball: dribbled, carried up for the layup, met by Wemby's hand, then sent back the other way
    let bx, by, spin = 0;
    const hit = (() => { const [p1, x1, l1] = wembyAt(tB); const a = wemby.draw(p1, x1, floor - l1 * k, k, 1); return a('rh'); })();
    wemby.draw(wp, wx, floor - wl * k, k, 1);
    if (fpt < tG) { const h = ad('rh'); const ph = (fpt * 3.2) % 1, f = ph < .5 ? ph * 2 : (1 - ph) * 2; bx = h[0] + 8 * k; by = lerp(h[1], floor - 13 * k, f * f * (3 - 2 * f)); }
    else if (fpt < tB - .08) { const h = ad('rh'); bx = h[0] + 4 * k; by = h[1] - 12 * k; }
    else if (fpt <= tB) { const h = ad('rh'); const u = clamp((fpt - (tB - .08)) / .08); bx = lerp(h[0] + 4 * k, hit[0] + 6 * k, u); by = lerp(h[1] - 12 * k, hit[1] - 6 * k, u); }
    else { const a = fpt - tB; bx = hit[0] - 1500 * a; by = hit[1] - 160 * a + 900 * a * a; spin = a * 1400; }
    ballG.setAttribute('transform', `translate(${bx.toFixed(1)} ${by.toFixed(1)})`); seam.setAttribute('transform', `rotate(${spin.toFixed(0)})`);
    const after = fpt - tB;
    btrail.setAttribute('d', after > 0 ? 'M' + Array.from({length: 16}, (_, i) => { const a = Math.max(0, after - i * .012); return `${(hit[0] - 1500 * a).toFixed(1)} ${(hit[1] - 160 * a + 900 * a * a).toFixed(1)}`; }).join('L') : 'M0 0');
    btrail.setAttribute('opacity', after > 0 && after < .5 ? .8 : 0);
    // impact: shockwave rings, shards, a shake
    const imp = pt - tB;
    waves.forEach((w, i) => { const a = (imp - i * .06) / .5; if (imp < 0 || a < 0 || a > 1) { w.setAttribute('opacity', 0); return; } w.setAttribute('cx', hit[0]); w.setAttribute('cy', hit[1]); w.setAttribute('r', 20 + 120 * ease(a)); w.setAttribute('opacity', (1 - a).toFixed(2)); });
    shards.forEach((s, i) => { const a = imp / .4; if (imp < 0 || a > 1) { s.n.setAttribute('opacity', 0); return; } const r0 = 30 + 90 * ease(a), r1 = r0 + 34 * (1 - a); s.n.setAttribute('x1', hit[0] + Math.cos(s.a) * r0); s.n.setAttribute('y1', hit[1] + Math.sin(s.a) * r0); s.n.setAttribute('x2', hit[0] + Math.cos(s.a) * r1); s.n.setAttribute('y2', hit[1] + Math.sin(s.a) * r1); s.n.setAttribute('opacity', (1 - a).toFixed(2)); });
    const sh = imp > 0 && imp < .35 ? 14 * (1 - imp / .35) : 0;
    play.setAttribute('transform', sh ? `translate(${(Math.sin(imp * 90) * sh).toFixed(1)} ${(Math.cos(imp * 70) * sh * .6).toFixed(1)})` : '');
    slowTag.setAttribute('opacity', slow ? 1 : 0);
    return imp;
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

  const render = (t) => {
    let pt = Math.max(0, Math.min(PLAY, t - P0)), slow = false, step = -1;
    if (t >= B0) { pt = SEGS[SEGS.length - 1][1]; segT.forEach(([s0, s1, a, sp], i) => { if (t >= s0 && t < s1) { pt = a + (t - s0) * sp; slow = true; step = i; } }); }
    const imp = drawPlay(pt, slow);
    rimLine.setAttribute('opacity', step === 1 ? 1 : 0);
    stampG.setAttribute('opacity', imp > .05 && t < B0 ? prog(pt, tB + .05, .15) : 0);
    stampG.setAttribute('transform', `translate(${W / 2} ${floor + 170}) scale(${imp > .05 ? 1 + .3 * (1 - prog(pt, tB + .05, .2)) : 1}) translate(${-W / 2} ${-floor - 170})`);
    cap.forEach((g, i) => g.setAttribute('opacity', i === step ? 1 : 0));
    endc.setAttribute('opacity', t >= END0 ? prog(t, END0, .35) : 0);
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
out = out.replace('__TITLE__', html.escape(CFG['hook'][0])).replace('__ARIA__', html.escape(CFG['aria'])).replace('__CFG__', json.dumps(CFG, ensure_ascii=False))
dst = os.path.join(ROOT, 'src', 'anim', CFG['out'])
open(dst, 'w').write(out)
print('wrote', os.path.relpath(dst, ROOT))
