"""Signature move: LeBron James' power drive ("Freight Train"): downhill, through contact, the dunk, the shoulder-roll flex.
Usage (from the repo root): python3 kit/make_drive.py [kit/moves/lebron-freight-train.json] -> src/anim/<out>
Then: bash kit/short_mp4.sh src/anim/<out> kit/out/<name>.mp4 1
Order: the drive at full speed (downhill, the help defender bounces off, two-hand hammer dunk, the shoulder-roll flex),
a slow breakdown with three numbered beats, then the end card. Original illustration, not traced, not to scale."""
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
CFG = json.load(open(sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'moves', 'lebron-freight-train.json')))
PAL = team_palette(CFG['team'])
KIT = CFG['kit']
KITCSS = f".fig-kit-phi{{stroke:{KIT['jersey']};fill:{KIT['jersey']}}}\n.fig-num{{fill:{KIT['number']}}}\n.fig-band{{stroke:{KIT['number']}}}"

BODY = r"""
  // LeBron poses (facing right)
  POSES.shoulder = {head: [30, -202], neck: [22, -180], hip: [0, -118], lk: [34, -62], lf: [52, 0], rk: [-26, -60], rf: [-48, -8], le: [40, -144], lh: [58, -156], re: [18, -160], rh: [36, -132]};
  POSES.load2 = {head: [20, -196], neck: [14, -172], hip: [-6, -100], lk: [24, -54], lf: [14, 0], rk: [-6, -54], rf: [-22, 0], le: [28, -150], lh: [44, -164], re: [24, -156], rh: [42, -170]};
  POSES.cock = {head: [8, -240], neck: [4, -216], hip: [-2, -136], lk: [24, -98], lf: [14, -50], rk: [-12, -82], rf: [-28, -30], le: [24, -200], lh: [40, -218], re: [-8, -258], rh: [-4, -298]};
  POSES.slam = {head: [16, -236], neck: [10, -212], hip: [0, -134], lk: [18, -86], lf: [10, -36], rk: [-10, -78], rf: [-24, -26], le: [34, -262], lh: [62, -290], re: [38, -264], rh: [66, -294]};
  POSES.flexA = {head: [6, -228], neck: [3, -204], hip: [0, -124], lk: [14, -62], lf: [22, 0], rk: [-14, -62], rf: [-24, 0], le: [-46, -204], lh: [-30, -244], re: [50, -204], rh: [34, -244]};
  POSES.flexB = {head: [10, -224], neck: [6, -198], hip: [0, -122], lk: [14, -60], lf: [22, 0], rk: [-14, -60], rf: [-24, 0], le: [-42, -222], lh: [-26, -258], re: [48, -192], rh: [36, -230]};
  POSES.knocked = {head: [-34, -206], neck: [-28, -184], hip: [-6, -116], lk: [14, -60], lf: [20, 0], rk: [-22, -58], rf: [-38, 0], le: [-50, -176], lh: [-70, -190], re: [8, -176], rh: [26, -196]};
  POSES.seated = {head: [-24, -124], neck: [-18, -102], hip: [-10, -40], lk: [22, -46], lf: [44, 0], rk: [14, -40], rf: [36, -4], le: [-30, -72], lh: [-46, -26], re: [0, -80], rh: [-20, -30]};

  const svg = document.getElementById('sv');
  const W = 900, H = 1600, M = 56, k = 1.32, ACC = C.accent;
  const floor = 1180, hoopX = W - M - 24, rimY = floor - 240 * k * 1.62, rimR = 30 * k;
  const TOTAL = 19.5;
  const P0 = 0.5, PLAY = 5.4, B0 = 6.2;
  const SEGS = [[0.2, 1.3, 0.45], [1.3, 2.5, 0.3], [2.75, 4.9, 0.9]];
  const segT = []; let acc = B0; SEGS.forEach(([a, b, sp]) => { segT.push([acc, acc + (b - a) / sp, a, sp]); acc += (b - a) / sp; });
  const B_END = acc, END0 = B_END + 1.0;

  const defs = S('defs', {}, svg);
  const glow = S('filter', {id: 'glow', x: '-50%', y: '-50%', width: '200%', height: '200%'}, defs);
  S('feGaussianBlur', {stdDeviation: 6, result: 'b'}, glow);
  const mg = S('feMerge', {}, glow); S('feMergeNode', {in: 'b'}, mg); S('feMergeNode', {in: 'SourceGraphic'}, mg);

  const top = S('g', {}, svg);
  T(top, M, 92, C.kicker, 'k', 26);
  T(top, M, 196, C.hook[0], 'd', 92);
  T(top, M, 256, C.hook[1], 'b m', 40);
  const slowTag = S('g', {opacity: 0}, top);
  S('rect', {x: W - M - 250, y: 300, width: 250, height: 52, rx: 26, fill: 'none', stroke: 'var(--red)', 'stroke-width': 2.5}, slowTag);
  T(slowTag, W - M - 125, 335, 'SLOW MOTION', 'k', 24, 'middle').style.fill = 'var(--red)';
  const play = S('g', {}, svg);
  const court = S('g', {class: 's-silver', 'stroke-width': 3, 'stroke-linecap': 'round', opacity: .9}, play);
  S('line', {x1: -40, x2: W + 40, y1: floor, y2: floor}, court);
  S('line', {x1: hoopX + 40 * k, x2: hoopX + 40 * k, y1: rimY - 120 * k, y2: floor + 40}, court);
  const board = S('rect', {x: hoopX + 26 * k, y: rimY - 150 * k, width: 12 * k, height: 170 * k, rx: 3, fill: 'var(--silver)'}, play);
  const net = S('g', {class: 's-silver', 'stroke-width': 2.4, opacity: .85}, play);
  const netL = Array.from({length: 5}, () => S('line', {}, net));
  const drawNet = (snap) => netL.forEach((l, i) => { const L = 44 * k * (1 + .6 * snap), tp = hoopX - rimR + i * rimR / 2, bt = hoopX - rimR * (.55 - .18 * snap) + i * rimR * (1.1 - .36 * snap) / 4; l.setAttribute('x1', tp); l.setAttribute('y1', rimY); l.setAttribute('x2', bt); l.setAttribute('y2', rimY + L); });
  const rim = S('line', {x1: hoopX - rimR, x2: hoopX + 26 * k, y1: rimY, y2: rimY, class: 's-red', 'stroke-width': 6, 'stroke-linecap': 'round'}, play);
  // speed lines behind the drive, and dust where he plants
  const speed = Array.from({length: 7}, (_, i) => S('line', {stroke: 'var(--ink)', 'stroke-width': 4, 'stroke-linecap': 'round', opacity: 0}, play));
  const defender = figure(play, 'opp', k); defender.g.setAttribute('opacity', .9);
  const ghosts = [0, 1, 2].map(() => { const gh = figureReal(play, 'phi', k, C.number, C.build); gh.g.style.opacity = 0; return gh; }).reverse();
  const pulses = [0, 1, 2].map(() => S('circle', {r: 0, fill: 'none', stroke: ACC, 'stroke-width': 5, opacity: 0}, play));
  const bron = figureReal(play, 'phi', k, C.number, C.build);
  const hitW = [0, 1].map(() => S('circle', {r: 0, fill: 'none', stroke: 'var(--ink)', 'stroke-width': 5, opacity: 0}, play));
  const rings = [0, 1, 2].map(() => S('ellipse', {cx: hoopX, cy: rimY + 4, rx: 0, ry: 0, fill: 'none', stroke: ACC, 'stroke-width': 4, opacity: 0}, play));
  const ballG = S('g', {}, play);
  S('circle', {r: 13 * k, class: 'f-ink', filter: 'url(#glow)'}, ballG);
  S('path', {d: `M${-13 * k} 0L${13 * k} 0M0 ${-13 * k}Q${7 * k} 0 0 ${13 * k}`, stroke: 'rgba(17,18,20,.55)', 'stroke-width': 2.4, fill: 'none'}, ballG);
  const stampG = S('g', {opacity: 0}, top);
  const st1 = T(stampG, W / 2, floor + 170, 'FLEX', 'd', 140, 'middle'); st1.style.fill = ACC;
  T(stampG, W / 2, floor + 236, 'The King, in motion', 'd', 46, 'middle');
  const cap = C.steps.map((s, i) => { const g = S('g', {opacity: 0}, top); const n = T(g, M, floor + 150, `${i + 1}`, 'd', 64); n.style.fill = ACC; T(g, M + 62, floor + 150, s[0], 'd', 54); T(g, M, floor + 212, s[1], 'b m', 36); return g; });
  T(top, M, H - 56, 'Original illustration · not traced from footage, not to scale', 'b m', 22);

  // ---- the play, as a function of play-time pt ----
  const x0 = 60, xC = hoopX - 330 * k / 1.32, tC = 1.25, tJ = 1.55, tD = 2.05, tL = 2.45, tF = 2.8;
  const dx0 = xC + 70;
  const bronAt = (pt) => {
    if (pt < tC) { const u = clamp(pt / tC); const x = lerp(x0, xC, u * (2 - u) * .55 + u * .45); const c = Math.sin(pt * 8.5) * .5 + .5; return [mixPose(POSES.run1, POSES.run2, c), x, 0]; }
    if (pt < tC + .15) return [mixPose(POSES.run1, POSES.shoulder, prog(pt, tC - .05, .12)), xC + 20 * prog(pt, tC, .15), 0];
    if (pt < tJ) return [mixPose(POSES.shoulder, POSES.load2, prog(pt, tC + .15, .15)), xC + 20 + 30 * prog(pt, tC + .15, .15), 0];
    if (pt < tD) { const u = clamp((pt - tJ) / (tD - tJ)); const pose = u < .7 ? mixPose(POSES.load2, POSES.cock, ease(u / .7)) : mixPose(POSES.cock, POSES.slam, ease((u - .7) / .3)); return [pose, lerp(xC + 50, hoopX - 165, ease(u)), 120 * Math.sin(Math.PI / 2 * Math.min(1, u * 1.15))]; }
    if (pt < tL) { const d = clamp((pt - tD) / (tL - tD)); return [mixPose(POSES.slam, POSES.land, ease(d)), hoopX - 165 - 20 * d, 120 * (1 - d * d)]; }
    if (pt < tF) return [mixPose(POSES.land, POSES.flexA, prog(pt, tL, .3)), hoopX - 185 - 60 * prog(pt, tL, .35), 0];
    const r = (pt - tF) * 5.2; const c = Math.sin(r) * .5 + .5; // the shoulder roll
    return [mixPose(POSES.flexA, POSES.flexB, c), hoopX - 245, 4 * Math.sin(r * 2)];
  };
  const defAt = (pt) => {
    if (pt < tC - .05) return [POSES.guard, dx0 + 40 * (1 - prog(pt, .3, .8)), 0];
    if (pt < tC + .45) { const u = prog(pt, tC - .05, .5); return [mixPose(POSES.guard, POSES.knocked, ease(Math.min(1, u * 2))), dx0 + 150 * ease(u), 0]; }
    const d = prog(pt, tC + .45, .4); return [mixPose(POSES.knocked, POSES.seated, ease(d)), dx0 + 150 + 30 * d, 0];
  };
  const drawPlay = (pt, slow) => {
    const [bp, bx, bl] = bronAt(pt), [dp, dx, dl] = defAt(pt);
    const driving = pt > .25 && pt < tC + .1;
    ghosts.forEach((gh, i) => { if (!driving) { gh.g.style.opacity = 0; return; } const [gp, gx, gl] = bronAt(pt - (i + 1) * .06); gh.draw(gp, gx, floor - gl * k, k, 1); gh.g.style.opacity = (.34 - i * .1).toFixed(2); });
    speed.forEach((s, i) => { if (!driving) { s.setAttribute('opacity', 0); return; } const y = floor - (40 + i * 34) * k, len = 60 + (i * 37) % 70, ph = ((pt * 3 + i * .37) % 1); s.setAttribute('x1', bx - 60 - ph * 160); s.setAttribute('x2', bx - 60 - ph * 160 - len); s.setAttribute('y1', y); s.setAttribute('y2', y); s.setAttribute('opacity', (.5 * (1 - ph)).toFixed(2)); });
    defender.draw(dp, dx, floor - dl * k, k, -1);
    const ab = bron.draw(bp, bx, floor - bl * k, k, 1);
    // ball: dribbled on the drive, tucked through contact, cocked back, hammered through
    let x, y;
    if (pt < tC) { const h = ab('rh'); const ph = (pt * 3.4) % 1, f = ph < .5 ? ph * 2 : (1 - ph) * 2; x = h[0] + 8 * k; y = lerp(h[1], floor - 13 * k, f * f * (3 - 2 * f)); }
    else if (pt < tJ) { const h = ab('lh'); x = h[0] + 4 * k; y = h[1] - 6 * k; }
    else if (pt < tD) { const h = ab('rh'); const u = prog(pt, tD - .14, .14); x = lerp(h[0], hoopX - 6, u); y = lerp(h[1] - 12 * k, rimY - 10, u); }
    else { const d = clamp((pt - tD) / .55); x = hoopX - 6; y = lerp(rimY - 4, floor - 13 * k, d * d); }
    ballG.setAttribute('transform', `translate(${x.toFixed(1)} ${y.toFixed(1)})`);
    // contact: a hit wave where the shoulders meet
    const ci = pt - tC;
    hitW.forEach((w, i) => { const a = (ci - i * .07) / .45; if (ci < 0 || a < 0 || a > 1) { w.setAttribute('opacity', 0); return; } w.setAttribute('cx', (bx + dx) / 2); w.setAttribute('cy', floor - 170 * k); w.setAttribute('r', 16 + 110 * ease(a)); w.setAttribute('opacity', (1 - a).toFixed(2)); });
    // the dunk: rim bends, board shakes, net snaps, rings off the rim
    const di = pt - tD;
    const bend = di > 0 && di < .5 ? 14 * Math.sin(Math.PI * di / .5) * (1 - di / .5) : 0;
    rim.setAttribute('transform', `rotate(${bend.toFixed(1)} ${hoopX + 26 * k} ${rimY})`);
    board.setAttribute('transform', di > 0 && di < .4 ? `translate(${(Math.sin(di * 80) * 4 * (1 - di / .4)).toFixed(1)} 0)` : '');
    drawNet(di > 0 ? (di < .45 ? Math.sin(Math.PI * di / .45) : 0) : 0);
    rings.forEach((r, i) => { const a = di - i * .12; if (a < 0 || a > 1) { r.setAttribute('opacity', 0); return; } const e = ease(a); r.setAttribute('rx', rimR + 160 * e); r.setAttribute('ry', 10 + 40 * e); r.setAttribute('opacity', (1 - a).toFixed(2)); });
    const sh = (ci > 0 && ci < .25 ? 10 * (1 - ci / .25) : 0) + (di > 0 && di < .3 ? 16 * (1 - di / .3) : 0);
    play.setAttribute('transform', sh ? `translate(${(Math.sin(pt * 90) * sh).toFixed(1)} ${(Math.cos(pt * 70) * sh * .6).toFixed(1)})` : '');
    // the flex: pulses off him on every roll of the shoulders
    const fi = pt - tF;
    pulses.forEach((p, i) => { if (fi < 0) { p.setAttribute('opacity', 0); return; } const a = ((fi * 1.2 + i / 3) % 1); p.setAttribute('cx', bx); p.setAttribute('cy', floor - 200 * k); p.setAttribute('r', 60 + 200 * a); p.setAttribute('opacity', (.7 * (1 - a) * prog(pt, tF, .3)).toFixed(2)); });
    slowTag.setAttribute('opacity', slow ? 1 : 0);
    return fi;
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
  T(endc, W / 2, 1010, 'Signature moves at boxandmotion.com', 'b', 36, 'middle');
  T(endc, W / 2, 1070, 'Follow for every game, in motion', 'b m', 32, 'middle');

  const render = (t) => {
    let pt = Math.max(0, Math.min(PLAY, t - P0)), slow = false, step = -1;
    if (t >= B0) { pt = SEGS[SEGS.length - 1][1]; segT.forEach(([s0, s1, a, sp], i) => { if (t >= s0 && t < s1) { pt = a + (t - s0) * sp; slow = sp < .8; step = i; } }); }
    const fi = drawPlay(pt, slow);
    stampG.setAttribute('opacity', fi > .1 && t < B0 ? prog(pt, tF + .1, .2) : 0);
    stampG.setAttribute('transform', `translate(${W / 2} ${floor + 170}) scale(${1 + .04 * Math.sin(Math.max(0, fi) * 10.4)}) translate(${-W / 2} ${-floor - 170})`);
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
