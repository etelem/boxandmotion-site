"""Build a ~26-second, play-first YouTube Short (9:16) for one game from a short config.
Usage (from the repo root): python3 kit/make_playshort.py kit/shorts/<id>.json  ->  src/anim/<out>
Then: bash kit/short_mp4.sh src/anim/<out> kit/out/<name>.mp4 1

Order: the play of the game from the first frame (hook title, score and clock on screen), the free throw / result beat,
a slow-motion replay, the final score with the star's line, then the end card. The star is the recap silhouette drawn to
his build in his skin tone and team colours, face blank; the play is drawn from written accounts, not traced, not to scale.
This version draws a drive and a floater through contact (and-one). Other play types get their own scene function."""
import os, sys, json, html
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from make_reel import team_palette
base = open(os.path.join(HERE, 'base-reel.html')).read().split('\n')
start = next(i for i, l in enumerate(base) if l.startswith('  const POSES = {'))
end = next(i for i in range(start, len(base)) if base[i] == '  }' and i > start + 12)
FIGURE = '\n'.join(base[start:end + 1])
FIGURE_REAL = open(os.path.join(HERE, 'figure-real.js')).read()
CFG = json.load(open(sys.argv[1]))
PAL = team_palette(CFG['team'])
from looks import look_for, kit_for, kit_css
if CFG.get('player'):
    _look, _status, _sig = look_for(CFG['player'])
    CFG['build'] = {**_look, **CFG.get('build', {})}
    if _sig == 'splash' and 'signature' not in CFG: CFG['signature'] = 'splash'
if not CFG.get('kit'):
    CFG['kit'] = kit_for(CFG['team'], CFG.get('home', True))
if not CFG.get('accent'):
    import json as _j; _t = _j.load(open(os.path.join(ROOT, 'data', 'teams.json')))[CFG['team']]
    CFG['accent'] = _t['c2'] if _t['c2'].upper() not in ('#FFFFFF', '#C4CED4', '#B8C4CA', '#A1A1A4', '#63727A') else '#FF5A1F'
KIT = CFG.get('kit') or {}
KITCSS = (f".fig-kit-phi{{stroke:{KIT['jersey']};fill:{KIT['jersey']}}}\n.fig-num{{fill:{KIT['number']}}}\n.fig-band{{stroke:{KIT['number']}}}" if KIT else '')

