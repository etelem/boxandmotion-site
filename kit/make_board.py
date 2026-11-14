"""Build an animated coach's board (X's and O's) from a JSON config.
Usage (from the repo root): python3 kit/make_board.py kit/boards/<id>.json src/anim/<slug>.html

An original whiteboard drawing of a play: offense as numbered circles in team colors, defense as X's, cuts as solid
arrows, screens as T-bars, passes as dashed lines, the ball in orange. Only actions described in the cited sources are
drawn; where the sources don't give a spot, the page says positions are illustrative.

Coordinates are feet on a half court: x from -25 (offense's left sideline) to 25, y from 0 (baseline) to 47 (half line).
Config keys: team, kicker, title, situation, note, players {id: {x, y, num, name, side: 'o'|'d'}}, ball (holder id),
actions [{type: move|screen|pass|shot, t: [start, end], ...}], beats [{t, title, text}], clock {start, run, stop, end},
score {before, after, at}, final, sources [[label, url]], total (seconds).
Modes: ?embed=1 hides the page chrome, ?short=1 renders the 9:16 YouTube Shorts layout (no controls, brand footer).
window.__A = {render(t), build(), total} for frame export."""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
cfg = json.load(open(sys.argv[1])); out = sys.argv[2]
team = (json.load(open(os.path.join(ROOT, 'data', 'teams.json')))[cfg['team']] if cfg.get('team')
        else cfg.get('colors', {'c1': '#FF5A1F', 'c2': '#16181d'}))   # explainers (no team) use the brand colors

# optional drawn star (CFG.star = {id, name, num, home}): his approved look from kit/looks.json, drawn as a small standing
# figure on his spot instead of a numbered circle (dribbles, runs on his drive, turns and passes)
STAR_JS, STAR_CSS = '', ''
if cfg.get('star'):
    sys.path.insert(0, HERE)
    from looks import look_for, kit_for
    _st = cfg['star']; _look, _status, _sig = look_for(_st['name'])
    _st['build'] = {**_look, **_st.get('build', {})}
    _kit = kit_for(cfg['team'], _st.get('home', True))
    _base = open(os.path.join(HERE, 'base-reel.html')).read().split('\n')
    _a = next(i for i, l in enumerate(_base) if l.startswith('  const POSES = {'))
    _b = next(i for i in range(_a, len(_base)) if _base[i] == '  }' and i > _a + 12)
    STAR_JS = ('\n'.join(_base[_a:_b + 1]) + '\n' + open(os.path.join(HERE, 'figure-real.js')).read() + '''
  POSES.run1 = {head: [26, -222], neck: [20, -198], hip: [0, -122], lk: [30, -70], lf: [22, 0], rk: [-20, -62], rf: [-46, -12], le: [-4, -162], lh: [6, -130], re: [36, -160], rh: [54, -110]};
  POSES.run2 = {head: [26, -222], neck: [20, -198], hip: [0, -122], lk: [-20, -62], lf: [-46, -12], rk: [30, -70], rf: [22, 0], le: [-4, -162], lh: [6, -130], re: [36, -160], rh: [54, -110]};
  POSES.pass = {head: [10, -232], neck: [6, -208], hip: [0, -128], lk: [-14, -68], lf: [-24, 0], rk: [16, -70], rf: [26, 0], le: [34, -178], lh: [64, -182], re: [30, -170], rh: [62, -174]};''')
    STAR_CSS = (f".fig-o-star{{stroke:#16181d;fill:#16181d}}.fig-kit-star{{stroke:{_kit['jersey']};fill:{_kit['jersey']}}}"
                f".fig-skin{{stroke:#c99d7a;fill:#c99d7a}}.fig-num{{font-family:'Archivo',sans-serif;font-weight:800;fill:{_kit['number']}}}"
                f".fig-hair{{stroke:#3a2a1c;fill:#3a2a1c}}.fig-shoe{{stroke:#16181d;fill:#16181d}}.fig-band{{stroke:{_kit['number']};fill:none}}")

