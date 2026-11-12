"""One-team trend Short: "<Team> are W-L. Are they actually good?" Record vs. point differential for all 30 teams,
zoomed on one team and a same-record comparison team, the gap to the typical-record line, then the reason (a games panel).
Usage (repo root): python3 kit/make_team_trend.py kit/trends/<data>.csv kit/trends/<config>.json src/anim/<slug>.html
Fonts: FONT_DIR=<node_modules with @fontsource/archivo, ibm-plex-sans, ibm-plex-mono> (embedded as base64).
window.__A = {render(t), total, loop} for kit/short_mp4.sh."""
import base64, csv, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
if not os.path.exists(os.path.join(ROOT, 'data', 'teams.json')): ROOT = '/home/claude/boxandmotion-site'
rows = list(csv.DictReader(open(sys.argv[1]))); cfg = json.load(open(sys.argv[2])); out = sys.argv[3]
teams = json.load(open(os.path.join(ROOT, 'data', 'teams.json')))
FD = os.environ.get('FONT_DIR', os.path.join(HERE, 'node_modules'))
b64 = lambda pkg, f: base64.b64encode(open(os.path.join(FD, '@fontsource', pkg, 'files', f), 'rb').read()).decode()
FONTS = ''.join(f"@font-face{{font-family:'{fam}';font-weight:{w};src:url(data:font/woff2;base64,{b64(pkg, f)}) format('woff2')}}"
                for fam, w, pkg, f in [('Archivo', 800, 'archivo', 'archivo-latin-800-normal.woff2'),
                                       ('IBM Plex Sans', 400, 'ibm-plex-sans', 'ibm-plex-sans-latin-400-normal.woff2'),
                                       ('IBM Plex Sans', 600, 'ibm-plex-sans', 'ibm-plex-sans-latin-600-normal.woff2'),
                                       ('IBM Plex Mono', 500, 'ibm-plex-mono', 'ibm-plex-mono-latin-500-normal.woff2')])
X0, X1, Y0, Y1 = 62, 512, 372, 790
DMIN, DMAX, PMIN, PMAX = -17, 13, 0.0, 1.0
px = lambda d: X0 + (d - DMIN) / (DMAX - DMIN) * (X1 - X0)
py = lambda p: Y1 - (p - PMIN) / (PMAX - PMIN) * (Y1 - Y0)
pts = []
for r in rows:
    w, l, d = int(r['w']), int(r['l']), float(r['diff']); c = teams[r['team']]['c1']
    lum = sum(int(c[i:i + 2], 16) * k for i, k in ((1, .299), (3, .587), (5, .114)))
    pts.append({'t': r['team'], 'w': w, 'l': l, 'd': d, 'p': w / (w + l), 'x': px(d), 'y': py(w / (w + l)), 'c': c,
                'ink': '#16181d' if lum > 160 else '#ffffff'})
for _ in range(300):   # nudge overlapping dots a few px apart
    for i, a in enumerate(pts):
        for b in pts[i + 1:]:
            dx, dy = b['x'] - a['x'], b['y'] - a['y']; dist = (dx * dx + dy * dy) ** .5
            if dist < 31:
                ux, uy = (dx / dist, dy / dist) if dist > .01 else (0, 1); push = (31 - dist) / 2
                a['x'] -= ux * push; a['y'] -= uy * push; b['x'] += ux * push; b['y'] += uy * push
n = len(pts); mx = sum(p['d'] for p in pts) / n; my = sum(p['p'] for p in pts) / n
slope = sum((p['d'] - mx) * (p['p'] - my) for p in pts) / sum((p['d'] - mx) ** 2 for p in pts); icpt = my - slope * mx
for p in pts: p['fit'] = py(icpt + slope * p['d'])
DATA = {'pts': pts, 'line': [[px(d), py(icpt + slope * d)] for d in (-16, 12.5)], 'box': [X0, X1, Y0, Y1], 'zero': [px(0), py(.5)],
        'xt': [[px(v), ('+' if v > 0 else '') + str(v)] for v in (-15, -10, -5, 0, 5, 10)],
        'yt': [[py(v), '1.000' if v == 1 else f'.{int(round(v * 1000)):03d}'] for v in (0, .25, .5, .75, 1)], **cfg}

