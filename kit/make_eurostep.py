"""Build a Euro-step animation for a player's scouting report from a move config.
Usage (from the repo root): python3 kit/make_eurostep.py kit/moves/<id>.json  ->  src/anim/<out>
Config: out, team, number, name, title, build {tall, ape, mass, ...look keys if approved}, kit {jersey, number}, steps
[[n, title, line] x3], aria, sub (optional dated line under the title in the Short).
Modeled on make_stepback.py: same figure, palette, controls, ?short=1 mode, window.__A, reduced motion, height postMessage.
The move: drive at speed, a high two-hand gather, one long stride to one side (toward the viewer) so the help defender commits,
a second long stride back across (away from the viewer) around him, and a soft one-hand floater. Side view: the sideways
part of each stride is drawn as depth (lower on screen = nearer). His trait motion is the length of the strides: afterimages
on each stride, footprints where he plants and the zig-zag his feet trace on the floor.
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

BODY = r"""  POSES.run1 = {head: [26, -222], neck: [20, -198], hip: [0, -122], lk: [30, -70], lf: [22, 0], rk: [-20, -62], rf: [-46, -12], le: [-4, -162], lh: [6, -130], re: [36, -160], rh: [54, -110]};
  POSES.run2 = {head: [26, -222], neck: [20, -198], hip: [0, -122], lk: [-20, -62], lf: [-46, -12], rk: [30, -70], rf: [22, 0], le: [-4, -162], lh: [6, -130], re: [36, -160], rh: [54, -110]};
  // the high gather: ball picked up with both hands above the right shoulder, still moving
  POSES.gather = {head: [20, -216], neck: [14, -192], hip: [0, -118], lk: [28, -64], lf: [30, 0], rk: [-18, -60], rf: [-36, -6], le: [26, -194], lh: [36, -224], re: [32, -190], rh: [44, -226]};
  // the two long strides (left foot reaches first, then the right), ball kept high and away from the defender
  POSES.stride1 = {head: [22, -204], neck: [15, -182], hip: [0, -106], lk: [44, -56], lf: [76, 0], rk: [-32, -50], rf: [-66, -8], le: [26, -190], lh: [36, -216], re: [32, -186], rh: [44, -218]};
  POSES.stride2 = {head: [22, -204], neck: [15, -182], hip: [0, -106], lk: [-30, -50], lf: [-64, -8], rk: [46, -58], rf: [80, 0], le: [22, -192], lh: [30, -218], re: [30, -188], rh: [40, -220]};
  // the floater: off one foot, right arm extended, a soft push high over the help
  POSES.float = {head: [6, -246], neck: [2, -222], hip: [-4, -140], lk: [24, -110], lf: [16, -62], rk: [-8, -74], rf: [-12, -6], le: [14, -218], lh: [26, -232], re: [22, -266], rh: [34, -312]};
  POSES.land = {head: [0, -214], neck: [-2, -190], hip: [-6, -112], lk: [12, -60], lf: [-4, 0], rk: [16, -58], rf: [20, 0], le: [20, -170], lh: [28, -190], re: [16, -156], rh: [30, -150]};
  POSES.reach = {head: [-14, -230], neck: [-10, -206], hip: [0, -126], lk: [-18, -68], lf: [-28, 0], rk: [16, -66], rf: [26, 0], le: [-34, -220], lh: [-62, -262], re: [24, -186], rh: [40, -200]};
