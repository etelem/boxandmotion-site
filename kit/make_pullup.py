"""Build a hard-stop pull-up animation for a player's scouting report from a move config.
Usage (from the repo root): python3 kit/make_pullup.py kit/moves/<id>.json  ->  src/anim/<out>
Config: out, team, number, name, title, build {tall, ape, mass, ...look keys if approved}, kit {jersey, number}, steps
[[n, title, line] x3], aria, sub (optional dated line under the title in the Short), kicker (optional).
Modeled on make_eurostep.py / make_stepback.py: same figure, palette, controls, ?short=1 and ?embed=1 modes, window.__A,
reduced motion, height postMessage.
The move: a full-speed drive with the defender backpedaling, one hard stop (lead foot planted out front as a brake), the
defender keeps sliding back and a gap opens, then a pull-up jumper into that gap. His trait motion is the deceleration:
afterimages that pile up as he stops, skid marks under the plant foot, and the gap labelled "The window".
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
  // the hard stop: lead foot planted out in front as a brake, hips sunk, chest back, ball pulled in with both hands
  POSES.brake = {head: [-6, -206], neck: [-6, -184], hip: [-8, -108], lk: [30, -58], lf: [62, 0], rk: [-30, -56], rf: [-52, -6], le: [10, -150], lh: [30, -134], re: [18, -148], rh: [38, -132]};
  // squared up and balanced, both feet under him, ball at the chin: the defender is still going backwards
  POSES.set2 = {head: [4, -214], neck: [2, -190], hip: [-2, -114], lk: [14, -62], lf: [8, 0], rk: [20, -60], rf: [26, 0], le: [22, -172], lh: [30, -196], re: [18, -158], rh: [34, -190]};
  POSES.land = {head: [0, -214], neck: [-2, -190], hip: [-6, -112], lk: [12, -60], lf: [-4, 0], rk: [16, -58], rf: [20, 0], le: [20, -170], lh: [28, -190], re: [16, -156], rh: [30, -150]};
__FIGURE_REAL__
  const BUILD = __BUILD__;
  const svg = document.getElementById('sv');
  const steps = __STEPS__;
  const TOTAL = 6.0;                                  // one pass of the move (site loop)
  const t = {brake: 1.3, stop: 1.68, set: 1.98, rise: 2.02, rel: 2.38, make: 3.2};
  // the Short: full speed once, then a slow breakdown of the three beats with their captions
  const P_END = 4.1, B0 = 4.3, SEGS = [[0.75, 1.32, .4], [1.28, 2.02, .32], [1.98, 3.4, .5]];
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
    const k = short ? 1.32 : portrait ? 1.0 : 1.12;
    const floor = short ? H - 520 : portrait ? H - 290 : H - 190;
    const hoopX = W - M - (short ? 10 : portrait ? 20 : 60);
    const rimY = floor - 240 * k * 1.62, rimR = 30 * k;
    // he stops at the elbow-ish mid-range spot; the drive starts off the left edge
    const xStop = hoopX - (short ? 420 : portrait ? 400 : 470) * k, xBrake = xStop - 70 * k, x0 = short ? M - 60 : Math.max(M - 20, xStop - 560 * k);
    // the defender starts a step ahead of him and backpedals; at the stop he keeps sliding (the window), then lunges back late
    const xD0 = x0 + 250 * k, xD1 = xBrake + 210 * k, xD2 = xStop + 270 * k, xD3 = xStop + 150 * k;
    // header
    const hy = short ? 100 : M + 6;
    // the kicker shrinks to fit the width when a long name would run off the edge (re-fit once the fonts load)
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
    // his trait: the brakes. Skid marks where the lead foot plants, a "Full stop" tag, then the gap that opens ("The window")
    const skid = S('g', {opacity: 0}, svg);
    const skidL = [0, 1, 2].map((i) => S('line', {stroke: 'var(--red)', 'stroke-width': 5 - i * 1.4, 'stroke-linecap': 'round', opacity: 1 - i * .25}, skid));
    const stopT = T(svg, 0, 0, 'Full stop', 'b', short ? 32 : portrait ? 24 : 21, 'middle'); stopT.style.fontWeight = 700; stopT.style.fill = 'var(--red)'; stopT.style.opacity = 0;
    const gapG = S('g', {opacity: 0}, svg);
    const gapL = S('line', {class: 's-silver', 'stroke-width': 3, 'stroke-dasharray': '6 7'}, gapG);
    const gapA = S('line', {class: 's-silver', 'stroke-width': 3}, gapG), gapB = S('line', {class: 's-silver', 'stroke-width': 3}, gapG);
    const gapT = T(gapG, 0, 0, 'The window', 'b', short ? 30 : portrait ? 22 : 19, 'middle'); gapT.style.fontWeight = 600;
    // figures: afterimages that pile up as he decelerates, the defender, the star
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
    // the lead foot's plant spot (for the skid marks)
    const plant = star.draw(POSES.brake, xStop, floor, k, 1)('lf');
    const skidX0 = plant[0] - 70 * k, skidX1 = plant[0] + 6 * k;
    skidL.forEach((l, i) => { const y = floor + 4 + i * 7; l.setAttribute('y1', y); l.setAttribute('y2', y); });
    stopT.setAttribute('x', plant[0] - 30 * k); stopT.setAttribute('y', floor + (short ? 58 : 44));
    // release point and the jumper's arc
    const relPt = () => { const at = star.draw(POSES.rise, xStop, floor - 30 * k, k, 1); return [(at('lh')[0] + at('rh')[0]) / 2 + 4 * k, (at('lh')[1] + at('rh')[1]) / 2 - 16 * k]; };
    const rel = relPt();
    const peak = short ? 190 : portrait ? 170 : 150;
    const arcAt = (u) => [lerp(rel[0], hoopX, u), lerp(rel[1], rimY - 6, u) - 4 * peak * u * (1 - u)];
    const trail = S('path', {d: 'M' + Array.from({length: 61}, (_, i) => arcAt(i / 60)).map(([x, y]) => `${x.toFixed(1)} ${y.toFixed(1)}`).join('L'), stroke: 'var(--blue-text)', fill: 'none', 'stroke-width': 4, 'stroke-dasharray': '0 1', pathLength: 1, opacity: .9, filter: 'url(#glow)'}, trailG);
    built = {portrait};
    // the star: [pose, x, lift]
    const starAt = (lt) => {
      if (lt < t.brake) { const c = Math.sin(lt * 10) * .5 + .5; return [mixPose(POSES.run1, POSES.run2, c), lerp(x0, xBrake, lt / t.brake), 0]; }
      if (lt < t.stop) { const u = clamp((lt - t.brake) / (t.stop - t.brake)); return [mixPose(POSES.run1, POSES.brake, ease(Math.min(1, u * 1.6))), lerp(xBrake, xStop, 1 - Math.pow(1 - u, 3)), 0]; }
      if (lt < t.rise) { const u = prog(lt, t.stop + .06, t.rise - t.stop - .06); return [mixPose(POSES.brake, POSES.set2, ease(u)), xStop, 0]; }
      if (lt < t.rel + .28) { const u = prog(lt, t.rise, t.rel + .1 - t.rise); return [mixPose(POSES.set2, POSES.rise, ease(u)), xStop, 30 * ease(u)]; }
      const d = clamp((lt - t.rel - .28) / .55); return [mixPose(POSES.rise, POSES.land, ease(d)), xStop, 30 * (1 - d * d)];
    };
    // the defender: backpedals ahead of the drive, can't stop when he does, then lunges back for a late contest
    const defAt = (lt) => {
      if (lt < t.brake) return [POSES.guard, lerp(xD0, xD1, lt / t.brake), 0];
      if (lt < t.set + .02) { const u = prog(lt, t.brake, t.set + .02 - t.brake); return [POSES.guard, lerp(xD1, xD2, 1 - Math.pow(1 - u, 2)), 0]; }
      if (lt < t.rel + .25) { const u = prog(lt, t.set + .02, t.rel + .2 - t.set); return [mixPose(POSES.guard, POSES.contest, ease(u)), lerp(xD2, xD3, ease(u)), 14 * Math.sin(Math.PI * u)]; }
      const b = prog(lt, t.rel + .25, .6); return [mixPose(POSES.contest, POSES.guard, ease(b)), xD3, 0];
    };
    L = (lt, slow) => {
      const [pose, x, lift] = starAt(lt), [dp, dx, dl] = defAt(lt);
      // afterimages from the drive into the stop: spaced out at speed, stacked on top of him once he has stopped
      const ghosting = lt > t.brake - .55 && lt < t.stop + .2;
      ghosts.forEach((gh, i) => {
        if (!ghosting) { gh.g.style.opacity = 0; return; }
        const [gp, gx, gl] = starAt(Math.max(0, lt - (i + 1) * .07));
        gh.draw(gp, gx, floor - gl * k, k, 1);
        gh.g.style.opacity = ((.34 - i * .09) * (1 - prog(lt, t.stop, .2))).toFixed(2);
      });
      defender.draw(dp, dx, floor - dl * k, k, -1);
      const at = star.draw(pose, x, floor - lift * k, k, 1);
      const fade = 1 - prog(lt, TOTAL - .7, .5);
      // skid marks grow under the lead foot through the stop; the tag fades in once he is planted
      const sk = prog(lt, t.brake + .04, t.stop - t.brake - .04);
      skid.setAttribute('opacity', lt > t.brake ? (.85 * fade).toFixed(2) : 0);
      skidL.forEach((l) => { l.setAttribute('x1', skidX0); l.setAttribute('x2', skidX0 + (skidX1 - skidX0) * sk); });
      stopT.style.opacity = (prog(lt, t.stop - .1, .2) * (1 - prog(lt, t.make + .5, .4)) * fade).toFixed(2);
      // the window: the gap between them while the defender is still sliding back
      const gx1 = x + 34 * k, gx2 = dx - 34 * k, gy = floor - 290 * k;
      gapL.setAttribute('x1', gx1); gapL.setAttribute('x2', gx2); gapL.setAttribute('y1', gy); gapL.setAttribute('y2', gy);
      [[gapA, gx1], [gapB, gx2]].forEach(([l, xx]) => { l.setAttribute('x1', xx); l.setAttribute('x2', xx); l.setAttribute('y1', gy - 12); l.setAttribute('y2', gy + 12); });
      gapT.setAttribute('x', (gx1 + gx2) / 2); gapT.setAttribute('y', gy - (short ? 22 : 16));
      gapG.setAttribute('opacity', (prog(lt, t.stop, .2) * (1 - prog(lt, t.rise + .04, .16))).toFixed(2));
      // ball: dribbled on the drive, pulled in on the stop, up at the chin, then the pull-up jumper
      let bx, by;
      if (lt < t.brake) { const [hx, hy] = at('rh'); const ph = (lt * 3.4) % 1, f = ph < .5 ? ph * 2 : (1 - ph) * 2; bx = hx + 6 * k; by = lerp(hy, floor - 13 * k, f * f * (3 - 2 * f)); }
      else if (lt < t.rel) { const hx = (at('lh')[0] + at('rh')[0]) / 2 + 6 * k, hy = (at('lh')[1] + at('rh')[1]) / 2 - 10 * k; if (lt < t.brake + .2) { const u = ease(prog(lt, t.brake, .2)), [rx, ry] = at('rh'); bx = lerp(rx + 6 * k, hx, u); by = lerp(ry + 30 * k, hy, u); } else { bx = hx; by = hy; } }
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
      const phase = lt < t.brake ? 0 : lt < t.set ? 1 : 2;
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
JUMPS = ''.join(f'<button class="jump" data-t="{t}" type="button">{n} · {_h.escape(short_title(title))}</button>' for t, (n, title, _) in zip(('0.4', '1.3', '1.98'), CFG['steps']))
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