HTML = r"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>__TITLE__ · Box &amp; Motion Hoops</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@700;800&family=IBM+Plex+Mono:wght@500&family=IBM+Plex+Sans:wght@400;600&display=swap">
<style>
:root{
__PAL__
  --font-display:'Archivo',system-ui,sans-serif;--font-body:'IBM Plex Sans',system-ui,sans-serif;--font-mono:'IBM Plex Mono',ui-monospace,monospace;
}
html,body{margin:0;background:#111214}
body{font-family:var(--font-body);color:var(--ink);display:flex;justify-content:center}
.wrap{width:min(100vw,56.25vh);background:radial-gradient(120% 95% at 12% 0%,var(--navy-lift),var(--navy-mid) 55%,var(--navy));overflow:hidden}
html.short .wrap{width:100%}
svg{display:block;width:100%;height:auto}
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
__KITCSS__
</style></head><body>
<div class="wrap"><svg id="sv" viewBox="0 0 900 1600" role="img" aria-label="__ARIA__"></svg></div>
<script>
if (/[?&]short=1/.test(location.search)) document.documentElement.classList.add('short');
(() => {
  const C = __CFG__;
  const NS = 'http://www.w3.org/2000/svg';
  const clamp = (v) => Math.max(0, Math.min(1, v));
  const ease = (v) => 1 - Math.pow(1 - v, 3);
  const inout = (v) => v < .5 ? 2 * v * v : 1 - Math.pow(-2 * v + 2, 2) / 2;
  const prog = (lt, s, d) => ease(clamp((lt - s) / d));
  const lerp = (a, b, p) => a + (b - a) * p;
  const S = (tag, attrs, parent) => { const n = document.createElementNS(NS, tag); for (const k in attrs) n.setAttribute(k, attrs[k]); if (parent) parent.appendChild(n); return n; };
  const T = (p, x, y, s, cls, size, anchor) => { const n = S('text', {x, y, class: cls, 'text-anchor': anchor || 'start'}, p); n.textContent = s; n.style.fontSize = size + 'px'; return n; };
__FIGURE__
  // drive, gather and floater poses (facing right)
  POSES.run1 = {head: [26, -222], neck: [20, -198], hip: [0, -122], lk: [30, -70], lf: [22, 0], rk: [-20, -62], rf: [-46, -12], le: [-4, -162], lh: [6, -130], re: [36, -160], rh: [54, -110]};
  POSES.run2 = {head: [26, -222], neck: [20, -198], hip: [0, -122], lk: [-20, -62], lf: [-46, -12], rk: [30, -70], rf: [22, 0], le: [-4, -162], lh: [6, -130], re: [36, -160], rh: [54, -110]};
  POSES.gather = {head: [16, -214], neck: [12, -190], hip: [-2, -116], lk: [20, -62], lf: [12, 0], rk: [-14, -62], rf: [-28, 0], le: [26, -168], lh: [36, -172], re: [22, -160], rh: [36, -168]};
  POSES.float = {head: [2, -246], neck: [0, -222], hip: [-4, -140], lk: [24, -110], lf: [16, -62], rk: [-8, -74], rf: [-12, -6], le: [16, -232], lh: [22, -258], re: [18, -264], rh: [26, -310]};
  POSES.land = {head: [0, -214], neck: [-2, -190], hip: [-6, -112], lk: [12, -60], lf: [-4, 0], rk: [16, -58], rf: [20, 0], le: [20, -170], lh: [28, -190], re: [16, -156], rh: [30, -150]};
  POSES.bump = {head: [-14, -230], neck: [-10, -206], hip: [0, -128], lk: [-16, -68], lf: [-26, 0], rk: [18, -68], rf: [26, 0], le: [-30, -196], lh: [-44, -224], re: [24, -200], rh: [30, -240]};
__FIGURE_REAL__
  const BUILD = C.build;
  const svg = document.getElementById('sv');
  const W = 900, H = 1600, M = 56, k = 1.5;
  const floor = 1230, hoopX = W - M - 20, rimY = floor - 240 * k * 1.62, rimR = 30 * k;
  const TOTAL = 26;
  // scene timing (seconds of the Short)
  const JUMP = C.play_type === 'jumper';
  const P0 = 0.25, PLAY = 5.2, FT0 = 5.6, R0 = 7.6, R_FROM = JUMP ? 0.9 : 1.5, R_TO = JUMP ? 3.7 : 4.5, R_SPEED = 0.42, FIN0 = 15.2, END0 = 21.5;
  const R1 = R0 + (R_TO - R_FROM) / R_SPEED;

  const defs = S('defs', {}, svg);
  const glow = S('filter', {id: 'glow', x: '-50%', y: '-50%', width: '200%', height: '200%'}, defs);
  S('feGaussianBlur', {stdDeviation: 6, result: 'b'}, glow);
  const mg = S('feMerge', {}, glow); S('feMergeNode', {in: 'b'}, mg); S('feMergeNode', {in: 'SourceGraphic'}, mg);

  // ---------- play layer ----------
  const play = S('g', {}, svg);
  T(play, M, 92, C.kicker, 'k', 26);
  const hook1 = T(play, M, 170, C.hook[0], 'd', 74), hook2 = T(play, M, 250, C.hook[1], 'd', 74);
  // scoreboard + clock
  const sb = S('g', {}, play);
  S('rect', {x: M, y: 296, width: W - 2 * M, height: 88, rx: 16, fill: 'rgba(0,0,0,.28)'}, sb);
  const sbUs = T(sb, M + 28, 356, '', 'd', 44), sbThem = T(sb, M + 300, 356, '', 'd', 44);
  sbThem.style.fill = 'var(--muted)';
  T(sb, W - M - 28, 356, C.clock, 'k', 30, 'end').style.fill = 'var(--ink)';
  const slowTag = S('g', {opacity: 0}, play);
  S('rect', {x: W - M - 250, y: 410, width: 250, height: 52, rx: 26, fill: 'none', stroke: 'var(--red)', 'stroke-width': 2.5}, slowTag);
  T(slowTag, W - M - 125, 445, 'SLOW MOTION', 'k', 24, 'middle').style.fill = 'var(--red)';
  // court
  const court = S('g', {class: 's-silver', 'stroke-width': 3, 'stroke-linecap': 'round', opacity: .9}, play);
  S('line', {x1: -20, x2: W + 20, y1: floor, y2: floor}, court);
  S('line', {x1: hoopX + 40 * k, x2: hoopX + 40 * k, y1: rimY - 120 * k, y2: floor}, court);
  const laneX = C.three ? hoopX - 560 * k / 1.5 : hoopX - 345 * k; S('line', {x1: laneX, x2: laneX, y1: floor - 6, y2: floor + 16}, court);
  T(play, laneX, floor + 40, C.three ? '3-pt line' : 'lane', 'b m', 22, 'middle');
  S('rect', {x: hoopX + 26 * k, y: rimY - 150 * k, width: 12 * k, height: 170 * k, rx: 3, fill: 'var(--silver)'}, play);
  S('line', {x1: hoopX - rimR, x2: hoopX + 26 * k, y1: rimY, y2: rimY, class: 's-red', 'stroke-width': 6, 'stroke-linecap': 'round'}, play);
  const net = S('g', {class: 's-silver', 'stroke-width': 2, opacity: .8}, play);
  // signature finish (per star): 'splash' = Steph's gold arc, backspin, the net snapping, rings and droplets, then SPLASH
  const SIG = C.signature || null, GOLD = C.gold || '#FFC72C', FXC = SIG === 'splash' ? GOLD : (C.accent || '#FF5A1F');
  const netL = Array.from({length: 5}, () => S('line', {}, net));
  const drawNet = (snap) => netL.forEach((l, i) => { const L = 44 * k * (1 + .55 * snap), tp = hoopX - rimR + i * rimR / 2, bt = hoopX - rimR * (.55 - .18 * snap) + i * rimR * (1.1 - .36 * snap) / 4; l.setAttribute('x1', tp); l.setAttribute('y1', rimY); l.setAttribute('x2', bt); l.setAttribute('y2', rimY + L); });
  drawNet(0);
  const rings = [0, 1, 2].map(() => S('ellipse', {cx: hoopX, cy: rimY + 4, rx: 0, ry: 0, fill: 'none', stroke: FXC, 'stroke-width': 3, opacity: 0}, play));
  const drops = SIG === 'splash' ? Array.from({length: 16}, (_, i) => ({a: -Math.PI / 2 + (i / 15 - .5) * 2.6, v: 260 + (i * 53) % 170, r: 7 + (i * 7) % 6, n: S('circle', {r: 6, fill: i % 3 ? '#cfe6ff' : GOLD, opacity: 0}, play)})) : [];
  // figures
  const defender = figure(play, 'opp', k); defender.g.setAttribute('opacity', .85);
  const ghosts = [0, 1, 2].map(() => { const gh = figureReal(play, 'phi', k, C.number, BUILD); gh.g.style.opacity = 0; return gh; }).reverse();
  const star = figureReal(play, 'phi', k, C.number, BUILD);
  const burst = S('g', {class: 's-red', 'stroke-width': 5, 'stroke-linecap': 'round', opacity: 0}, play);
  for (let i = 0; i < 5; i++) { const a = -Math.PI / 2 + (i - 2) * 0.5; S('line', {x1: Math.cos(a) * 26, y1: Math.sin(a) * 26, x2: Math.cos(a) * 52, y2: Math.sin(a) * 52}, burst); }
  const trail = S('path', {fill: 'none', stroke: FXC, 'stroke-width': 5, 'stroke-linecap': 'round', opacity: .8, filter: 'url(#glow)'}, play);
  const sparks = Array.from({length: 12}, () => S('circle', {r: 3.5, fill: FXC, opacity: 0}, play));
  const ball = S('circle', {r: 13 * k, class: 'f-ink', filter: 'url(#glow)'}, play);
  const seam = S('path', {d: `M${-13 * k} 0L${13 * k} 0M0 ${-13 * k}Q${7 * k} 0 0 ${13 * k}`, stroke: 'rgba(17,18,20,.55)', 'stroke-width': 2.4, fill: 'none'}, play);
  const flash = S('circle', {cx: hoopX, cy: rimY, r: 0, fill: 'none', stroke: 'var(--ink)', 'stroke-width': 4, opacity: 0}, play);
  const stamp = T(play, hoopX - 40, rimY - 120, C.stamp, 'd', 78, 'end'); stamp.style.fill = FXC;
  const sigWord = SIG === 'splash' ? T(play, hoopX - 40, rimY - 50, 'SPLASH', 'd', 60, 'end') : null; if (sigWord) { sigWord.style.fill = GOLD; sigWord.style.opacity = 0; }
  const ftG = S('g', {opacity: 0}, play);
  const BEAT = C.ft_line || C.beat; if (!C.score_ft) C.score_ft = C.score_make;
  T(ftG, M, floor + 130, BEAT[0], 'd', 54);
  T(ftG, M, floor + 190, BEAT[1], 'b m', 36);
  T(play, M, H - 56, 'Original illustration · not traced from footage, not to scale', 'b m', 22);

  // the play, as a function of play-time pt (0..PLAY). Types: 'drive' (default: drive, contact, floater) and 'jumper' (pull-up / catch-and-shoot, two or three)
  let x0, xG, tG, tC, tR, tM, peak, starAt, defAt;
  if (JUMP) {
    const three = !!C.three; xG = hoopX - (three ? 560 : 380) * k / 1.5; x0 = xG - 130 * k;
    tG = 1.15; tC = -9; tR = 1.75; tM = tR + (three ? 1.25 : 1.0); peak = three ? 230 : 190;
    starAt = (pt) => {
      if (pt < tG) { const x = lerp(x0, xG, inout(clamp(pt / tG))); const c = Math.sin(pt * 8) * .5 + .5; return [mixPose(POSES.run1, POSES.run2, c), x, 0]; }
      if (pt < tG + .3) return [mixPose(POSES.run1, POSES.set, prog(pt, tG, .25)), xG, 0];
      if (pt < tR + .1) { const u = clamp((pt - tG - .3) / (tR + .1 - tG - .3)); return [mixPose(POSES.set, POSES.rise, ease(u)), xG, 54 * Math.sin(Math.PI / 2 * u)]; }
      const d = clamp((pt - tR - .1) / .55); return [mixPose(POSES.rise, POSES.dribble, d), xG, 54 * (1 - d * d)];
    };
    defAt = (pt, x) => { // closes out and contests the release
      const dx = lerp(xG + 300 * k, xG + 125 * k, prog(pt, .3, tR - .2)); let pose = POSES.guard, l = 0;
      if (pt > tR - .45) { pose = mixPose(POSES.guard, POSES.contest, prog(pt, tR - .45, .3)); l = 26 * Math.sin(Math.PI * clamp((pt - tR + .45) / .8)); }
      if (pt > tR + .5) pose = mixPose(POSES.contest, POSES.guard, prog(pt, tR + .5, .4));
      return [pose, dx, l];
    };
  } else {
    x0 = 70; xG = hoopX - 300 * k; tG = 2.2; tC = 2.45; tR = 2.95; tM = 4.0; peak = 200;
    starAt = (pt) => {
      let x, pose, lift = 0;
      if (pt < tG) { const p = clamp(pt / tG); x = lerp(x0, xG, inout(p)); const c = Math.sin(pt * 9) * .5 + .5; pose = mixPose(POSES.run1, POSES.run2, c); }
      else if (pt < tR - .15) { x = xG + 10 * k * prog(pt, tG, .3); pose = mixPose(POSES.run1, POSES.gather, prog(pt, tG, .25)); }
      else if (pt < tR + .5) { x = xG + 10 * k; const u = prog(pt, tR - .15, .3); pose = mixPose(POSES.gather, POSES.float, u); lift = 34 * u; }
      else { x = xG + 10 * k; const d = clamp((pt - tR - .5) / .5); pose = mixPose(POSES.float, POSES.land, d); lift = 34 * (1 - d * d); }
      return [pose, x, lift];
    };
    defAt = (pt, x) => { // backpedals ahead of the drive, steps in for the contact, then contests
      let dx = Math.min(x + 150 * k, xG + 120 * k), dPose = POSES.guard, dLift = 0;
      if (pt > tG) { dx = lerp(xG + 120 * k, xG + 92 * k, prog(pt, tG, .25)); dPose = pt < tC + .3 ? mixPose(POSES.guard, POSES.bump, prog(pt, tG, .25)) : mixPose(POSES.bump, POSES.contest, prog(pt, tC + .3, .3)); dLift = pt > tC + .3 && pt < tM ? 18 * prog(pt, tC + .3, .3) : 0; }
      return [dPose, dx, dLift];
    };
  }
  const rel = (() => { const [p, x, l] = starAt(tR); const at = star.draw(p, x, floor - l * k, k, 1); const h = JUMP ? [(at('lh')[0] + at('rh')[0]) / 2, (at('lh')[1] + at('rh')[1]) / 2 - 16 * k] : at('rh'); return JUMP ? h : [h[0] + 6 * k, h[1] - 12 * k]; })();
  const arcAt = (u) => [lerp(rel[0], hoopX, u), lerp(rel[1], rimY - 6, u) - 4 * peak * u * (1 - u)];
  const trailTo = (u) => { const n = Math.max(1, Math.round(u * 60)); trail.setAttribute('d', u <= 0 ? 'M0 0' : 'M' + Array.from({length: n + 1}, (_, i) => arcAt(i / n * u)).map(([x, y]) => `${x.toFixed(1)} ${y.toFixed(1)}`).join('L')); };

  const drawPlay = (pt, slow) => {
    const [pose, x, lift] = starAt(pt);
    // his movement into the shot leaves a fading afterimage trail (as in the signature pieces)
    ghosts.forEach((gh, i) => {
      const on = pt > .3 && pt < tG + .2;
      if (!on) { gh.g.style.opacity = 0; return; }
      const [gp, gx, gl] = starAt(pt - (i + 1) * .07);
      gh.draw(gp, gx, floor - gl * k, k, 1); gh.g.style.opacity = ((.42 - i * .12) * (1 - prog(pt, tG - .1, .3))).toFixed(2);
    });
    const at = star.draw(pose, x, floor - lift * k, k, 1);
    const [dPose, dx, dLift] = defAt(pt, x);
    defender.draw(dPose, dx, floor - dLift * k, k, -1);
    // contact burst (drives only)
    const cOn = pt > tC - .05 && pt < tC + .6;
    burst.setAttribute('transform', `translate(${(x + dx) / 2} ${floor - 175 * k})`);
    burst.setAttribute('opacity', cOn ? (1 - prog(pt, tC + .25, .35)).toFixed(2) : 0);
    // ball
    let bx, by;
    if (pt < tG) { const [hx, hy] = at('rh'); const ph = (pt * 3.2) % 1, f = ph < .5 ? ph * 2 : (1 - ph) * 2; bx = hx + 8 * k; by = lerp(hy, floor - 13 * k, f * f * (3 - 2 * f)); }
    else if (pt < tR) { if (JUMP) { bx = (at('lh')[0] + at('rh')[0]) / 2; by = (at('lh')[1] + at('rh')[1]) / 2 - 16 * k; } else { const [hx, hy] = at('rh'); bx = hx + 4 * k; by = hy - 10 * k; } }
    else if (pt < tM) { const u = clamp((pt - tR) / (tM - tR)); [bx, by] = arcAt(u); trailTo(u); }
    else { const d = clamp((pt - tM) / .6); bx = hoopX - 4; by = lerp(rimY - 6, floor - 13 * k, d * d); }
    if (pt < tR) trailTo(0); else if (pt >= tM) trailTo(1);
    trail.setAttribute('opacity', pt < tM ? .8 : (.8 * (1 - prog(pt, tM, .45))).toFixed(2));
    ball.setAttribute('cx', bx); ball.setAttribute('cy', by);
    // the finish every star gets: backspin, sparks off the arc, the net snapping, rings off the rim; Steph adds the splash
    const spin = pt < tR ? 0 : -(Math.min(pt, tM) - tR) * 1440 - Math.max(0, pt - tM) * 600;
    seam.setAttribute('transform', `translate(${bx.toFixed(1)} ${by.toFixed(1)}) rotate(${spin.toFixed(0)})`);
    sparks.forEach((sk, i) => { const su = (i + .5) / sparks.length, born = tR + su * (tM - tR), age = pt - born;
      if (age < 0 || age > 1.1) { sk.setAttribute('opacity', 0); return; }
      const [sx, sy] = arcAt(su); sk.setAttribute('cx', sx + Math.sin(i * 2.1) * 10 * age); sk.setAttribute('cy', sy + 70 * age * age + 20 * age); sk.setAttribute('opacity', (1 - age / 1.1).toFixed(2)); });
    const sp = pt - tM;
    drawNet(sp > 0 ? (sp < .5 ? Math.sin(Math.PI * sp / .5) : .25 * Math.sin(Math.PI * clamp((sp - .5) / .4))) : 0);
    rings.forEach((r, i) => { const a = sp - i * .14; if (a < 0 || a > 1) { r.setAttribute('opacity', 0); return; } const e = ease(a); r.setAttribute('rx', rimR + 150 * e); r.setAttribute('ry', 10 + 34 * e); r.setAttribute('opacity', (1 - a).toFixed(2)); });
    drops.forEach((d) => { const a = sp - .02; if (a < 0 || a > 1) { d.n.setAttribute('opacity', 0); return; } d.n.setAttribute('cx', hoopX + Math.cos(d.a) * d.v * a); d.n.setAttribute('cy', rimY + 30 * k + Math.sin(d.a) * d.v * a + 520 * a * a); d.n.setAttribute('r', d.r * (1 - a * .5)); d.n.setAttribute('opacity', (1 - a).toFixed(2)); });
    if (sigWord) { sigWord.style.opacity = sp > .55 ? prog(pt, tM + .55, .25) : 0; sigWord.setAttribute('transform', `translate(0 ${sp > .55 ? 14 * (1 - prog(pt, tM + .55, .3)) : 14})`); }
    const made = pt >= tM;
    flash.setAttribute('opacity', 0);
    stamp.style.opacity = made ? prog(pt, tM + .05, .25) : 0;
    stamp.setAttribute('transform', `scale(${made ? 1 + .25 * (1 - prog(pt, tM + .05, .25)) : 1})`); stamp.style.transformOrigin = `${hoopX - 40}px ${rimY - 120}px`;
    slowTag.setAttribute('opacity', slow ? 1 : 0);
  };

  // ---------- final + end cards ----------
  const fin = S('g', {opacity: 0}, svg);
  S('rect', {width: W, height: H, fill: 'var(--navy)'}, fin);
  T(fin, M, 200, C.final.label, 'k', 28);
  T(fin, M, 300, `${C.final.us} ${C.final.us_pts}`, 'd', 96);
  T(fin, M, 400, `${C.final.them} ${C.final.them_pts}`, 'd', 96).style.fill = 'var(--muted)';
  S('line', {x1: M, x2: W - M, y1: 470, y2: 470, class: 's-silver', 'stroke-width': 2, opacity: .5}, fin);
  T(fin, M, 540, C.star.name, 'b', 40).style.fontWeight = 600;
  const bigN = T(fin, M - 6, 760, '0', 'd', 240); bigN.style.fill = 'var(--red)';
  T(fin, M, 830, C.star.big_label, 'b', 38);
  C.star.lines.forEach((l, i) => T(fin, M, 920 + i * 60, '· ' + l, 'b m', 36));
  const story = T(fin, M, 1120, '', 'b', 34);
  (() => { const words = C.story.split(' '); let line = S('tspan', {x: M}, story), n = 0; words.forEach((w) => { const prev = line.textContent; line.textContent = prev ? prev + ' ' + w : w; if (line.getComputedTextLength && line.getComputedTextLength() > W - 2 * M && prev) { line.textContent = prev; line = S('tspan', {x: M, dy: '1.3em'}, story); line.textContent = w; } }); })();

  const endc = S('g', {opacity: 0}, svg);
  S('rect', {width: W, height: H, fill: '#111214'}, endc);
  const lg = S('g', {transform: `translate(${W / 2 - 120} 430) scale(1)`}, endc);
  S('rect', {x: 0, y: 0, width: 240, height: 240, rx: 44, fill: 'none', stroke: '#fff', 'stroke-width': 26}, lg);
  S('path', {d: 'M58 52 L112 106 M112 52 L58 106', stroke: '#fff', 'stroke-width': 26, 'stroke-linecap': 'round'}, lg);
  [[92, 150], [104, 186], [130, 214]].forEach(([cx, cy]) => S('circle', {cx, cy, r: 12, fill: '#FF5A1F'}, lg));
  S('circle', {cx: 182, cy: 190, r: 34, fill: 'none', stroke: '#FF5A1F', 'stroke-width': 24}, lg);
  T(endc, W / 2, 800, 'BOX & MOTION HOOPS', 'd', 56, 'middle');
  const tg = T(endc, W / 2, 870, 'The box score, in motion.', 'b', 38, 'middle'); tg.style.fill = '#FF5A1F';
  // where to go next, readable in a glance: Shorts links aren't clickable, so the address has to be big enough to remember
  // (everything stays above y 1200 and away from the right edge, clear of the Shorts title bar and buttons)
  T(endc, W / 2, 990, "Every game's full recap", 'b m', 32, 'middle');
  const url = T(endc, W / 2, 1068, 'boxandmotion.com', 'd', 64, 'middle'); url.style.fill = '#fff';
  S('rect', {x: W / 2 - 150, y: 1090, width: 300, height: 8, rx: 4, fill: '#FF5A1F'}, endc);
  T(endc, W / 2, 1170, 'Free Sunday newsletter: link on our channel', 'b m', 30, 'middle');

  // ---------- timeline ----------
  const render = (t) => {
    let pt, slow = false;
    if (t < FT0) pt = clamp((t - P0) / 1) * 0 + Math.max(0, Math.min(PLAY, t - P0));
    else if (t < R0) pt = PLAY;
    else if (t < R1) { pt = R_FROM + (t - R0) * R_SPEED; slow = true; }
    else pt = PLAY;
    drawPlay(pt, slow);
    // score: before, after the make, after the free throw
    const s = C.margins ? [0, 0] : t >= FT0 + .4 && t < R0 ? C.score_ft : (t >= P0 + tM && t < R0) ? C.score_make : (t >= R1 ? C.score_ft : C.score_before);
    if (C.margins) { // only the margin is verified at that moment: "Lakers +4" -> "Lakers +6"
      sbUs.textContent = (t >= P0 + tM && t < R0) || t >= R1 ? C.margins[1] : C.margins[0]; sbThem.textContent = ''; sbUs.style.fill = 'var(--ink)';
    } else {
      sbUs.textContent = `${C.us} ${s[0]}`; sbThem.textContent = `${C.them} ${s[1]}`;
      sbUs.style.fill = s[0] > s[1] ? 'var(--ink)' : 'var(--muted)'; sbThem.style.fill = s[1] > s[0] ? 'var(--ink)' : 'var(--muted)';
    }
    ftG.setAttribute('opacity', t >= FT0 && t < R0 ? prog(t, FT0, .3) : 0);
    hook1.style.opacity = hook2.style.opacity = 1;
    // final card
    const fo = t >= FIN0 ? prog(t, FIN0, .35) : 0; fin.setAttribute('opacity', t >= END0 ? 1 - prog(t, END0, .3) : fo);
    bigN.textContent = String(Math.round(C.star.big * prog(t, FIN0 + .4, 1.4)));
    endc.setAttribute('opacity', t >= END0 ? prog(t, END0, .35) : 0);
  };
  let time = 0, last = null;
  const frame = (now) => { if (last != null) { time += (now - last) / 1000; if (time > TOTAL) time = 0; } last = now; if (!window.__hold) render(time); requestAnimationFrame(frame); };
  render(0); requestAnimationFrame(frame);
  window.__A = {render, build: () => {}, total: TOTAL};
})();
</script>
</body></html>
"""
out = (HTML.replace('__KITCSS__', KITCSS).replace('__PAL__', PAL).replace('__FIGURE__', FIGURE).replace('__FIGURE_REAL__', FIGURE_REAL)
       .replace('__TITLE__', html.escape(' '.join(CFG['hook']))).replace('__ARIA__', html.escape(CFG['aria'])).replace('__CFG__', json.dumps(CFG, ensure_ascii=False)))
dst = os.path.join(ROOT, 'src', 'anim', CFG['out'])
open(dst, 'w').write(out)
print('wrote', os.path.relpath(dst, ROOT))
# YouTube thumbnail: half a second after the make, when the hook title, the stamp (DAGGER, AND-ONE...) and the star are all
# on screen. Same timing as the JS (P0 + tM + 0.5); the MP4 runs at speed 1, so animation time = video time.
_tm = (1.75 + (1.25 if CFG.get('three') else 1.0)) if CFG.get('play_type') == 'jumper' else 4.0
print('thumbnail offset (ms):', int(round((0.25 + _tm + 0.5) * 1000)))