__FIGURE_REAL__
  const BUILD = __BUILD__;
  const svg = document.getElementById('sv');
  const steps = __STEPS__;
  const TOTAL = 6.0;                                  // one pass of the move (site loop)
  const t = {gath: 1.25, gathE: 1.55, s1: 2.1, s2: 2.68, rel: 3.02, make: 3.78};
  // the Short: full speed once, then a slow breakdown of the three beats with their captions
  const P_END = 4.5, B0 = 4.7, SEGS = [[1.05, 1.6, .38], [1.55, 2.14, .32], [2.1, 3.95, .5]];
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
    const k = short ? 1.4 : portrait ? 1.02 : 1.12;
    const floor = short ? H - 520 : portrait ? H - 290 : H - 190;
    const zy = (short ? 44 : 36) * k;               // how far one sideways stride moves him toward/away from the viewer
    const hoopX = W - M - (short ? 10 : portrait ? 20 : 60);
    const rimY = floor - 240 * k * 1.62, rimR = 30 * k;
    const xFin = hoopX - 215 * k, x2 = xFin - 22 * k, x1 = x2 - 132 * k, xG = x1 - 124 * k, x0 = short ? M - 40 : Math.max(M + 30, xG - 380 * k);
    const xD = x1 + 66 * k;
    // header
    const hy = short ? 100 : M + 6;
    T(svg, M, hy, 'Scouting report · ' + __NAMEJS__, 'k', short ? 28 : portrait ? 22 : 18);
    T(svg, M, hy + (short ? 76 : portrait ? 56 : 48), __TITLEJS__, 'd', short ? 68 : portrait ? 52 : 44);
    if (short && __SUBJS__) T(svg, M, hy + 128, __SUBJS__, 'b', 34).style.fontWeight = 600;
    if (short) { T(svg, M, H - 70, 'BOX & MOTION HOOPS', 'd', 36); T(svg, W - M, H - 70, 'boxandmotion.com', 'b m', 28, 'end'); }
    const slowTag = S('g', {opacity: 0}, svg);
    if (short) { S('rect', {x: W - M - 250, y: hy + 160, width: 250, height: 52, rx: 26, fill: 'none', stroke: 'var(--red)', 'stroke-width': 2.5}, slowTag); T(slowTag, W - M - 125, hy + 195, 'SLOW MOTION', 'k', 24, 'middle').style.fill = 'var(--red)'; }
    // court: the floor line, a faint band for the width of the lane (depth), the stanchion, board, rim and net
    S('rect', {x: M - 30, y: floor - zy - 8, width: W - M + 60, height: 2 * zy + 16, fill: 'var(--track)', opacity: .55}, svg);
    const court = S('g', {class: 's-silver', 'stroke-width': 3, 'stroke-linecap': 'round', opacity: .9}, svg);
    S('line', {x1: M - 30, x2: W + 30, y1: floor, y2: floor, opacity: .5}, court);
    S('line', {x1: hoopX + 40 * k, x2: hoopX + 40 * k, y1: rimY - 120 * k, y2: floor}, court);
    S('rect', {x: hoopX + 26 * k, y: rimY - 150 * k, width: 12 * k, height: 170 * k, rx: 3, fill: 'var(--silver)'}, svg);
    const rim = S('line', {x1: hoopX - rimR, x2: hoopX + 26 * k, y1: rimY, y2: rimY, class: 's-red', 'stroke-width': 6, 'stroke-linecap': 'round'}, svg);
    const net = S('g', {class: 's-silver', 'stroke-width': 2, opacity: .8}, svg);
    const netL = Array.from({length: 5}, () => S('line', {}, net));
    const drawNet = (snap) => netL.forEach((l, i) => { const Ln = 44 * k * (1 + .55 * snap), tp = hoopX - rimR + i * rimR / 2, bt = hoopX - rimR * (.55 - .2 * snap) + i * rimR * (1.1 - .4 * snap) / 4; l.setAttribute('x1', tp); l.setAttribute('y1', rimY); l.setAttribute('x2', bt); l.setAttribute('y2', rimY + Ln); });
    drawNet(0);
    // the zig-zag his feet trace, the two footprints and the stride label (his trait: length)
    const zig = S('path', {fill: 'none', stroke: 'var(--red)', 'stroke-width': 4, 'stroke-linecap': 'round', 'stroke-linejoin': 'round', pathLength: 1, 'stroke-dasharray': '0 1', opacity: .75}, svg);
    const pr1 = S('ellipse', {rx: 24 * k, ry: 6, class: 'f-red', opacity: 0}, svg), pr2 = S('ellipse', {rx: 24 * k, ry: 6, class: 'f-red', opacity: 0}, svg);
    const strideG = S('g', {opacity: 0}, svg);
    const strideL = S('line', {class: 's-silver', 'stroke-width': 3, 'stroke-dasharray': '6 7'}, strideG);
    const strideT = T(strideG, 0, 0, 'One long stride', 'b', short ? 30 : portrait ? 22 : 19, 'middle'); strideT.style.fontWeight = 600;
    // figures (ghosts and both players live in one layer so they can swap in front/behind as he goes around)
    const figs = S('g', {}, svg);
    const ghosts = [0, 1, 2].map(() => { const gh = figureReal(figs, 'phi', k, __NUM__, BUILD); gh.g.style.opacity = 0; return gh; }).reverse();
    const defender = figure(figs, 'opp', k); defender.g.setAttribute('opacity', .85);
    const star = figureReal(figs, 'phi', k, __NUM__, BUILD);
    const trailG = S('g', {}, svg);
    const ball = S('circle', {r: 13 * k, class: 'f-ink', filter: 'url(#glow)'}, svg);
    const rings = [0, 1, 2].map(() => S('ellipse', {cx: hoopX, cy: rimY + 4, rx: 0, ry: 0, fill: 'none', stroke: 'var(--blue-text)', 'stroke-width': 4, opacity: 0}, svg));
    const plus = T(svg, hoopX - rimR - 10, rimY - 64 * k, '+2', 'd', portrait ? 72 : 64, 'end');
    // step cards
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
    const yAt = (z) => floor + z * zy;
    // where his feet land on each stride (for the footprints and the zig-zag)
    const fp1 = star.draw(POSES.stride1, x1, yAt(1), k, 1)('lf'), fp2 = star.draw(POSES.stride2, x2, yAt(-1), k, 1)('rf');
    const fp0 = [xG + 30 * k + 20 * k, floor];
    const zigPts = [[x0 + 40 * k, floor], fp0, [fp1[0] + 8 * k, fp1[1]], [fp2[0] + 8 * k, fp2[1]], [xFin + 10 * k, yAt(-1)]];
    zig.setAttribute('d', 'M' + zigPts.map(([x, y]) => `${x.toFixed(1)} ${y.toFixed(1)}`).join('L'));
    pr1.setAttribute('cx', fp1[0] + 8 * k); pr1.setAttribute('cy', fp1[1] + 2); pr2.setAttribute('cx', fp2[0] + 8 * k); pr2.setAttribute('cy', fp2[1] + 2);
    const sy = floor + zy + (short ? 34 : 26);
    strideL.setAttribute('x1', fp1[0] + 8 * k); strideL.setAttribute('x2', fp2[0] + 8 * k); strideL.setAttribute('y1', sy - (short ? 22 : 16)); strideL.setAttribute('y2', sy - (short ? 22 : 16));
    strideT.setAttribute('x', (fp1[0] + fp2[0]) / 2 + 8 * k); strideT.setAttribute('y', sy + (short ? 12 : 6));
    // release point and the floater's arc
    const relPt = () => { const at = star.draw(POSES.float, xFin, yAt(-1) - 50 * k, k, 1); return [at('rh')[0] + 4 * k, at('rh')[1] - 12 * k]; };
    const rel = relPt();
    const peak = short ? 110 : portrait ? 90 : 60;
    const arcAt = (u) => [lerp(rel[0], hoopX, u), lerp(rel[1], rimY - 6, u) - 4 * peak * u * (1 - u)];
    const trail = S('path', {d: 'M' + Array.from({length: 61}, (_, i) => arcAt(i / 60)).map(([x, y]) => `${x.toFixed(1)} ${y.toFixed(1)}`).join('L'), stroke: 'var(--blue-text)', fill: 'none', 'stroke-width': 4, 'stroke-dasharray': '0 1', pathLength: 1, opacity: .9, filter: 'url(#glow)'}, trailG);
    built = {portrait};
    // the star: [pose, x, lift, z]
    const starAt = (lt) => {
      if (lt < t.gath) { const c = Math.sin(lt * 9) * .5 + .5; return [mixPose(POSES.run1, POSES.run2, c), lerp(x0, xG, lt / t.gath), 0, 0]; }
      if (lt < t.gathE) { const u = clamp((lt - t.gath) / (t.gathE - t.gath)); return [mixPose(POSES.run1, POSES.gather, ease(u)), xG + 30 * k * u, 0, 0]; }
      if (lt < t.s1) { const u = clamp((lt - t.gathE) / (t.s1 - t.gathE)); return [mixPose(POSES.gather, POSES.stride1, ease(u)), lerp(xG + 30 * k, x1, inout(u)), 18 * Math.sin(Math.PI * u), inout(u)]; }
      if (lt < t.s2) { const u = clamp((lt - t.s1) / (t.s2 - t.s1)); return [mixPose(POSES.stride1, POSES.stride2, inout(u)), lerp(x1, x2, inout(u)), 22 * Math.sin(Math.PI * u), lerp(1, -1, inout(u))]; }
      if (lt < t.rel + .22) { const u = clamp((lt - t.s2) / (t.rel + .22 - t.s2)); return [mixPose(POSES.stride2, POSES.float, ease(u)), lerp(x2, xFin, ease(u)), 50 * ease(u), -1]; }
      const d = clamp((lt - t.rel - .22) / .5); return [mixPose(POSES.float, POSES.land, ease(d)), xFin + 20 * k * d, 50 * (1 - d * d), -1];
    };
    // the help defender: waits in the lane, slides with the first stride (he commits), reaches back too late
    const defAt = (lt) => {
      if (lt < t.gathE) return [POSES.guard, xD + 6 * k * Math.sin(lt * 5), 0, 0];
      if (lt < t.s1 + .15) { const u = prog(lt, t.gathE + .05, t.s1 + .1 - t.gathE); return [POSES.guard, xD - 8 * k * u, 0, .85 * u]; }
      const r = prog(lt, t.s2 - .2, .35), back = prog(lt, t.make, .8);
      return [mixPose(mixPose(POSES.guard, POSES.reach, r), POSES.guard, back), xD - 8 * k, 0, .85 - .25 * back];
    };
    let front = 'star';
    L = (lt, slow) => {
      const [pose, x, lift, z] = starAt(lt), [dp, dx, dl, dz] = defAt(lt);
      // in front or behind the defender, by depth
      const want = z < dz - .05 ? 'def' : 'star';
      if (want !== front) { figs.appendChild(want === 'def' ? defender.g : star.g); front = want; }
      // afterimages on each long stride
      const striding = lt > t.gathE + .05 && lt < t.s2 + .12;
      ghosts.forEach((gh, i) => {
        if (!striding) { gh.g.style.opacity = 0; return; }
        const [gp, gx, gl, gz] = starAt(lt - (i + 1) * .07);
        gh.draw(gp, gx, yAt(gz) - gl * k, k, 1);
        gh.g.style.opacity = (.32 - i * .09).toFixed(2);
      });
      defender.draw(dp, dx, yAt(dz) - dl * k, k, -1);
      const at = star.draw(pose, x, yAt(z) - lift * k, k, 1);
      // floor trace, footprints and the stride label
      const zu = lt < t.gath ? .25 * lt / t.gath : lt < t.gathE ? .25 + .07 * (lt - t.gath) / (t.gathE - t.gath) : lt < t.s1 ? .32 + .28 * (lt - t.gathE) / (t.s1 - t.gathE) : lt < t.s2 ? .6 + .3 * (lt - t.s1) / (t.s2 - t.s1) : Math.min(1, .9 + .1 * (lt - t.s2) / .3);
      zig.setAttribute('stroke-dasharray', `${zu.toFixed(3)} 1`);
      const fade = 1 - prog(lt, TOTAL - .7, .5);
      zig.style.opacity = (.75 * fade).toFixed(2);
      pr1.setAttribute('opacity', lt > t.s1 - .05 ? (.6 * fade).toFixed(2) : 0);
      pr2.setAttribute('opacity', lt > t.s2 - .05 ? (.6 * fade).toFixed(2) : 0);
      strideG.setAttribute('opacity', lt > t.s2 ? (prog(lt, t.s2, .3) * (1 - prog(lt, t.make + .6, .4))).toFixed(2) : 0);
      // ball: dribbled on the drive, picked up high, carried high through both strides, then the floater
      let bx, by;
      if (lt < t.gath) { const [hx, hy] = at('rh'); const ph = (lt * 3.2) % 1, f = ph < .5 ? ph * 2 : (1 - ph) * 2; bx = hx + 6 * k; by = lerp(hy, floor - 13 * k, f * f * (3 - 2 * f)); }
      else if (lt < t.rel) { const hx = (at('lh')[0] + at('rh')[0]) / 2 + 4 * k, hy = (at('lh')[1] + at('rh')[1]) / 2 - 14 * k; if (lt < t.gathE) { const u = ease(clamp((lt - t.gath) / (t.gathE - t.gath))), [rx, ry] = at('rh'); bx = lerp(rx + 6 * k, hx, u); by = lerp(ry + 20 * k, hy, u); } else { bx = hx; by = hy; } if (lt > t.s2) { const [rx, ry] = at('rh'), u = prog(lt, t.s2 + .1, .2); bx = lerp(bx, rx + 4 * k, u); by = lerp(by, ry - 12 * k, u); } }
      else if (lt < t.make) { const u = inout(clamp((lt - t.rel) / (t.make - t.rel))); [bx, by] = arcAt(u); trail.setAttribute('stroke-dasharray', `${u.toFixed(3)} 1`); }
      else { const d = clamp((lt - t.make) / .6); bx = hoopX - 4; by = lerp(rimY - 6, floor - 13 * k, d * d); }
      if (lt < t.rel) trail.setAttribute('stroke-dasharray', '0 1');
      trail.style.opacity = (.9 * fade).toFixed(2);
      ball.setAttribute('cx', bx); ball.setAttribute('cy', by);
      // the make: net snaps, rings off the rim, +2
      const di = lt - t.make;
      drawNet(di > 0 && di < .45 ? Math.sin(Math.PI * di / .45) : 0);
      rings.forEach((r, i) => { const a = di - i * .12; if (a < 0 || a > 1) { r.setAttribute('opacity', 0); return; } const e = ease(a); r.setAttribute('rx', rimR + 150 * e); r.setAttribute('ry', 10 + 36 * e); r.setAttribute('opacity', (1 - a).toFixed(2)); });
      plus.style.opacity = di > 0 ? prog(lt, t.make, .3) * fade : 0;
      const phase = lt < t.gathE ? 0 : lt < t.s1 + .02 ? 1 : 2;
      if (!short) { cards.forEach((g, i) => g.classList.toggle('on', i === phase && lt > .3)); buttons.forEach((b, i) => b.classList.toggle('on', i === phase && lt > .3)); }
      slowTag.setAttribute('opacity', slow ? 1 : 0);
    };
    // the Short's timeline: once at full speed, then the three beats slowed down with their captions
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
  let time = still ? 2.4 : 0, playing = !still, speed = 1, last = null;
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
JUMPS = ''.join(f'<button class="jump" data-t="{t}" type="button">{n} · {_h.escape(short_title(title))}</button>' for t, (n, title, _) in zip(('0.9', '1.55', '2.1'), CFG['steps']))
KIT = CFG.get('kit') or {}
KITCSS = (f".fig-kit-phi{{stroke:{KIT['jersey']};fill:{KIT['jersey']}}}\n.fig-num{{fill:{KIT['number']}}}\n.fig-band{{stroke:{KIT['number']}}}" if KIT else '')
out = (HTML.replace('__KITCSS__', KITCSS).replace('__JUMPS__', JUMPS).replace('__NAME__', _h.escape(CFG['name'])).replace('__TITLE__', _h.escape(CFG['title']))
       .replace('__ARIA__', _h.escape(CFG['aria'])).replace('__STEPS__', json.dumps(CFG['steps'], ensure_ascii=False))
       .replace('__NAMEJS__', json.dumps(CFG['name'], ensure_ascii=False)).replace('__TITLEJS__', json.dumps(CFG['title'], ensure_ascii=False))
       .replace('__SUBJS__', json.dumps(CFG.get('sub') or '', ensure_ascii=False)).replace('__NUM__', json.dumps(CFG['number']))
       .replace('__PAL__', PAL).replace('__FIGURE__', FIGURE).replace('__FIGURE_REAL__', FIGURE_REAL).replace('__BUILD__', json.dumps(BUILD)))
os.makedirs(os.path.join(ROOT, 'src', 'anim'), exist_ok=True)
dst = os.path.join(ROOT, 'src', 'anim', CFG['out'])
open(dst, 'w').write(out)
print('wrote', os.path.relpath(dst, ROOT))
