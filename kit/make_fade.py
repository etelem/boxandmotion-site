"""Build a one-legged fadeaway animation for a player's scouting report from a move config.
Usage (from the repo root): python3 kit/make_fade.py kit/moves/<id>.json  ->  src/anim/<out>
Config: out, team, number, name, title, build {tall, ape, mass, ...look keys if approved}, kit {jersey, number}, steps
[[n, title, line] x3], aria, sub (optional dated line under the title in the Short), kicker (optional).
Modeled on make_pullup.py / make_stepback.py: same figure, palette, controls, ?short=1 and ?embed=1 modes, window.__A,
reduced motion, height postMessage.
The move: back to the basket on the block, two bumps to win a sliver of space, a pivot on the right foot to face up,
then a fadeaway off the left foot with the right knee up, falling away from the rim. His trait motion is his length:
at the release a dashed line marks the defender's highest reach and another his release point, labelled "Out of reach".
An original drawn illustration, not traced from footage and not to scale."""
import os, sys, json
import html as _h
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from make_reel import team_palette
base = open(os.path.join(HERE, 'base-reel.html')).read().split('\n')
start = next(i for i, l in enumerate(base) if l.startswith('  const POSES = {'))
end = next(i for i in range(start, len(base)) if base[i] == '  }' and i > start + 12)
FIGURE = '\n'.join(base[start:end + 1])
FIGURE_REAL = open(os.path.join(HERE, 'figure-real.js')).read()
CFG = json.load(open(sys.argv[1]))
BUILD = CFG['build']
PAL = team_palette(CFG['team'])
# page head, CSS and controls are shared with the step-back report so every scouting-report animation looks the same
sb = open(os.path.join(HERE, 'make_stepback.py')).read()
HEAD = sb[sb.index('HTML = r"""') + 11: sb.index('__FIGURE__\n') + len('__FIGURE__\n')]

