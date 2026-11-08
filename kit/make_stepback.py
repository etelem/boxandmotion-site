"""Build a step-back-three animation for a player's scouting report from a move config.
Usage (from the repo root): python3 kit/make_stepback.py [kit/moves/<id>.json]  ->  src/anim/<out>
(defaults to kit/moves/luka-stepback.json). Config: out, team, number, name, title, build {tall, ape, mass}, steps, aria.
An original drawn illustration of his signature move, not traced from footage and not to scale.
The figure is drawn to his listed 6-8, 230 lb with arms scaled to a reported 6-11 wingspan (same build as the Nov 6 recap)."""
import os, sys, json
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from make_reel import team_palette
base = open(os.path.join(HERE, 'base-reel.html')).read().split('\n')
start = next(i for i, l in enumerate(base) if l.startswith('  const POSES = {'))
end = next(i for i in range(start, len(base)) if base[i] == '  }' and i > start + 12)
FIGURE = '\n'.join(base[start:end + 1])
FIGURE_REAL = open(os.path.join(HERE, 'figure-real.js')).read()
CFG = json.load(open(sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'moves', 'luka-stepback.json')))
BUILD = CFG['build']
PAL = team_palette(CFG['team'])

HTML = r"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>__NAME__: __TITLE__ · Box &amp; Motion Hoops</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@700;800&family=IBM+Plex+Mono:wght@500&family=IBM+Plex+Sans:wght@400;600&display=swap">
<style>
:root{
__PAL__
  --font-display:'Archivo',system-ui,sans-serif;--font-body:'IBM Plex Sans',system-ui,sans-serif;--font-mono:'IBM Plex Mono',ui-monospace,monospace;
}
html,body{margin:0;background:transparent}
body{font-family:var(--font-body);color:var(--ink)}
.wrap{background:radial-gradient(120% 95% at 12% 0%,var(--navy-lift),var(--navy-mid) 55%,var(--navy));border-radius:18px;overflow:hidden}
svg{display:block;width:100%;height:auto}
.bar{display:flex;flex-wrap:wrap;gap:8px;align-items:center;padding:0 16px 16px}
.bar button{font:600 14px/1 var(--font-body);color:var(--ink);background:transparent;border:1px solid var(--hairline);border-radius:999px;min-height:38px;padding:0 14px;cursor:pointer}
.bar button[aria-pressed="true"],.bar button.on{background:var(--ink);color:var(--navy);border-color:var(--ink)}
.bar button:focus-visible{outline:2px solid var(--blue-text);outline-offset:2px}
.bar .sp{flex:1}
.d{font-family:var(--font-display);font-weight:800;fill:var(--ink)}
.k{font-family:var(--font-mono);font-weight:500;letter-spacing:.14em;text-transform:uppercase;fill:var(--red-text)}
.b{font-family:var(--font-body);fill:var(--ink)}
.m{fill:var(--muted)}
.s-silver{stroke:var(--silver);fill:none}
.s-red{stroke:var(--red);fill:none}
.f-ink{fill:var(--ink)}
.f-red{fill:var(--red)}
.fig-o-phi{stroke:var(--blue-text);fill:var(--blue-text)}
.fig-o-opp{stroke:var(--silver);fill:var(--silver)}
.fig-skin{stroke:var(--navy);fill:var(--navy)}
.fig-kit-phi{stroke:var(--blue);fill:var(--blue)}
.fig-kit-opp{stroke:var(--navy-mid);fill:var(--navy-mid)}
.fig-shoe{stroke:var(--ink);fill:var(--ink)}
.fig-num{font-family:var(--font-display);font-weight:800;fill:var(--navy-lift)}
.fig-hair{stroke:var(--navy-mid);fill:var(--navy-mid)}
.fig-band{stroke:var(--navy-lift);fill:none}
.step{opacity:.35;transition:opacity .2s}
html.short .step{transition:none}
html.short .step.solo{opacity:0}
html.short .step.solo.on{opacity:1}
html.short .bar{display:none}
html.short .wrap{border-radius:0}
.step.on{opacity:1}
__KITCSS__
</style></head><body>
<div class="wrap">
<svg id="sv" role="img" aria-label="__ARIA__"></svg>
<div class="bar"><button id="pp" type="button">Pause</button><button id="slow" type="button" aria-pressed="false">Slow motion</button><span class="sp"></span>
__JUMPS__</div>
</div>
<script>
(() => {
  const NS = 'http://www.w3.org/2000/svg';
  const clamp = (v) => Math.max(0, Math.min(1, v));
  const ease = (v) => 1 - Math.pow(1 - v, 3);
  const inout = (v) => v < .5 ? 2 * v * v : 1 - Math.pow(-2 * v + 2, 2) / 2;
  const prog = (lt, s, d) => ease(clamp((lt - s) / d));
  const lerp = (a, b, p) => a + (b - a) * p;
  const S = (tag, attrs, parent) => { const n = document.createElementNS(NS, tag); for (const k in attrs) n.setAttribute(k, attrs[k]); if (parent) parent.appendChild(n); return n; };
  const T = (p, x, y, s, cls, size, anchor) => { const n = S('text', {x, y, class: cls, 'text-anchor': anchor || 'start'}, p); n.textContent = s; n.style.fontSize = size + 'px'; return n; };
__FIGURE__
  if (__KNEEUP__) POSES.rise = Object.assign({}, POSES.rise, {rk: [28, -112], rf: [22, -58]});   // his high release with one knee driven up
  POSES.dribble = {head: [14, -224], neck: [8, -200], hip: [-2, -122], lk: [-20, -64], lf: [-30, 0], rk: [22, -66], rf: [32, 0], le: [-14, -160], lh: [-20, -124], re: [34, -156], rh: [52, -104]};
  POSES.jab = {head: [34, -208], neck: [26, -186], hip: [4, -112], lk: [44, -58], lf: [66, 0], rk: [-18, -60], rf: [-34, 0], le: [-4, -148], lh: [4, -110], re: [46, -150], rh: [66, -104]};
  POSES.land = {head: [0, -210], neck: [-2, -186], hip: [-8, -108], lk: [10, -60], lf: [-6, 0], rk: [16, -58], rf: [18, 0], le: [18, -168], lh: [28, -186], re: [16, -154], rh: [30, -182]};
__FIGURE_REAL__
  const BUILD = __BUILD__;
  const svg = document.getElementById('sv');
  const steps = __STEPS__;
  const TOTAL = 7.2;
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
    const k = short ? 1.16 : portrait ? 1.02 : 1.12;
    const floor = short ? H - 560 : portrait ? H - 250 : H - 150;
    const hoopX = W - M - (short ? 10 : portrait ? 20 : 60);
    const arcX = short ? hoopX - 520 : portrait ? hoopX - 470 : hoopX - 640;
    const rimY = floor - 240 * k * 1.62, rimR = 30 * k;
    // header
    const hy = short ? 100 : M + 6;
    T(svg, M, hy, 'Signature move · ' + __NAMEJS__, 'k', short ? 28 : portrait ? 22 : 18);
    T(svg, M, hy + (short ? 76 : portrait ? 56 : 48), __TITLEJS__, 'd', short ? 68 : portrait ? 52 : 44);
    if (short) { T(svg, M, H - 70, 'BOX & MOTION HOOPS', 'd', 36); T(svg, W - M, H - 70, 'boxandmotion.com', 'b m', 28, 'end'); }
    // court
    const court = S('g', {class: 's-silver', 'stroke-width': 3, 'stroke-linecap': 'round', opacity: .9}, svg);
    S('line', {x1: M - 30, x2: W + 30, y1: floor, y2: floor}, court);
    S('line', {x1: arcX, x2: arcX, y1: floor - 6, y2: floor + 16}, court);
    S('line', {x1: hoopX + 40 * k, x2: hoopX + 40 * k, y1: rimY - 120 * k, y2: floor}, court);
    T(svg, arcX, floor + 36, '3-pt line', 'b m', portrait ? 20 : 16, 'middle');
    S('rect', {x: hoopX + 26 * k, y: rimY - 150 * k, width: 12 * k, height: 170 * k, rx: 3, fill: 'var(--silver)'}, svg);
    S('line', {x1: hoopX - rimR, x2: hoopX + 26 * k, y1: rimY, y2: rimY, class: 's-red', 'stroke-width': 6, 'stroke-linecap': 'round'}, svg);
    const net = S('g', {class: 's-silver', 'stroke-width': 2, opacity: .8}, svg);
    for (let i = 0; i <= 4; i++) { const tp = hoopX - rimR + i * rimR / 2, bt = hoopX - rimR * .55 + i * rimR * 1.1 / 4; S('line', {x1: tp, y1: rimY, x2: bt, y2: rimY + 44 * k}, net); }
    // space bracket
    const space = S('g', {}, svg);
    const sl = S('line', {class: 's-silver', 'stroke-width': 3, filter: 'url(#glow)'}, space);
    const c1 = S('line', {class: 's-silver', 'stroke-width': 3}, space), c2 = S('line', {class: 's-silver', 'stroke-width': 3}, space);
    const st = T(space, 0, 0, 'Space', 'b', portrait ? 24 : 20, 'middle'); st.style.fontWeight = 600;
    // footprints where he jabs and where he lands
    const prints = S('g', {}, svg);
    const pJab = S('ellipse', {rx: 22 * k, ry: 5, class: 'f-red', opacity: 0}, prints);
    const pLand = S('ellipse', {rx: 30 * k, ry: 5, class: 'f-red', opacity: 0}, prints);
    // figures
    const defender = figure(svg, 'opp', k);
    defender.g.setAttribute('opacity', .8);
    const ghosts = [0, 1, 2].map(() => { const gh = figureReal(svg, 'phi', k, __NUM__, BUILD); gh.g.style.opacity = 0; return gh; }).reverse();
    const luka = figureReal(svg, 'phi', k, __NUM__, BUILD);
    const trailG = S('g', {}, svg);
    const ball = S('circle', {r: 13 * k, class: 'f-ink', filter: 'url(#glow)'}, svg);
    const flash = S('circle', {cx: hoopX, cy: rimY, r: 0, fill: 'none', stroke: 'var(--ink)', 'stroke-width': 4, opacity: 0}, svg);
    const plus = T(svg, hoopX - rimR - 10, rimY - 64 * k, '+3', 'd', portrait ? 72 : 64, 'end');
    // step cards
    const cards = steps.map((s, i) => {
      const g = S('g', {class: 'step'}, svg);
      if (short) {
        const y = floor + 150;
        T(g, M, y, s[0], 'd', 64).setAttribute('fill', 'var(--red)');
        const t1 = T(g, M + 64, y - 12, s[1], 'b', 48); t1.style.fontWeight = 600;
        T(g, M + 64, y + 40, s[2], 'b m', 34);
        g.classList.add('solo');
      } else if (portrait) {
        const y = floor + 86 + i * 54;
        T(g, M, y, s[0], 'd', 34).setAttribute('fill', 'var(--red)');
        const t1 = T(g, M + 40, y, s[1], 'b', 26); t1.style.fontWeight = 600;
        T(g, M + 40 + 254, y, s[2], 'b m', 20);
      } else {
        const cw = (W - 2 * M) / 3, x = M + i * cw, y = floor + 92;
        T(g, x, y, s[0], 'd', 38).setAttribute('fill', 'var(--red)');
        const t1 = T(g, x + 38, y - 8, s[1], 'b', 23); t1.style.fontWeight = 600;
        T(g, x + 38, y + 20, s[2], 'b m', 18);
      }
      return g;
    });
    const note = T(svg, M, short ? hy + 124 : portrait ? M + 96 : M + 84, 'Original illustration · not traced from footage, not to scale', 'b m', short ? 24 : portrait ? 18 : 15);
    // timing (seconds)
    const t = {jab: 0.6, hop: 2.0, land: 2.55, rise: 2.95, rel: 3.45, make: 4.55};
    const x0 = arcX - 150 * k, xJab = arcX + 40 * k, xLand = arcX - 120 * k;
    const relPt = () => { const at = luka.draw(POSES.rise, xLand, floor - 16 * k, k, 1); return [(at('lh')[0] + at('rh')[0]) / 2 + 4 * k, (at('lh')[1] + at('rh')[1]) / 2 - 16 * k]; };
    const rel = relPt();
    const peak = short ? 200 : portrait ? 170 : 120;
    const arcAt = (u) => [lerp(rel[0], hoopX, u), lerp(rel[1], rimY - 6, u) - 4 * peak * u * (1 - u)];
    const trail = S('path', {d: 'M' + Array.from({length: 61}, (_, i) => arcAt(i / 60)).map(([x, y]) => `${x.toFixed(1)} ${y.toFixed(1)}`).join('L'), class: 's-silver', 'stroke-width': 4, 'stroke-dasharray': '0 1', pathLength: 1, opacity: .85, filter: 'url(#glow)'}, trailG);
    built = {portrait};
    const lukaAt = (lt) => {
      // Luka: dribble in, jab, hop back, set, rise, land
      let lx, pose, lift = 0;
      if (lt < t.jab) { lx = x0; pose = POSES.dribble; }
      else if (lt < t.hop) { const p = inout(clamp((lt - t.jab) / (t.hop - t.jab - .25))); lx = lerp(x0, xJab, p); pose = p > .7 ? mixPose(POSES.dribble, POSES.jab, (p - .7) / .3) : POSES.dribble; }
      else if (lt < t.land) { const p = clamp((lt - t.hop) / (t.land - t.hop)); lx = lerp(xJab, xLand, inout(p)); pose = mixPose(POSES.jab, POSES.land, p); lift = 30 * Math.sin(p * Math.PI); }
      else if (lt < t.rise) { lx = xLand; pose = mixPose(POSES.land, POSES.set, prog(lt, t.land, .35)); }
      else if (lt < t.make + .4) { lx = xLand; const up = prog(lt, t.rise, .5), down = clamp((lt - (t.rel + .25)) / .6); pose = lt < t.rel + .25 ? mixPose(POSES.set, POSES.rise, up) : mixPose(POSES.rise, POSES.land, down); lift = lt < t.rel + .25 ? 16 * up : 16 * (1 - down * down); }
      else { lx = xLand; pose = POSES.land; }
      if (lt < t.jab) { const bob = Math.sin(lt * 9) * 4; pose = POSES.dribble; lx += bob * k; }
      return [pose, lx, lift];
    };
    L = (lt) => {
      const [pose, lx, lift] = lukaAt(lt);
      // speed trail on the hop back: afterimages of him a beat behind, fading as he lands (like Maxey's coast-to-coast)
      ghosts.forEach((gh, i) => {
        const lag = (i + 1) * 0.06, on = lt > t.hop + .02 && lt < t.land + .45;
        if (!on) { gh.g.style.opacity = 0; return; }
        const [gp, gx, gl] = lukaAt(lt - lag);
        gh.draw(gp, gx, floor - gl * k, k, 1);
        gh.g.style.opacity = ((0.5 - i * 0.14) * (1 - prog(lt, t.land, .45))).toFixed(2);
      });
      const at = luka.draw(pose, lx, floor - lift * k, k, 1);
      // defender: guards, backs off the jab, closes out late
      let dx, dPose = POSES.guard, dLift = 0;
      const gap = lerp(165, 205, prog(lt, t.hop - .7, .6)) * k, dBack = xJab + 205 * k + 10 * k, dClose = xLand + 100 * k;
      if (lt < t.hop) dx = lx + gap;
      else if (lt < t.land + .1) dx = lerp(xJab + 205 * k, dBack, prog(lt, t.hop, .5));
      else { const p = inout(clamp((lt - t.land - .1) / 1.0)); dx = lerp(dBack, dClose, p); const up = prog(lt, t.rel - .1, .5), dn = clamp((lt - t.rel - .5) / .5); dPose = lt < t.rel - .1 ? POSES.guard : lt < t.rel + .5 ? mixPose(POSES.guard, POSES.contest, up) : mixPose(POSES.contest, POSES.guard, dn); dLift = lt < t.rel + .5 ? 24 * up : 24 * (1 - dn); }
      defender.draw(dPose, dx, floor - dLift * k, k, -1);
      // space bracket while he lands and sets
      const sy = floor - 150 * k, a = lx + 40 * k, b = dx - 40 * k, on = lt > t.land - .05 && lt < t.rel + .1 && b > a;
      [[sl, a, sy, b, sy], [c1, a, sy - 12, a, sy + 12], [c2, b, sy - 12, b, sy + 12]].forEach(([n, x1, y1, x2, y2]) => { n.setAttribute('x1', x1); n.setAttribute('y1', y1); n.setAttribute('x2', x2); n.setAttribute('y2', y2); });
      st.setAttribute('x', (a + b) / 2); st.setAttribute('y', sy - 20);
      space.style.opacity = on ? Math.min(prog(lt, t.land - .05, .25), 1 - prog(lt, t.rel - .15, .25)) : 0;
      // footprints
      pJab.setAttribute('cx', xJab + 50 * k); pJab.setAttribute('cy', floor + 2); pJab.setAttribute('opacity', lt > t.hop - .1 && lt < t.make + 1.2 ? .55 : 0);
      pLand.setAttribute('cx', xLand); pLand.setAttribute('cy', floor + 2); pLand.setAttribute('opacity', lt > t.land && lt < t.make + 1.2 ? .55 : 0);
      // ball
      let bx, by;
      if (lt >= t.hop && lt < t.land + .15) {
        // between the legs: right hand down through his legs, up into the left hand as he hops back to his left
        const p = clamp((lt - t.hop) / (t.land + .15 - t.hop)), [rx, ry] = at('rh'), [qx, qy] = at('lh');
        const px = (at('lf')[0] + at('rf')[0]) / 2, py = floor - 13 * k;
        if (p < .45) { const q = p / .45; bx = lerp(rx + 6 * k, px, q); by = lerp(ry, py, q * q); }
        else { const q = (p - .45) / .55; bx = lerp(px, qx - 4 * k, q); by = lerp(py, qy, 1 - (1 - q) * (1 - q)); }
      }
      else if (lt < t.rise) { const [hx, hy] = at('rh'); const ph = (lt * 2.5) % 1, f = ph < .5 ? ph * 2 : (1 - ph) * 2; bx = hx + 6 * k; by = lt < t.land ? lerp(hy, floor - 13 * k, f * f * (3 - 2 * f)) : (at('lh')[1] + hy) / 2 - 16 * k; if (lt >= t.land) bx = (at('lh')[0] + hx) / 2 + 4 * k; }
      else if (lt < t.rel) { bx = (at('lh')[0] + at('rh')[0]) / 2 + 4 * k; by = (at('lh')[1] + at('rh')[1]) / 2 - 16 * k; }
      else if (lt < t.make) { const u = inout(clamp((lt - t.rel) / (t.make - t.rel))); [bx, by] = arcAt(u); trail.setAttribute('stroke-dasharray', `${u.toFixed(3)} 1`); }
      else { const d = clamp((lt - t.make) / .6); bx = hoopX - 4; by = lerp(rimY - 6, floor - 13 * k, d * d); }
      if (lt < t.rel) trail.setAttribute('stroke-dasharray', '0 1');
      trail.style.opacity = .85 * (1 - prog(lt, TOTAL - .8, .5));
      ball.setAttribute('cx', bx); ball.setAttribute('cy', by);
      const made = lt >= t.make, f = made ? clamp((lt - t.make) / .8) : 0;
      flash.setAttribute('r', rimR + 140 * f); flash.setAttribute('opacity', made ? 1 - f : 0);
      plus.style.opacity = made ? prog(lt, t.make, .3) * (1 - prog(lt, TOTAL - .6, .4)) : 0;
      const phase = lt < t.hop ? 0 : lt < t.rise ? 1 : 2;
      cards.forEach((g, i) => g.classList.toggle('on', i === phase && lt > .3));
      buttons.forEach((b, i) => b.classList.toggle('on', i === phase && lt > .3));
    };
  }

  const buttons = [...document.querySelectorAll('.jump')];
  const still = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  let time = still ? 4.9 : 0, playing = !still, speed = 1, last = null;
  const pp = document.getElementById('pp'), slow = document.getElementById('slow');
  pp.textContent = playing ? 'Pause' : 'Play';
  pp.onclick = () => { playing = !playing; pp.textContent = playing ? 'Pause' : 'Play'; };
  slow.onclick = () => { speed = speed === 1 ? .35 : 1; slow.setAttribute('aria-pressed', speed < 1); };
  buttons.forEach((b) => b.onclick = () => { time = +b.dataset.t; playing = true; pp.textContent = 'Pause'; });
  build(); L(time);
  if ('ResizeObserver' in window) new ResizeObserver(() => { const p = svg.clientWidth < 620; if (built && built.portrait !== p) { build(); L(time); } }).observe(svg);
  const frame = (now) => { if (last != null && playing) { time += (now - last) / 1000 * speed; if (time > TOTAL) time = 0; } last = now; if (!window.__hold) L(time); requestAnimationFrame(frame); };
  requestAnimationFrame(frame);
  window.__SB = {render: (x) => L(x), build};
  window.__A = {render: (x) => L(x), build, total: TOTAL};
  // tell a parent page how tall we are, so its iframe fits without scrolling
  const postH = () => { if (window.parent !== window) window.parent.postMessage({bmH: Math.ceil(document.querySelector('.wrap').getBoundingClientRect().height)}, '*'); };
  if ('ResizeObserver' in window) new ResizeObserver(postH).observe(document.body); window.addEventListener('load', postH); postH();
})();
</script>
</body></html>
"""
import html as _h
JUMPS = ''.join(f'<button class="jump" data-t="{t}" type="button">{n} · {_h.escape((title[4:] if title.startswith("The ") else title)[:1].upper() + (title[4:] if title.startswith("The ") else title)[1:])}</button>' for t, (n, title, _) in zip(('0.6', '2.0', '2.9'), CFG['steps']))
KIT = CFG.get('kit') or {}
KITCSS = (f".fig-kit-phi{{stroke:{KIT['jersey']};fill:{KIT['jersey']}}}\n.fig-num{{fill:{KIT['number']}}}\n.fig-band{{stroke:{KIT['number']}}}" if KIT else '')
out = HTML.replace('__KITCSS__', KITCSS).replace('__KNEEUP__', 'true' if CFG.get('kneeUp') else 'false').replace('__JUMPS__', JUMPS).replace('__NAME__', _h.escape(CFG['name'])).replace('__TITLE__', _h.escape(CFG['title'])).replace('__ARIA__', _h.escape(CFG['aria'])).replace('__STEPS__', json.dumps(CFG['steps'], ensure_ascii=False)).replace('__NAMEJS__', json.dumps(CFG['name'], ensure_ascii=False)).replace('__TITLEJS__', json.dumps(CFG['title'], ensure_ascii=False)).replace('__NUM__', json.dumps(CFG['number'])).replace('__PAL__', PAL).replace('__FIGURE__', FIGURE).replace('__FIGURE_REAL__', FIGURE_REAL).replace('__BUILD__', json.dumps(BUILD))
os.makedirs(os.path.join(ROOT, 'src', 'anim'), exist_ok=True)
dst = os.path.join(ROOT, 'src', 'anim', CFG['out'])
open(dst, 'w').write(out)
print('wrote', os.path.relpath(dst, ROOT))