HTML = r"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>__TITLE__ | Box & Motion Hoops</title>
<style>__FONTS__
html,body{margin:0;background:#f4f4f2}.wrap{width:540px;height:960px;margin:0 auto;background:#fff;position:relative;overflow:hidden}svg{display:block}
.d{font-family:Archivo,sans-serif;font-weight:800;fill:#16181d}.k{font-family:'IBM Plex Mono',monospace;font-weight:500;letter-spacing:.14em;fill:#FF5A1F}
.b{font-family:'IBM Plex Sans',sans-serif;font-weight:400;fill:#16181d}.s{font-family:'IBM Plex Sans',sans-serif;font-weight:600;fill:#16181d}
.m{font-family:'IBM Plex Mono',monospace;font-weight:500;fill:#8a8f99}
</style></head><body><div class="wrap"><svg id="sv" width="540" height="960" viewBox="0 0 540 960" role="img" aria-label="__TITLE__"></svg></div>
<script>
(() => {
  // ?embed=1 (site iframe): scale the 9:16 board to the frame's width and report the height to the page
  if (/[?&]embed=1/.test(location.search)) { const w0 = document.querySelector('.wrap'); document.documentElement.style.background = 'transparent'; document.body.style.background = 'transparent';
    const fit = () => { const s = Math.min(1, document.documentElement.clientWidth / 540); w0.style.transformOrigin = 'top left'; w0.style.transform = `scale(${s})`;
      w0.style.marginLeft = Math.max(0, (document.documentElement.clientWidth - 540 * s) / 2) + 'px'; document.body.style.height = (960 * s) + 'px'; document.body.style.overflow = 'hidden';
      if (window.parent !== window) window.parent.postMessage({bmH: Math.ceil(960 * s)}, '*'); };
    w0.style.margin = '0'; fit(); window.addEventListener('resize', fit); }
  const D = __DATA__, NS = 'http://www.w3.org/2000/svg', sv = document.getElementById('sv');
  const S = (tag, at, par) => { const e = document.createElementNS(NS, tag); for (const k in at) e.setAttribute(k, at[k]); (par || sv).appendChild(e); return e; };
  const T = (par, x, y, txt, cls, size, anchor) => { const e = S('text', {x, y, class: cls, 'text-anchor': anchor || 'start'}, par); e.style.fontSize = size + 'px'; e.textContent = txt; return e; };
  const wrap = (el, x, maxW, lh) => { const words = el.textContent.split(' '); el.textContent = ''; let ln = S('tspan', {x}, el), cur = '';
    words.forEach((w) => { const tr = cur ? cur + ' ' + w : w; ln.textContent = tr; if (ln.getComputedTextLength() > maxW && cur) { ln.textContent = cur; ln = S('tspan', {x, dy: lh}, el); ln.textContent = w; cur = w; } else cur = tr; }); };
  const cl = (v) => Math.max(0, Math.min(1, v)), ease = (u) => { u = cl(u); return u * u * (3 - 2 * u); };
  const back = (u) => { u = cl(u); const c = 1.7; return 1 + (c + 1) * Math.pow(u - 1, 3) + c * Math.pow(u - 1, 2); };
  const [X0, X1, Y0, Y1] = D.box, M = 30, ME = D.team, VS = D.compare || [];

  // header: the hook stays on screen the whole Short (it's also the first frame)
  T(sv, M, 54, D.kicker, 'k', 14);
  T(sv, M, 108, D.hook[0], 'd', 46);
  const h2 = T(sv, M, 160, D.hook[1], 'd', 46); h2.style.fill = '#FF5A1F';
  const cap = S('g', {}, sv), capK = T(cap, M, 220, '', 'k', 13), capT = T(cap, M, 254, '', 'd', 26), capB = T(cap, M, 286, '', 'b', 17);

  // chart (zoomable)
  S('clipPath', {id: 'cp'}, S('defs', {}, sv)).appendChild(Object.assign(document.createElementNS(NS, 'rect'), {}));
  const cpr = sv.querySelector('#cp rect'); [['x', 0], ['y', Y0 - 40], ['width', 540], ['height', Y1 - Y0 + 100]].forEach(([k, v]) => cpr.setAttribute(k, v));
  const clip = S('g', {'clip-path': 'url(#cp)'}, sv), ch = S('g', {}, clip);
  const ax = S('g', {}, ch);
  S('line', {x1: X0, y1: Y1, x2: X1, y2: Y1, stroke: '#16181d', 'stroke-width': 2}, ax);
  S('line', {x1: X0, y1: Y0, x2: X0, y2: Y1, stroke: '#16181d', 'stroke-width': 2}, ax);
  S('line', {x1: D.zero[0], y1: Y0, x2: D.zero[0], y2: Y1, stroke: '#c9ccd2', 'stroke-width': 1.5, 'stroke-dasharray': '4 5'}, ax);
  S('line', {x1: X0, y1: D.zero[1], x2: X1, y2: D.zero[1], stroke: '#c9ccd2', 'stroke-width': 1.5, 'stroke-dasharray': '4 5'}, ax);
  D.xt.forEach(([x, l]) => T(ax, x, Y1 + 22, l, 'm', 13, 'middle'));
  D.yt.forEach(([y, l]) => T(ax, X0 - 8, y + 4, l, 'm', 13, 'end'));
  T(ax, (X0 + X1) / 2, Y1 + 48, 'POINT DIFFERENTIAL PER GAME', 'k', 12, 'middle').style.fill = '#16181d';
  const yl = T(ax, 0, 0, 'WIN %', 'k', 12, 'middle'); yl.style.fill = '#16181d'; yl.setAttribute('transform', `translate(${X0 - 44},${Y0 + 80}) rotate(-90)`);
  const lg = S('g', {}, ch);
  const ln = S('line', {x1: D.line[0][0], y1: D.line[0][1], x2: D.line[0][0], y2: D.line[0][1], stroke: '#FF5A1F', 'stroke-width': 3, 'stroke-linecap': 'round', 'stroke-dasharray': '2 8'}, lg);
  const leg = S('g', {}, lg); S('line', {x1: X1 - 236, y1: Y1 - 18, x2: X1 - 206, y2: Y1 - 18, stroke: '#FF5A1F', 'stroke-width': 3, 'stroke-linecap': 'round', 'stroke-dasharray': '2 8'}, leg);
  T(leg, X1 - 6, Y1 - 13, 'typical record for that margin', 's', 13, 'end').style.fill = '#FF5A1F';
  const gaps = S('g', {}, ch), dots = {};
  D.pts.forEach((p, i) => {
    const g = S('g', {}, ch), ring = S('circle', {r: 22, fill: 'none', stroke: '#FF5A1F', 'stroke-width': 3.5}, g);
    S('circle', {r: 15, fill: p.c, stroke: '#fff', 'stroke-width': 1.5}, g);
    const tx = T(g, 0, 4, p.t, 'd', 10.5, 'middle'); tx.style.fill = p.ink;
    const tag = S('g', {}, g), tb = S('rect', {rx: 6, height: 24, fill: p.t === ME ? '#16181d' : '#5b606b'}, tag);
    const tt = T(tag, 0, 0, `${p.w}-${p.l}, ${p.d > 0 ? '+' : ''}${p.d.toFixed(1)} a game`, 's', 13); tt.style.fill = '#fff';
    const gap = S('line', {x1: p.x, y1: p.y, x2: p.x, y2: p.fit, stroke: '#FF5A1F', 'stroke-width': 2.5}, gaps);
    dots[p.t] = {p, g, ring, tag, tb, tt, gap, delay: p.t === ME ? 0 : 0.02 * ((p.x - X0) / (X1 - X0) * 20 + (i % 3))};
  });
  // games panel (the reason): one box per game, grouped (not in date order)
  const gp = S('g', {}, sv); S('rect', {x: M - 8, y: Y0 - 20, width: 540 - 2 * M + 16, height: Y1 - Y0 + 70, rx: 14, fill: '#fff', stroke: '#e3e4e8'}, gp);
  T(gp, M + 10, Y0 + 18, D.panel.kicker, 'k', 13);
  const boxes = [], G = D.panel.groups; let gi = 0;
  const bw = 66, bh = 66, gapx = 12, cols = 6, bx0 = (540 - (cols * bw + (cols - 1) * gapx)) / 2, by0 = Y0 + 46;
  G.forEach((grp) => { for (let k = 0; k < grp.n; k++, gi++) { const c = gi % cols, r = Math.floor(gi / cols), x = bx0 + c * (bw + gapx), y = by0 + r * (bh + 16);
    const g = S('g', {transform: `translate(${x},${y})`}, gp);
    S('rect', {width: bw, height: bh, rx: 10, fill: grp.fill, stroke: grp.stroke || 'none', 'stroke-width': 2}, g);
    const l = T(g, bw / 2, bh / 2 + 9, grp.mark, 'd', 26, 'middle'); l.style.fill = grp.ink;
    boxes.push({g, i: gi}); } });
  const legY = by0 + 2 * (bh + 16) + 26;
  G.forEach((grp, i) => { const y = legY + i * 30; S('rect', {x: M + 10, y: y - 14, width: 18, height: 18, rx: 4, fill: grp.fill, stroke: grp.stroke || 'none', 'stroke-width': 2}, gp);
    T(gp, M + 38, y, grp.label, 's', 15); });
  const pn = T(gp, M + 10, legY + G.length * 30 + 22, D.panel.note, 'd', 21); wrap(pn, M + 10, 540 - 2 * M - 20, 26);
  // footer
  const ft = T(sv, M, 878, D.sources, 'b', 11.5); ft.style.fill = '#8a8f99'; wrap(ft, M, 540 - 2 * M, 15);
  T(sv, M, 930, 'Unofficial fan content. Not affiliated with the NBA or any team.', 'b', 11.5).style.fill = '#8a8f99';
  T(sv, 540 - M, 930, 'BOX & MOTION HOOPS', 'k', 11.5, 'end').style.fill = '#16181d';

  const B = D.beats, TOTAL = D.total, me = dots[ME].p;
  let lastBeat = -2;
  function render(t) {
    let bi = -1; B.forEach((b, i) => { if (t >= b.t[0] && t < b.t[1]) bi = i; });
    const b = B[bi] || {}, inB = b.t ? ease((t - b.t[0]) / 0.4) * (1 - ease((t - b.t[1] + 0.35) / 0.35)) : 0;
    if (bi !== lastBeat) { lastBeat = bi; capK.textContent = b.kicker || ''; capT.textContent = b.title || ''; capB.textContent = b.text || ''; if (b.text) wrap(capB, M, 540 - 2 * M, 21); }
    cap.style.opacity = inB;
    // zoom toward the team during the zoom beats (eased in and out across beat edges)
    const zw = B.reduce((m, bb) => bb.zoom ? Math.max(m, ease((t - bb.t[0]) / 0.8) * (1 - ease((t - bb.t[1] + 0.2) / 0.8))) : m, 0);
    const zc = [me, ...VS.map((v) => dots[v].p)], Z = 1 + 0.35 * zw, cx = zc.reduce((a, q) => a + q.x, 0) / zc.length, cy = me.y + 40;
    ch.setAttribute('transform', `translate(${cx},${cy}) scale(${Z}) translate(${-cx},${-cy})`);
    const focus = b.teams || [];
    Object.values(dots).forEach((o) => { const on = focus.includes(o.p.t), u = back((t - o.delay) / 0.55), y0 = Y0 - 60;
      o.g.setAttribute('transform', `translate(${o.p.x},${y0 + (o.p.y - y0) * u})`);
      o.g.style.opacity = ease((t - o.delay) / 0.25) * (1 - (on || !b.t ? 0 : 0.8 * inB));
      o.ring.style.opacity = on ? inB : 0; o.tag.style.opacity = on ? inB : 0;
      if (on) { const w = o.tt.getComputedTextLength() + 16, below = o.p.t !== ME, x = below ? 18 - w : -26 - w, y = below ? 26 : -12;
        o.tb.setAttribute('x', x); o.tb.setAttribute('y', y); o.tt.setAttribute('y', y + 17); o.tb.setAttribute('width', w); o.tt.setAttribute('x', x + 8); o.g.parentNode.appendChild(o.g); }
      o.gap.style.opacity = on && b.gap ? inB : 0; });
    const lu = ease((t - D.line_in) / 0.9);
    ln.setAttribute('x2', D.line[0][0] + (D.line[1][0] - D.line[0][0]) * lu); ln.setAttribute('y2', D.line[0][1] + (D.line[1][1] - D.line[0][1]) * lu);
    lg.style.opacity = t < D.line_in ? 0 : 1; leg.style.opacity = ease((t - D.line_in - 0.7) / 0.3);
    // games panel beat
    const pb = B.find((bb) => bb.panel), pu = pb ? ease((t - pb.t[0]) / 0.4) * (1 - ease((t - pb.t[1] + 0.35) / 0.35)) : 0;
    gp.style.opacity = pu; clip.style.opacity = 1 - 0.85 * pu;
    boxes.forEach((o) => { const u = back((t - pb.t[0] - 0.3 - o.i * 0.12) / 0.4); o.g.style.opacity = cl((t - pb.t[0] - 0.3 - o.i * 0.12) / 0.15);
      const tr = o.g.getAttribute('transform').split(' scale')[0]; o.g.setAttribute('transform', tr + ` scale(${0.6 + 0.4 * u})`); });
    window.__t = t;
  }
  const start = performance.now();
  function tick() { if (!window.__hold) { render(((performance.now() - start) / 1000) % TOTAL); requestAnimationFrame(tick); } }
  render(0); requestAnimationFrame(tick);
  window.__A = {render, total: TOTAL, loop: {start: D.loop_start, cut: TOTAL}};
})();
</script></body></html>"""
open(out, 'w').write(HTML.replace('__TITLE__', cfg['hook'][0] + ' ' + cfg['hook'][1]).replace('__FONTS__', FONTS).replace('__DATA__', json.dumps(DATA)))
print(out)