BODY = r"""  // back to the basket on the block, leaning into his man, ball held high at the chest (x is forward = away from the rim)
  POSES.post = {head: [-14, -214], neck: [-12, -190], hip: [-4, -112], lk: [22, -62], lf: [30, 0], rk: [-30, -60], rf: [-40, 0], le: [14, -164], lh: [30, -176], re: [20, -160], rh: [34, -170]};
  // the bump: hips and shoulders driven back into the defender
  POSES.bump = {head: [-26, -208], neck: [-22, -186], hip: [-14, -110], lk: [18, -60], lf: [30, 0], rk: [-36, -58], rf: [-40, 0], le: [10, -162], lh: [26, -174], re: [16, -158], rh: [30, -168]};
  // mid-pivot on the right foot, ball up by the head
  POSES.turn = {head: [0, -226], neck: [0, -202], hip: [0, -120], lk: [10, -64], lf: [16, 0], rk: [-12, -62], rf: [-18, 0], le: [14, -196], lh: [18, -228], re: [-6, -194], rh: [-2, -230]};
  // facing the rim now, gathered on the left foot, ball high
  POSES.gather = {head: [-6, -212], neck: [-6, -188], hip: [-6, -110], lk: [-14, -60], lf: [-20, 0], rk: [20, -62], rf: [22, -4], le: [8, -196], lh: [16, -232], re: [0, -194], rh: [10, -234]};
  // the fade: off the left foot, right knee up, chest falling back, ball released at the top of his arms
  POSES.fade = {head: [-30, -236], neck: [-26, -212], hip: [-8, -130], lk: [-10, -70], lf: [-18, -4], rk: [26, -104], rf: [24, -52], le: [-8, -266], lh: [6, -318], re: [-16, -264], rh: [-2, -322]};
  POSES.land = {head: [-10, -214], neck: [-10, -190], hip: [-6, -114], lk: [-4, -60], lf: [-10, 0], rk: [20, -80], rf: [24, -30], le: [-4, -250], lh: [8, -292], re: [-12, -248], rh: [2, -296]};
  POSES.stand = {head: [0, -224], neck: [0, -200], hip: [0, -118], lk: [8, -62], lf: [10, 0], rk: [-8, -62], rf: [-12, 0], le: [14, -160], lh: [18, -112], re: [-12, -160], rh: [-16, -112]};
  // the defender at his back: chest into him, arms up
  POSES.wall = {head: [6, -226], neck: [4, -202], hip: [-4, -124], lk: [-18, -66], lf: [-30, 0], rk: [18, -66], rf: [26, 0], le: [22, -186], lh: [36, -200], re: [26, -176], rh: [40, -186]};
__FIGURE_REAL__
  const BUILD = __BUILD__;
  const svg = document.getElementById('sv');
  const steps = __STEPS__;
  const TOTAL = 6.0;                                  // one pass of the move (site loop)
  const t = {b1: .3, b2: .85, turn: 1.4, fade: 1.86, rel: 2.26, land: 2.76, make: 3.1};
  // the Short: full speed once, then a slow breakdown of the three beats with their captions
  const P_END = 4.1, B0 = 4.3, SEGS = [[0.2, 1.42, .45], [1.36, 1.92, .32], [1.86, 3.4, .5]];
  const segT = []; { let acc = B0; SEGS.forEach(([a, b, sp]) => { segT.push([acc, acc + (b - a) / sp, a, sp]); acc += (b - a) / sp; }); }
  const S_CUT = segT[segT.length - 1][1] + .55, S_TOTAL = S_CUT + .2;
  let L = null, built = null;

  const short = /[?&]short=1/.test(location.search);
  if (short) document.documentElement.classList.add('short');
  function build() {
    const portrait = short || (svg.clientWidth > 0 && svg.clientWidth < 620);
    const W = short ? 900 : portrait ? 800 : 1280, H = short ? 1600 : portrait ? 980 : 760, M = short ? 56 : portrait ? 44 : 56;
    svg.setAttribute('viewBox', `0 0 ${W} ${H}`); svg.replaceChildren();
    const defs = S('defs', {}, svg);
    const glow = S('filter', {id: 'glow', x: '-50%', y: '-50%', width: '200%', height: '200%'}, defs);
    S('feGaussianBlur', {stdDeviation: 6, result: 'b'}, glow);
    const mg = S('feMerge', {}, glow); S('feMergeNode', {in: 'b'}, mg); S('feMergeNode', {in: 'SourceGraphic'}, mg);
    const k = short ? 1.2 : portrait ? .92 : 1.0;
    const floor = short ? H - 520 : portrait ? H - 290 : H - 190;
    const hoopX = W - M - (short ? 10 : portrait ? 20 : 60);
    const rimY = floor - 240 * k * 1.62, rimR = 30 * k;
    // he catches on the block, backs down two bumps, pivots, then fades back toward the left
    const xP0 = hoopX - (short ? 360 : portrait ? 360 : 400) * k, bumpD = 18 * k, xP2 = xP0 + 2 * bumpD, fadeD = 72 * k;
    const dOff = 66 * k;                              // the defender, chest to his back
    const hy = short ? 100 : M + 6;
    const kSize = short ? 28 : portrait ? 22 : 18, kNode = T(svg, M, hy, __KICKERJS__, 'k', kSize);
    const fitK = () => { kNode.style.fontSize = kSize + 'px'; const w = kNode.getComputedTextLength(), max = W - 2 * M; if (w > max) kNode.style.fontSize = (kSize * max / w).toFixed(2) + 'px'; };
    fitK(); if (document.fonts && document.fonts.ready) document.fonts.ready.then(fitK);
    T(svg, M, hy + (short ? 76 : portrait ? 56 : 48), __TITLEJS__, 'd', short ? 68 : portrait ? 52 : 44);
    if (short && __SUBJS__) T(svg, M, hy + 128, __SUBJS__, 'b', 34).style.fontWeight = 600;
    if (short) { T(svg, M, H - 70, 'BOX & MOTION HOOPS', 'd', 36); T(svg, W - M, H - 70, 'boxandmotion.com', 'b m', 28, 'end'); }
    const slowTag = S('g', {opacity: 0}, svg);
    if (short) { S('rect', {x: W - M - 250, y: hy + 160, width: 250, height: 52, rx: 26, fill: 'none', stroke: 'var(--red)', 'stroke-width': 2.5}, slowTag); T(slowTag, W - M - 125, hy + 195, 'SLOW MOTION', 'k', 24, 'middle').style.fill = 'var(--red)'; }
    // court: the floor line, the stanchion, board, rim and net
    const court = S('g', {class: 's-silver', 'stroke-width': 3, 'stroke-linecap': 'round', opacity: .9}, svg);
    S('line', {x1: M - 30, x2: W + 30, y1: floor, y2: floor, opacity: .5}, court);
    S('line', {x1: hoopX + 40 * k, x2: hoopX + 40 * k, y1: rimY - 120 * k, y2: floor}, court);
    S('rect', {x: hoopX + 26 * k, y: rimY - 150 * k, width: 12 * k, height: 170 * k, rx: 3, fill: 'var(--silver)'}, svg);
    S('line', {x1: hoopX - rimR, x2: hoopX + 26 * k, y1: rimY, y2: rimY, class: 's-red', 'stroke-width': 6, 'stroke-linecap': 'round'}, svg);
    const net = S('g', {class: 's-silver', 'stroke-width': 2, opacity: .8}, svg);
    const netL = Array.from({length: 5}, () => S('line', {}, net));
    const drawNet = (snap) => netL.forEach((l, i) => { const Ln = 44 * k * (1 + .55 * snap), tp = hoopX - rimR + i * rimR / 2, bt = hoopX - rimR * (.55 - .2 * snap) + i * rimR * (1.1 - .4 * snap) / 4; l.setAttribute('x1', tp); l.setAttribute('y1', rimY); l.setAttribute('x2', bt); l.setAttribute('y2', rimY + Ln); });
    drawNet(0);
    // the block: a short paint line under the post-up
    S('line', {x1: xP0 - 40 * k, x2: xP0 + 60 * k, y1: floor + 10, y2: floor + 10, class: 's-silver', 'stroke-width': 4, opacity: .35}, svg);
    const bumpT = T(svg, 0, 0, 'Bump', 'b', short ? 30 : portrait ? 22 : 20, 'middle'); bumpT.style.fontWeight = 700; bumpT.style.fill = 'var(--red)'; bumpT.style.opacity = 0;
    // his trait: length. Two dashed lines at the release: the defender's highest reach and where the ball leaves his hands
    const reach = S('g', {opacity: 0}, svg);
    const lnR = S('line', {stroke: 'var(--red)', 'stroke-width': 3, 'stroke-dasharray': '8 8'}, reach);
    const lnD = S('line', {class: 's-silver', 'stroke-width': 3, 'stroke-dasharray': '8 8'}, reach);
    const brk = S('line', {stroke: 'var(--red)', 'stroke-width': 3}, reach);
    const fs = short ? 28 : portrait ? 20 : 18;
    const tR = T(reach, 0, 0, 'Release', 'b', fs); tR.style.fontWeight = 700; tR.style.fill = 'var(--red)';
    const tD = T(reach, 0, 0, 'Defender', 'b m', fs);
    const tO = T(reach, 0, 0, 'Out of reach', 'd', short ? 40 : portrait ? 30 : 28, 'middle');
    // figures: afterimages of the fade, the defender, the star
    const figs = S('g', {}, svg);
    const ghosts = [0, 1].map(() => { const gh = figureReal(figs, 'phi', k, __NUM__, BUILD); gh.g.style.opacity = 0; return gh; }).reverse();
    const defender = figure(figs, 'opp', k); defender.g.setAttribute('opacity', .85);
    const star = figureReal(figs, 'phi', k, __NUM__, BUILD);
    const trailG = S('g', {}, svg);
    const ball = S('circle', {r: 13 * k, class: 'f-ink', filter: 'url(#glow)'}, svg);
    const rings = [0, 1, 2].map(() => S('ellipse', {cx: hoopX, cy: rimY + 4, rx: 0, ry: 0, fill: 'none', stroke: 'var(--blue-text)', 'stroke-width': 4, opacity: 0}, svg));
    const plus = T(svg, hoopX - rimR - 10, rimY - 64 * k, '+2', 'd', portrait ? 72 : 64, 'end');
    const cards = steps.map((s, i) => {
      const g = S('g', {class: 'step'}, svg);
      if (short) {
        const y = floor + 190;
        T(g, M, y, s[0], 'd', 64).setAttribute('fill', 'var(--red)');
        const t1 = T(g, M + 64, y - 12, s[1], 'b', 48); t1.style.fontWeight = 600;
        T(g, M + 64, y + 40, s[2], 'b m', 34);
        g.classList.add('solo');
      } else if (portrait) {
        const y = floor + 112 + i * 54;
        T(g, M, y, s[0], 'd', 34).setAttribute('fill', 'var(--red)');
        const t1 = T(g, M + 40, y, s[1], 'b', 26); t1.style.fontWeight = 600;
        T(g, M + 40 + 170, y, s[2], 'b m', 20);
      } else {
        const cw = (W - 2 * M) / 3, x = M + i * cw, y = floor + 124;
        T(g, x, y, s[0], 'd', 38).setAttribute('fill', 'var(--red)');
        const t1 = T(g, x + 38, y - 8, s[1], 'b', 23); t1.style.fontWeight = 600;
        T(g, x + 38, y + 20, s[2], 'b m', 18);
      }
      return g;
    });
    T(svg, M, short ? hy + 268 : portrait ? M + 96 : M + 84, 'Original illustration · not traced from footage, not to scale', 'b m', short ? 24 : portrait ? 18 : 15);
    built = {portrait};
    const pulse = (lt, a) => { const u = (lt - a) / .32; return u > 0 && u < 1 ? Math.sin(Math.PI * u) : 0; };
    const stepIn = (lt, a) => ease(prog(lt, a + .08, .2));
    const liftAt = (lt) => lt > t.fade && lt < t.land ? 46 * Math.sin(Math.PI * (lt - t.fade) / (t.land - t.fade)) : 0;
    // the star: [pose, x, lift, dir]
    const starAt = (lt) => {
      if (lt < t.turn) { const p = Math.max(pulse(lt, t.b1), pulse(lt, t.b2)); return [mixPose(POSES.post, POSES.bump, p), xP0 + bumpD * (stepIn(lt, t.b1) + stepIn(lt, t.b2)), 0, -1]; }
      if (lt < t.fade) {
        const u = prog(lt, t.turn, t.fade - t.turn), c = -Math.cos(Math.PI * ease(u)), dir = Math.abs(c) < .2 ? (c < 0 ? -.2 : .2) : c;
        const pose = u < .5 ? mixPose(POSES.post, POSES.turn, ease(u * 2)) : mixPose(POSES.turn, POSES.gather, ease(u * 2 - 1));
        return [pose, xP2, 0, dir];
      }
      const fx = xP2 - fadeD * ease(prog(lt, t.fade, t.land - t.fade));
      if (lt < t.rel) return [mixPose(POSES.gather, POSES.fade, ease(prog(lt, t.fade, t.rel - t.fade))), fx, liftAt(lt), 1];
      if (lt < t.land) return [mixPose(POSES.fade, POSES.land, ease(prog(lt, t.rel + .12, t.land - t.rel - .12))), fx, liftAt(lt), 1];
      return [mixPose(POSES.land, POSES.stand, ease(prog(lt, t.land + .2, .6))), fx, 0, 1];
    };
    // the defender: chest to his back, pushed back a little on each bump, then up for a late contest
    const defAt = (lt) => {
      if (lt < t.turn) { const p = Math.max(pulse(lt, t.b1), pulse(lt, t.b2)); return [POSES.wall, xP0 + dOff + bumpD * (stepIn(lt, t.b1) + stepIn(lt, t.b2)) + 8 * k * p, 0]; }
      if (lt < t.rel + .2) { const u = prog(lt, t.turn + .2, t.rel - t.turn - .1); return [mixPose(POSES.wall, POSES.contest, ease(u)), xP2 + dOff - 10 * k * ease(u), 14 * Math.sin(Math.PI * Math.min(1, prog(lt, t.fade + .05, .5)))]; }
      const b = prog(lt, t.rel + .2, .6); return [mixPose(POSES.contest, POSES.guard, ease(b)), xP2 + dOff - 10 * k, 0];
    };
    // release point, the defender's best reach, and the arc
    const [rp, rx, rl, rd] = starAt(t.rel);
    const at0 = star.draw(rp, rx, floor - rl * k, k, rd);
    const rel = [(at0('lh')[0] + at0('rh')[0]) / 2 + 4 * k, Math.min(at0('lh')[1], at0('rh')[1]) - 14 * k];
    const dAt = defender.draw(POSES.contest, xP2 + dOff - 10 * k, floor - 14 * k, k, -1);
    const defTop = Math.min(dAt('lh')[1], dAt('rh')[1]) - 6 * k;
    const lx1 = rel[0] - 60 * k, lx2 = rel[0] + 230 * k;
    lnR.setAttribute('x1', lx1); lnR.setAttribute('x2', lx2); lnR.setAttribute('y1', rel[1]); lnR.setAttribute('y2', rel[1]);
    lnD.setAttribute('x1', lx1); lnD.setAttribute('x2', lx2); lnD.setAttribute('y1', defTop); lnD.setAttribute('y2', defTop);
    brk.setAttribute('x1', lx2); brk.setAttribute('x2', lx2); brk.setAttribute('y1', rel[1]); brk.setAttribute('y2', defTop);
    tR.setAttribute('x', lx2 + 12); tR.setAttribute('y', rel[1] + fs * .35);
    tD.setAttribute('x', lx2 + 12); tD.setAttribute('y', defTop + fs * .35);
    tO.setAttribute('x', rel[0] + 130 * k); tO.setAttribute('y', (rel[1] + defTop) / 2 + (short ? 14 : 10));
    bumpT.setAttribute('x', xP0 + dOff / 2); bumpT.setAttribute('y', floor - 270 * k);
    const peak = short ? 170 : portrait ? 150 : 140;
    const arcAt = (u) => [lerp(rel[0], hoopX, u), lerp(rel[1], rimY - 6, u) - 4 * peak * u * (1 - u)];
    const trail = S('path', {d: 'M' + Array.from({length: 61}, (_, i) => arcAt(i / 60)).map(([x, y]) => `${x.toFixed(1)} ${y.toFixed(1)}`).join('L'), stroke: 'var(--blue-text)', fill: 'none', 'stroke-width': 4, 'stroke-dasharray': '0 1', pathLength: 1, opacity: .9, filter: 'url(#glow)'}, trailG);
    L = (lt, slow) => {
      const [pose, x, lift, dir] = starAt(lt), [dp, dx, dl] = defAt(lt);
      // afterimages of the fade: he falls away from the rim
      const ghosting = lt > t.fade + .05 && lt < t.land + .1;
      ghosts.forEach((gh, i) => {
        if (!ghosting) { gh.g.style.opacity = 0; return; }
        const [gp, gx, gl, gd] = starAt(Math.max(t.fade, lt - (i + 1) * .08));
        gh.draw(gp, gx, floor - gl * k, k, gd);
        gh.g.style.opacity = ((.3 - i * .1) * (1 - prog(lt, t.land - .1, .2))).toFixed(2);
      });
      defender.draw(dp, dx, floor - dl * k, k, -1);
      const at = star.draw(pose, x, floor - lift * k, k, dir);
      const fade = 1 - prog(lt, TOTAL - .7, .5);
      bumpT.style.opacity = (Math.max(pulse(lt, t.b1), pulse(lt, t.b2)) * fade).toFixed(2);
      reach.setAttribute('opacity', (prog(lt, t.rel - .08, .16) * (1 - prog(lt, t.make + .6, .4)) * fade).toFixed(2));
      // ball: held high on the post-up and the turn, released at the top of the fade
      let bx, by;
      if (lt < t.rel) { bx = (at('lh')[0] + at('rh')[0]) / 2 + dir * 8 * k; by = Math.min(at('lh')[1], at('rh')[1]) - (lt < t.turn ? 2 : 12) * k; }
      else if (lt < t.make) { const u = inout(clamp((lt - t.rel) / (t.make - t.rel))); [bx, by] = arcAt(u); trail.setAttribute('stroke-dasharray', `${u.toFixed(3)} 1`); }
      else { const d = clamp((lt - t.make) / .6); bx = hoopX - 4; by = lerp(rimY - 6, floor - 13 * k, d * d); }
      if (lt < t.rel) trail.setAttribute('stroke-dasharray', '0 1');
      trail.style.opacity = (.9 * fade).toFixed(2);
      ball.setAttribute('cx', bx); ball.setAttribute('cy', by);
      const di = lt - t.make;
      drawNet(di > 0 && di < .45 ? Math.sin(Math.PI * di / .45) : 0);
      rings.forEach((r, i) => { const a = di - i * .12; if (a < 0 || a > 1) { r.setAttribute('opacity', 0); return; } const e = ease(a); r.setAttribute('rx', rimR + 150 * e); r.setAttribute('ry', 10 + 36 * e); r.setAttribute('opacity', (1 - a).toFixed(2)); });
      plus.style.opacity = di > 0 ? prog(lt, t.make, .3) * fade : 0;
      const phase = lt < t.turn ? 0 : lt < t.fade ? 1 : 2;
      if (!short) { cards.forEach((g, i) => g.classList.toggle('on', i === phase && lt > .2)); buttons.forEach((b, i) => b.classList.toggle('on', i === phase && lt > .2)); }
      slowTag.setAttribute('opacity', slow ? 1 : 0);
    };
    window.__RS = (tt) => {
      let lt = Math.min(tt, P_END), slow = false, step = -1;
      if (tt >= B0) { lt = SEGS[SEGS.length - 1][1]; segT.forEach(([s0, s1, a, sp], i) => { if (tt >= s0 && tt < s1) { lt = a + (tt - s0) * sp; slow = true; step = i; } }); }
      L(lt, slow);
      cards.forEach((g, i) => g.classList.toggle('on', i === step));
    };
  }

"""
TAIL = r"""  const buttons = [...document.querySelectorAll('.jump')];
  const still = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  let time = still ? 2.3 : 0, playing = !still, speed = 1, last = null;
  const pp = document.getElementById('pp'), slow = document.getElementById('slow');
  pp.textContent = playing ? 'Pause' : 'Play';
  pp.onclick = () => { playing = !playing; pp.textContent = playing ? 'Pause' : 'Play'; };
  slow.onclick = () => { speed = speed === 1 ? .35 : 1; slow.setAttribute('aria-pressed', speed < 1); };
  buttons.forEach((b) => b.onclick = () => { time = +b.dataset.t; playing = true; pp.textContent = 'Pause'; });
  build();
  const R = (x) => short ? window.__RS(x) : L(x, false);
  const TT = short ? S_TOTAL : TOTAL;
  R(time);
  if ('ResizeObserver' in window) new ResizeObserver(() => { const p = svg.clientWidth < 620; if (built && built.portrait !== p && !short) { build(); R(time); } }).observe(svg);
  const frame = (now) => { if (last != null && playing) { time += (now - last) / 1000 * speed; if (time > TT) time = 0; } last = now; if (!window.__hold) R(time); requestAnimationFrame(frame); };
  requestAnimationFrame(frame);
  // Shorts open mid-drive and loop (short_frames.js adds the end card and the blend back to the first frame)
  window.__A = {render: R, build, total: TT, loop: short ? {start: 0.3, cut: S_CUT} : null};
  // tell a parent page how tall we are, so its iframe fits without scrolling
  const postH = () => { if (window.parent !== window) window.parent.postMessage({bmH: Math.ceil(document.querySelector('.wrap').getBoundingClientRect().height)}, '*'); };
  if ('ResizeObserver' in window) new ResizeObserver(postH).observe(document.body); window.addEventListener('load', postH); postH();
})();
</script>
</body></html>
"""
HTML = HEAD + BODY + TAIL
def short_title(title):
    s = title[4:] if title.startswith('The ') else title
    return s[:1].upper() + s[1:]