HTML = r"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>__TITLE__ · Box &amp; Motion Hoops</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@700;800&family=IBM+Plex+Mono:wght@500&family=IBM+Plex+Sans:wght@400;600&display=swap">
<style>
:root{--board:#f7f6f1;--ink:#16181d;--dim:#6b6f78;--line:#d9d7cf;--acc:#FF5A1F;--c1:__C1__;--c2:__C2__}
html,body{margin:0;background:transparent}
body{font-family:'IBM Plex Sans',system-ui,sans-serif;color:var(--ink)}
.wrap{background:var(--board);border:1px solid var(--line);border-radius:18px;overflow:hidden}
svg{display:block;width:100%;height:auto}
.bar{display:flex;flex-wrap:wrap;gap:8px;align-items:center;padding:0 16px 16px}
.bar button{font:600 14px/1 'IBM Plex Sans',system-ui,sans-serif;color:var(--ink);background:transparent;border:1.5px solid var(--ink);border-radius:999px;min-height:38px;padding:0 14px;cursor:pointer}
.bar button[aria-pressed="true"],.bar button.on{background:var(--ink);color:var(--board)}
.bar button:focus-visible{outline:2px solid var(--acc);outline-offset:2px}
.bar .sp{flex:1}
html.short .bar{display:none}
html.short .wrap,html.embed .wrap{border-radius:0;border:0}
.d{font-family:'Archivo',system-ui,sans-serif;font-weight:800;fill:var(--ink)}
.k{font-family:'IBM Plex Mono',monospace;font-weight:500;letter-spacing:.14em;text-transform:uppercase;fill:var(--acc)}
.b{font-family:'IBM Plex Sans',system-ui,sans-serif;fill:var(--ink)}
.m{fill:var(--dim)}
.court{fill:none;stroke:var(--ink);stroke-linecap:round;stroke-linejoin:round}
.beat{transition:opacity .2s}
__STARCSS__
html.short .beat{transition:none}
</style></head><body>
<div class="wrap">
<svg id="sv" role="img" aria-label="__ARIA__"></svg>
<div class="bar"><button id="pp" type="button">Pause</button><button id="slow" type="button" aria-pressed="false">Slow motion</button><button id="again" type="button">Replay</button><span class="sp"></span><span id="jumps"></span></div>
</div>
<script>
if (/[?&]embed=1/.test(location.search)) document.documentElement.classList.add('embed');
if (/[?&]short=1/.test(location.search)) document.documentElement.classList.add('short');
(function () {
  const CFG = __CFG__;
  // Music under the board (CFG.music; X's and O's use the owner's Streetball Groove since Nov 12, 2026; coach's boards default to Film Room). While it plays, the board follows the music's clock (sndClock), so nothing is re-synced mid-play;
  // Replay, the step buttons, pause, slow motion and the loop move the music once (sndSeek / sndRun).
  let sndBtn = null, sndTxt = null, sndOn = false, audio = null;
  function sndClock() {
    if (!sndOn || !audio || audio.paused || audio.seeking || audio.readyState < 3) return null;
    const c = audio.currentTime; audio.volume = Math.max(0, Math.min(1, (TOTAL + 1.5 - c) / 1.5)); return c;
  }
  function sndSeek(x) { if (sndOn && audio) { try { audio.currentTime = x; } catch (e) {} } }
  function sndRun(go, x) { if (!sndOn || !audio) return; if (go) { sndSeek(x); audio.play().catch(() => {}); } else audio.pause(); }
  function toggleSound() {
    sndOn = !sndOn;
    if (sndTxt) sndTxt.textContent = sndOn ? 'Mute' : '▶ Play with sound';
    if (!audio) { audio = new Audio(CFG.music || '../audio/film-room.mp3'); audio.preload = 'auto'; }
    if (sndOn) { document.getElementById('again').click(); audio.volume = 1; audio.currentTime = 0; audio.play().catch(() => { sndOn = false; if (sndTxt) sndTxt.textContent = 'Sound unavailable'; }); }
    else audio.pause();
  }
  const NS = 'http://www.w3.org/2000/svg';
  const S = (tag, a, p) => { const e = document.createElementNS(NS, tag); for (const k in a) e.setAttribute(k, a[k]); if (p) p.appendChild(e); return e; };
  const T = (p, x, y, txt, cls, size, anchor) => { const e = S('text', {x, y, class: cls, 'text-anchor': anchor || 'start'}, p); e.style.fontSize = size + 'px'; e.textContent = txt; return e; };
  const clamp = (v, a = 0, b = 1) => Math.max(a, Math.min(b, v));
  const lerp = (a, b, p) => a + (b - a) * p;
__STARJS__
  const ease = (p) => p < .5 ? 2 * p * p : 1 - Math.pow(-2 * p + 2, 2) / 2;
  const svg = document.getElementById('sv');
  const short = document.documentElement.classList.contains('short');
  const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  // "Find the open man" quiz (optional CFG.quiz = {t, hold, prompt, sub, answer, tag}): the board freezes at board time
  // quiz.t for quiz.hold seconds with a countdown and a "?" over every offensive player, then rings the answer and plays on.
  const Q = CFG.quiz || null, HOLD = Q ? Q.hold : 0;
  const TOTAL = CFG.total + HOLD;
  const BT = (t) => !Q || t < Q.t ? t : t < Q.t + HOLD ? Q.t : t - HOLD;   // play time -> board time
  // polyline helpers: length, point at fraction
  const plen = (pts) => { let L = 0; for (let i = 1; i < pts.length; i++) L += Math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]); return L; };
  const pat = (pts, f) => { const L = plen(pts) * clamp(f); let acc = 0; for (let i = 1; i < pts.length; i++) { const d = Math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]); if (acc + d >= L) { const q = d ? (L - acc) / d : 0; return [lerp(pts[i - 1][0], pts[i][0], q), lerp(pts[i - 1][1], pts[i][1], q)]; } acc += d; } return pts[pts.length - 1].slice(); };
  // smooth a polyline with Catmull-Rom so cuts curve like marker strokes
  const smooth = (pts) => { if (pts.length < 3) return pts; const o = []; for (let i = 0; i < pts.length - 1; i++) { const p0 = pts[Math.max(0, i - 1)], p1 = pts[i], p2 = pts[i + 1], p3 = pts[Math.min(pts.length - 1, i + 2)]; for (let s = 0; s < 8; s++) { const t = s / 8, t2 = t * t, t3 = t2 * t; o.push([0.5 * ((2 * p1[0]) + (-p0[0] + p2[0]) * t + (2 * p0[0] - 5 * p1[0] + 4 * p2[0] - p3[0]) * t2 + (-p0[0] + 3 * p1[0] - 3 * p2[0] + p3[0]) * t3), 0.5 * ((2 * p1[1]) + (-p0[1] + p2[1]) * t + (2 * p0[1] - 5 * p1[1] + 4 * p2[1] - p3[1]) * t2 + (-p0[1] + 3 * p1[1] - 3 * p2[1] + p3[1]) * t3)]); } } o.push(pts[pts.length - 1]); return o; };
  CFG.actions.forEach((a) => { if (a.path) a.sp = smooth(a.path); });
  // wrap a text element's words onto tspans no wider than maxW (returns the line count)
  const wrap = (tx, x, maxW) => { const words = tx.textContent.split(' '); tx.textContent = ''; let line = S('tspan', {x}, tx), n = 1;
    words.forEach((wd) => { const prev = line.textContent; line.textContent = prev ? prev + ' ' + wd : wd; if (line.getComputedTextLength() > maxW && prev) { line.textContent = prev; line = S('tspan', {x, dy: '1.25em'}, tx); line.textContent = wd; n += 1; } }); return n; };

  let L, draw;
  function build() {
    const tall = short || svg.parentNode.getBoundingClientRect().width < 700;
    const W = short ? 900 : tall ? 800 : 1280, H = short ? 1600 : tall ? 1580 : 780, M = short ? 56 : 40;
    let s, cx, cy, top;
    // 5 extra feet on the left so a sideline inbounder and his name fit
    if (short) { top = 300; s = (W - 2 * M) / 55; }
    else if (tall) { top = 190; s = (W - 2 * M) / 55; }
    else { top = 160; s = (H - top - 56) / 47; }
    cx = tall ? M + 30 * s : M + 30 * s; cy = top;   // court origin: center of the baseline
    const P = (x, y) => [cx + x * s, cy + y * s];
    L = {W, H, M, s, P, tall, short};
    svg.setAttribute('viewBox', `0 0 ${W} ${H}`);
    svg.replaceChildren();
    const defs = S('defs', {}, svg);
    const mk = (id, col) => { const m = S('marker', {id, viewBox: '0 0 10 10', refX: 6, refY: 5, markerWidth: 5, markerHeight: 5, orient: 'auto-start-reverse'}, defs); S('path', {d: 'M0 0L10 5L0 10z', fill: col}, m); };
    mk('ar-ink', '#16181d'); mk('ar-acc', '#FF5A1F');
    const F = (v) => v.toFixed(1);
    // header
    const ks = short ? 26 : tall ? 20 : 16, ts = short ? 64 : tall ? 46 : 40;
    T(svg, M, short ? 96 : M + 14, CFG.kicker, 'k', ks);
    const title = T(svg, M, (short ? 96 : M + 14) + ts + 6, CFG.title, 'd', ts);
    // long titles shrink to fit the width instead of running off the board
    if (title.getComputedTextLength && title.getComputedTextLength() > W - 2 * M) title.style.fontSize = (ts * (W - 2 * M) / title.getComputedTextLength()) + 'px';
    T(svg, M, (short ? 96 : M + 14) + ts + 6 + (short ? 50 : 30), CFG.situation, 'b m', short ? 30 : tall ? 22 : 18);
    // court
    const g = S('g', {class: 'court', 'stroke-width': F(s * 0.22)}, svg);
    const [x0, y0] = P(-25, 0), [x1, y1] = P(25, 47);
    S('rect', {x: F(x0), y: F(y0), width: F(x1 - x0), height: F(y1 - y0), rx: F(s * 0.6)}, g);
    const [px0, py0] = P(-8, 0), [px1, py1] = P(8, 19);
    S('rect', {x: F(px0), y: F(py0), width: F(px1 - px0), height: F(py1 - py0)}, g);
    const [fc, fy] = P(0, 19); S('circle', {cx: F(fc), cy: F(fy), r: F(6 * s)}, g);
    const arcR = 23.75 * s, [hx, hy] = P(0, 5.25), cornerY = 5.25 + Math.sqrt(23.75 * 23.75 - 22 * 22);
    const [lx0, ly0] = P(-22, 0), [lx1, ly1] = P(-22, cornerY), [rx1, ry1] = P(22, cornerY), [rx0, ry0] = P(22, 0);
    S('path', {d: `M${F(lx0)} ${F(ly0)}L${F(lx1)} ${F(ly1)}A${F(arcR)} ${F(arcR)} 0 0 0 ${F(rx1)} ${F(ry1)}L${F(rx0)} ${F(ry0)}`}, g);
    const [bx0, by] = P(-3, 4), [bx1] = P(3, 4); S('path', {d: `M${F(bx0)} ${F(by)}L${F(bx1)} ${F(by)}`, 'stroke-width': F(s * 0.35)}, g);
    S('circle', {cx: F(hx), cy: F(hy), r: F(0.9 * s), stroke: '#FF5A1F'}, g);
    const [hc, hcy] = P(0, 47); S('path', {d: `M${F(hc - 6 * s)} ${F(hcy)}A${F(6 * s)} ${F(6 * s)} 0 0 1 ${F(hc + 6 * s)} ${F(hcy)}`}, g);
    // clock and score
    // sound: a "Play with sound" button right under the court (site and standalone only, never in the Short)
    const SND = !short, sndH = SND && tall ? 62 : 0;
    const sbY = tall ? y1 + (short ? 70 : (CFG.score || CFG.clock ? 52 : 4)) + sndH : top - 6, sbX = tall ? M : x1 + 40;   // explainers have no score row
    if (SND) {
      const bw = tall ? 270 : 210, bh = tall ? 46 : 38, bx = tall ? M : W - M - bw, by = tall ? y1 + 16 : H - bh - 12;
      sndBtn = S('g', {role: 'button', tabindex: 0, 'aria-label': 'Play with sound', style: 'cursor:pointer'}, svg);
      S('rect', {x: bx, y: by, width: bw, height: bh, rx: bh / 2, fill: 'var(--board)', stroke: '#FF5A1F', 'stroke-width': 2}, sndBtn);
      sndTxt = T(sndBtn, bx + bw / 2, by + bh * 0.66, sndOn ? 'Mute' : '▶ Play with sound', 'b', tall ? 21 : 16, 'middle'); sndTxt.style.fontWeight = 600;
      sndBtn.addEventListener('click', toggleSound);
      sndBtn.addEventListener('keydown', (e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); toggleSound(); } });
    }
    const clock = T(svg, tall ? W - M : W - M, tall ? sbY : M + 14 + ts + 6, '', 'd', short ? 64 : tall ? 44 : 40, 'end');
    const score = T(svg, tall ? M : x1 + 40, tall ? sbY : M + 14 + ts + 6, '', 'd', short ? 44 : tall ? 30 : 26);
    if (!tall) { clock.setAttribute('y', top + 40); score.setAttribute('y', top + 40); }
    // beats panel
    const beats = CFG.beats.map((b, i) => {
      let x, y, w;
      if (short) { x = M; y = sbY + 90; w = W - 2 * M; }
      else if (tall) { x = M; y = sbY + 44 + i * 112; w = W - 2 * M; }
      else { x = x1 + 40; y = top + 100 + i * 92; w = W - M - x; }
      const bg = S('g', {class: 'beat'}, svg);
      const ns = short ? 56 : tall ? 36 : 30;
      T(bg, x, y + ns, String(i + 1), 'd', ns);
      T(bg, x + ns * 1.1, y + ns * 0.78, b.title, 'd', short ? 50 : tall ? 30 : 24);
      const tx = T(bg, x + ns * 1.1, y + ns * 0.78 + (short ? 58 : tall ? 36 : 30), b.text, 'b', short ? 38 : tall ? 24 : 17);
      // wrap the description to the panel width
      wrap(tx, x + ns * 1.1, w - ns * 1.1);
      return bg;
    });
    const note = T(svg, M, short ? H - 170 : H - (tall ? 52 : 22), CFG.note, 'b m', short ? 24 : tall ? 18 : 14); if (short || tall) wrap(note, M, W - 2 * M);
    if (short) {
      T(svg, M, H - 70, 'BOX & MOTION HOOPS', 'd', 36);
      T(svg, W - M, H - 70, 'boxandmotion.com', 'b m', 28, 'end');
    }
    // layers: trails under players
    const trails = S('g', {}, svg), marks = S('g', {}, svg), people = S('g', {}, svg), top2 = S('g', {}, svg);
    const trailEls = CFG.actions.map((a) => {
      if (a.type === 'move' && a.trail !== false) {
        const d = 'M' + a.sp.map((p) => P(p[0], p[1]).map(F).join(' ')).join('L');
        const acc = !!a.key;
        const el = S('path', {d, fill: 'none', stroke: acc ? '#FF5A1F' : '#16181d', 'stroke-width': F(s * (acc ? 0.34 : 0.26)), 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'marker-end': `url(#ar-${acc ? 'acc' : 'ink'})`}, trails);
        const len = el.getTotalLength(); el.style.strokeDasharray = len; el.style.strokeDashoffset = len; el.__len = len; return el;
      }
      if (a.type === 'pass') { const el = S('path', {fill: 'none', stroke: '#16181d', 'stroke-width': F(s * 0.24), 'stroke-dasharray': `${F(s)} ${F(s * 0.7)}`, 'stroke-linecap': 'round', 'marker-end': 'url(#ar-ink)'}, trails); return el; }
      if (a.type === 'screen') { return S('path', {fill: 'none', stroke: '#16181d', 'stroke-width': F(s * 0.42), 'stroke-linecap': 'round'}, marks); }
      return null;
    });
    // players
    const R = 1.45 * s;
    const peeps = {};
    Object.entries(CFG.players).forEach(([id, p]) => {
      const pg = S('g', {}, people);
      if (p.side === 'd') {
        const d = 0.95 * s;
        S('path', {d: `M${-d} ${-d}L${d} ${d}M${d} ${-d}L${-d} ${d}`, stroke: '#7d828c', 'stroke-width': F(s * 0.36), 'stroke-linecap': 'round'}, pg);
      } else {
        S('circle', {r: F(R), fill: 'var(--c1)', stroke: '#16181d', 'stroke-width': F(s * 0.14)}, pg);
        const n = T(pg, 0, R * 0.42, String(p.num), 'd', R * 1.2, 'middle'); n.style.fill = '#fff';
        if (p.name) { const nm = T(pg, 0, R + (short ? 30 : 20), p.name, 'b', short ? 24 : tall ? 16 : 15, 'middle'); nm.style.fontWeight = 600; }
      }
      peeps[id] = pg;
    });
    const SP = CFG.star || null; let star = null, starName = null, starHand = null, starHead = null;
    if (SP) {
      peeps[SP.id].style.display = 'none';
      star = figureReal(people, 'star', s * 0.048, SP.num, SP.build || {});
      starName = T(people, 0, 0, SP.label || '', 'b', short ? 24 : tall ? 16 : 15, 'middle'); starName.style.fontWeight = 600;
    }
    // where the ball leaves his hands on a pass (the pass pose's hands, facing the pass)
    const starRelease = (a) => { const [fx, fy] = P(...posAt(SP.id, a.t[0])), K = s * 0.048 * ((SP.build || {}).tall || 1), d = SP.passDir || -1; return [fx + d * 66 * K, fy - 152 * K]; };
    const starDraw = (t) => {
      const [fx, fy] = P(...posAt(SP.id, t)), K = s * 0.048 * ((SP.build || {}).tall || 1);
      const drive = CFG.actions.find((a) => a.type === 'move' && a.who === SP.id), pass = CFG.actions.find((a) => a.type === 'pass' && a.from === SP.id);
      let pose = POSES.dribble, dir = 1, hasBall = true;
      if (drive && t >= drive.t[0] && t < drive.t[1]) { const c = Math.sin((t - drive.t[0]) * 9) * .5 + .5; pose = mixPose(POSES.run1, POSES.run2, c); }
      if (pass && t >= pass.t[0] - 0.3) { dir = SP.passDir || -1; pose = mixPose(POSES.dribble, POSES.pass, clamp((t - pass.t[0] + 0.3) / 0.3)); hasBall = t < pass.t[0]; }
      star.draw(pose, fx, fy, 1, dir);
      starHead = [fx + dir * pose.head[0] * K, fy + pose.head[1] * K];
      const bob = pose === POSES.dribble ? Math.abs(Math.sin(t * 7)) : 0.5;
      starHand = [fx + dir * (pose.rh[0] + 4) * K, fy + (pose.rh[1] + 22 + 70 * bob * (pose === POSES.dribble ? 1 : 0)) * K];
      if (!hasBall) starHand = null;
      starName.setAttribute('x', F(fx)); starName.setAttribute('y', F(fy + (short ? 30 : 20)));
    };
    const ball = S('circle', {r: F(0.62 * s), fill: '#FF5A1F', stroke: '#16181d', 'stroke-width': F(s * 0.1)}, top2);
    const plus = T(top2, 0, 0, (CFG.actions.find((a) => a.type === 'shot') || {}).plus || '+3', 'd', short ? 72 : 48, 'middle'); plus.style.fill = '#FF5A1F';

    // where is a player at time t (feet)
    const posAt = (id, t) => {
      let p = [CFG.players[id].x, CFG.players[id].y];
      CFG.actions.forEach((a) => { if (a.type === 'move' && a.who === id && t >= a.t[0]) p = pat(a.sp, ease(clamp((t - a.t[0]) / (a.t[1] - a.t[0])))); });
      return p;
    };
    const fmtClock = (v) => v.toFixed(1);
    draw = (t) => {
      Object.keys(peeps).forEach((id) => { const [x, y] = P(...posAt(id, t)); peeps[id].setAttribute('transform', `translate(${F(x)} ${F(y)})`); });
      CFG.actions.forEach((a, i) => {
        const el = trailEls[i]; if (!el) return;
        const p = clamp((t - a.t[0]) / (a.t[1] - a.t[0]));
        if (a.type === 'move') { el.style.strokeDashoffset = el.__len * (1 - ease(p)); el.style.opacity = p <= 0 ? 0 : t > a.t[1] + 2.2 ? .35 : 1; el.setAttribute('marker-end', p > .96 ? `url(#ar-${a.key ? 'acc' : 'ink'})` : ''); }
        if (a.type === 'pass') {
          const A = P(...posAt(a.from, a.t[0])), B = P(...posAt(a.to, a.t[1]));
          const q = ease(p), E = [lerp(A[0], B[0], q), lerp(A[1], B[1], q)];
          el.setAttribute('d', t < a.t[0] ? 'M0 0' : `M${F(A[0])} ${F(A[1])}L${F(E[0])} ${F(E[1])}`);
        }
        if (a.type === 'screen') {
          const on = t >= a.t[0] ? clamp((t - a.t[0]) / 0.3) : 0;
          const [x, y] = P(...posAt(a.who, a.t[0])), ang = a.angle * Math.PI / 180, r = R + 0.5 * s, w = 1.4 * s * on;
          const c = [x + Math.cos(ang) * r, y + Math.sin(ang) * r], n = [-Math.sin(ang), Math.cos(ang)];
          el.setAttribute('d', on ? `M${F(c[0] - n[0] * w)} ${F(c[1] - n[1] * w)}L${F(c[0] + n[0] * w)} ${F(c[1] + n[1] * w)}` : 'M0 0');
        }
      });
      if (SP) starDraw(t);
      // ball: with the holder, along a pass, or on the shot
      let bp = P(...posAt(CFG.ball, t)), br = 0.62 * s; let holder = CFG.ball;
      plus.style.opacity = 0;
      CFG.actions.forEach((a) => {
        if (a.type === 'pass' && t >= a.t[0]) {
          if (t < a.t[1]) { const A = SP && a.from === SP.id ? starRelease(a) : P(...posAt(a.from, a.t[0])), B = P(...posAt(a.to, a.t[1])), q = ease((t - a.t[0]) / (a.t[1] - a.t[0])); bp = [lerp(A[0], B[0], q), lerp(A[1], B[1], q)]; holder = null; }
          else { holder = a.to; bp = P(...posAt(a.to, t)); }
        }
        if (a.type === 'shot' && t >= a.t[0]) {
          const A = P(...posAt(a.who, a.t[0])), H2 = P(0, 5.25), q = clamp((t - a.t[0]) / (a.t[1] - a.t[0]));
          bp = [lerp(A[0], H2[0], q), lerp(A[1], H2[1], q) - Math.sin(q * Math.PI) * 3 * s]; br = 0.62 * s * (1 + 0.9 * Math.sin(q * Math.PI)); holder = null;
          if (q >= 1) { br = 0.62 * s * Math.max(0.5, 1 - (t - a.t[1]) * 2); }
          if (t > a.t[1]) { plus.style.opacity = clamp((t - a.t[1]) / 0.25); plus.setAttribute('x', F(H2[0] + 5 * s)); plus.setAttribute('y', F(H2[1] + 1.5 * s)); }
        }
      });
      if (holder && SP && holder === SP.id && starHand) bp = starHand;
      else if (holder) { bp = [bp[0] + R * 0.85, bp[1] - R * 0.85]; }
      ball.setAttribute('cx', F(bp[0])); ball.setAttribute('cy', F(bp[1])); ball.setAttribute('r', F(br));
      // clock: frozen until the catch, runs to the release
      if (CFG.clock) { const c = CFG.clock, cq = clamp((t - c.run) / (c.stop - c.run)); clock.textContent = fmtClock(lerp(c.start, c.end, cq)); }
      if (CFG.score) score.textContent = t >= CFG.score.at ? CFG.score.after : CFG.score.before;
      // active beat
      let k = 0; CFG.beats.forEach((b, i) => { if (t >= b.t) k = i; });
      beats.forEach((b, i) => { b.style.opacity = short ? (i === k ? 1 : 0) : (i === k ? 1 : i < k ? .45 : .22); });
    };
    if (Q) {
      let qx, qy, qw;
      if (short) { qx = M; qy = sbY + 90; qw = W - 2 * M; } else if (tall) { qx = M; qy = sbY + 44; qw = W - 2 * M; } else { qx = x1 + 40; qy = top + 100; qw = W - M - qx; }
      const qg = S('g', {}, svg); qg.style.opacity = 0;
      const ps = short ? 76 : tall ? 46 : 36;
      const qt = T(qg, qx, qy + ps, Q.prompt, 'd', ps); qt.style.fill = '#FF5A1F';
      if (qt.getComputedTextLength() > qw - ps * 1.9) qt.style.fontSize = (ps * (qw - ps * 1.9) / qt.getComputedTextLength()) + 'px';   // leave room for the countdown
      const qs = T(qg, qx, qy + ps + (short ? 62 : 38), Q.sub || '', 'b', short ? 36 : tall ? 24 : 18); wrap(qs, qx, qw * 0.7);
      const qn = T(qg, qx + qw, qy + ps * 2.1, '', 'd', ps * 2.4, 'end');
      const qm = {};
      Object.entries(CFG.players).forEach(([id, p]) => { if (p.side === 'o' && id !== Q.eyes) { const m = T(top2, 0, 0, '?', 'd', short ? 56 : 34, 'middle'); m.style.fill = '#FF5A1F'; m.style.opacity = 0; qm[id] = m; } });
      const ring = S('circle', {cx: 0, cy: 0, r: F(R * 1.9), fill: 'none', stroke: '#FF5A1F', 'stroke-width': F(s * 0.34)}, top2); ring.style.opacity = 0;
      const tag = T(top2, 0, 0, Q.tag || 'OPEN', 'k', short ? 34 : 20, 'start'); tag.style.opacity = 0;
      // sightlines (optional quiz.eyes = id of the player whose read it is): faint lines to every teammate during the freeze,
      // then only the answer's line, bold, until the pass leaves
      const eyes = Q.eyes ? Object.keys(CFG.players).filter((id) => CFG.players[id].side === 'o' && id !== Q.eyes).map((id) => {
        const ln = S('path', {fill: 'none', stroke: '#FF5A1F', 'stroke-linecap': 'round'}, trails); ln.style.opacity = 0; return [id, ln]; }) : [];
      const drawB = draw;
      draw = (t) => {
        const b = BT(t); drawB(b);
        const fz = t >= Q.t && t < Q.t + HOLD, after = t - Q.t - HOLD;
        qg.style.opacity = fz ? 1 : 0;
        if (fz) { beats.forEach((x) => { x.style.opacity = 0; }); qn.textContent = String(Math.ceil(Q.t + HOLD - t - 1e-6)); }
        const pulse = 1 + 0.14 * Math.sin((t - Q.t) * 8);
        Object.entries(qm).forEach(([id, m]) => { const [x, y] = P(...posAt(id, b)); m.setAttribute('transform', `translate(${F(x + R * 1.35)} ${F(y - R * 0.9)}) scale(${pulse.toFixed(3)})`); m.style.opacity = fz ? 1 : 0; });
        const show = after >= 0 && after < 2.8 ? (after < 2.2 ? 1 : (2.8 - after) / 0.6) : 0;
        const [ax, ay] = P(...posAt(Q.answer, b)), grow = after >= 0 ? 1 + 0.5 * Math.max(0, 1 - after / 0.35) : 1;
        ring.setAttribute('transform', `translate(${F(ax)} ${F(ay)}) scale(${grow.toFixed(3)})`); ring.style.opacity = show;
        eyes.forEach(([id, ln]) => {
          const E0 = SP && Q.eyes === SP.id && starHead ? starHead : P(...posAt(Q.eyes, b)), E1 = P(...posAt(id, b)), ans = id === Q.answer;
          const op = fz ? 0.55 : (ans && after >= 0 && after < (Q.lineHold || 0.6)) ? 1 : 0;
          ln.setAttribute('d', `M${F(E0[0])} ${F(E0[1])}L${F(E1[0])} ${F(E1[1])}`); ln.style.opacity = op;
          ln.setAttribute('stroke-width', F(s * (fz ? 0.16 : 0.3))); ln.setAttribute('stroke-dasharray', fz ? `${F(s * 0.6)} ${F(s * 0.6)}` : 'none');
        });
        tag.setAttribute('x', F(ax + R * 2.3)); tag.setAttribute('y', F(ay + R * 0.35)); tag.style.opacity = show;
      };
    }
    draw(window.__t || 0);
  }

  // playback
  let t = 0, last = null, playing = !reduce, speed = 1;
  window.__t = 0;
  const tick = (now) => {
    if (window.__hold) return;
    if (last != null && playing) {
      // with sound on, the music is the clock (no seeking while it plays, so it never stutters); otherwise frame time
      const c = speed === 1 ? sndClock() : null;
      t = c != null ? c : t + (now - last) / 1000 * speed;
      if (t > TOTAL + 1.5) { t = 0; sndSeek(0); }
    }
    last = now; window.__t = t; draw(Math.min(t, TOTAL)); requestAnimationFrame(tick);
  };
  build();
  if (reduce) { t = TOTAL; draw(TOTAL); }
  requestAnimationFrame(tick);
  let rw = 0; window.addEventListener('resize', () => { clearTimeout(rw); rw = setTimeout(() => { build(); draw(Math.min(t, TOTAL)); }, 120); });
  const pp = document.getElementById('pp'), slow = document.getElementById('slow');
  pp.addEventListener('click', () => { playing = !playing; pp.textContent = playing ? 'Pause' : 'Play'; last = null; sndRun(playing && speed === 1, t); });
  slow.addEventListener('click', () => { speed = speed === 1 ? 0.4 : 1; slow.setAttribute('aria-pressed', String(speed !== 1)); sndRun(playing && speed === 1, t); });
  document.getElementById('again').addEventListener('click', () => { t = 0; playing = true; pp.textContent = 'Pause'; sndRun(speed === 1, 0); });
  const jumps = document.getElementById('jumps');
  CFG.beats.forEach((b, i) => { const btn = document.createElement('button'); btn.type = 'button'; btn.textContent = (i + 1) + ' · ' + b.title; btn.addEventListener('click', () => { t = (Q && b.t >= Q.t ? b.t + HOLD : b.t) + 0.05; draw(t); sndSeek(t); }); jumps.appendChild(btn); jumps.appendChild(document.createTextNode(' ')); });
  window.__A = {render: (x) => draw(x), build, total: TOTAL, loop: {start: Math.max(0, Math.min(...(CFG.actions || []).map((a) => a.t[0]), TOTAL) - 0.3), cut: TOTAL}}; // Shorts open on the first action and loop
  // tell a parent page how tall we are, so its iframe fits without scrolling
  const postH = () => { if (window.parent !== window) window.parent.postMessage({bmH: Math.ceil(document.querySelector('.wrap').getBoundingClientRect().height)}, '*'); };
  if ('ResizeObserver' in window) new ResizeObserver(postH).observe(document.body); window.addEventListener('load', postH); postH();
})();
</script>
</body></html>
"""
out_html = (HTML.replace('__TITLE__', cfg['title']).replace('__ARIA__', cfg['aria'].replace('"', '&quot;'))
            .replace('__C1__', team['c1']).replace('__C2__', team['c2']).replace('__CFG__', json.dumps(cfg)).replace('__STARJS__', STAR_JS).replace('__STARCSS__', STAR_CSS))
os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
open(out, 'w').write(out_html)
print('wrote', out)