JUMPS = ''.join(f'<button class="jump" data-t="{t}" type="button">{n} · {_h.escape(short_title(title))}</button>' for t, (n, title, _) in zip(('0.2', '1.4', '1.86'), CFG['steps']))
KIT = CFG.get('kit') or {}
KITCSS = (f".fig-kit-phi{{stroke:{KIT['jersey']};fill:{KIT['jersey']}}}\n.fig-num{{fill:{KIT['number']}}}\n.fig-band{{stroke:{KIT['number']}}}" if KIT else '')
out = (HTML.replace('__KITCSS__', KITCSS).replace('__JUMPS__', JUMPS).replace('__NAME__', _h.escape(CFG['name'])).replace('__TITLE__', _h.escape(CFG['title']))
       .replace('__ARIA__', _h.escape(CFG['aria'])).replace('__STEPS__', json.dumps(CFG['steps'], ensure_ascii=False))
       .replace('__NAMEJS__', json.dumps(CFG['name'], ensure_ascii=False)).replace('__KICKERJS__', json.dumps(CFG.get('kicker') or 'Scouting report · ' + CFG['name'], ensure_ascii=False)).replace('__TITLEJS__', json.dumps(CFG['title'], ensure_ascii=False))
       .replace('__SUBJS__', json.dumps(CFG.get('sub') or '', ensure_ascii=False)).replace('__NUM__', json.dumps(CFG['number']))
       .replace('__PAL__', PAL).replace('__FIGURE__', FIGURE).replace('__FIGURE_REAL__', FIGURE_REAL).replace('__BUILD__', json.dumps(BUILD)))
os.makedirs(os.path.join(ROOT, 'src', 'anim'), exist_ok=True)
dst = os.path.join(ROOT, 'src', 'anim', CFG['out'])
open(dst, 'w').write(out)
print('wrote', os.path.relpath(dst, ROOT))
