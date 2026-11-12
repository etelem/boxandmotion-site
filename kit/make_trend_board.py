"""Build the "Good, lucky or in trouble?" trend board: every team's record vs. its point differential, in motion.
Usage (repo root): python3 kit/make_trend_board.py kit/trends/<data>.csv kit/trends/<config>.json src/anim/<slug>.html
Fonts: npm i @fontsource/archivo @fontsource/ibm-plex-sans @fontsource/ibm-plex-mono, then FONT_DIR=<that node_modules> (embedded as base64).
data.csv: team,w,l,pf,pa,diff (from a named standings source). config.json: title, kicker, asof, beats, sources.
Modes: ?short=1 renders the 9:16 Shorts layout (no chrome). window.__A = {render(t), total, loop} for frame export."""
import base64, csv, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.dirname(HERE)
rows = list(csv.DictReader(open(sys.argv[1])))
cfg = json.load(open(sys.argv[2])); out = sys.argv[3]
teams = json.load(open(os.path.join(SITE, 'data', 'teams.json')))


def font(pkg, f):
    p = os.path.join(os.environ.get('FONT_DIR', os.path.join(HERE, 'node_modules')), '@fontsource', pkg, 'files', f)
    return base64.b64encode(open(p, 'rb').read()).decode()


FONTS = ''.join(
    f"@font-face{{font-family:'{fam}';font-weight:{w};src:url(data:font/woff2;base64,{font(pkg, f)}) format('woff2')}}"
    for fam, w, pkg, f in [('Archivo', 700, 'archivo', 'archivo-latin-700-normal.woff2'),
                           ('Archivo', 800, 'archivo', 'archivo-latin-800-normal.woff2'),
                           ('IBM Plex Sans', 400, 'ibm-plex-sans', 'ibm-plex-sans-latin-400-normal.woff2'),
                           ('IBM Plex Sans', 600, 'ibm-plex-sans', 'ibm-plex-sans-latin-600-normal.woff2'),
                           ('IBM Plex Mono', 500, 'ibm-plex-mono', 'ibm-plex-mono-latin-500-normal.woff2')])

# chart geometry (CSS px in the 540x960 Short)
X0, X1, Y0, Y1 = 62, 512, 330, 790          # plot box: left, right, top, bottom
DMIN, DMAX, PMIN, PMAX = -17, 13, 0.0, 1.0
R = 15


def px(d): return X0 + (d - DMIN) / (DMAX - DMIN) * (X1 - X0)
def py(p): return Y1 - (p - PMIN) / (PMAX - PMIN) * (Y1 - Y0)


pts = []
for r in rows:
    w, l, d = int(r['w']), int(r['l']), float(r['diff'])
    c = teams[r['team']]['c1']
    lum = sum(int(c[i:i + 2], 16) * k for i, k in ((1, .299), (3, .587), (5, .114)))
    pts.append({'t': r['team'], 'w': w, 'l': l, 'd': d, 'p': w / (w + l), 'x': px(d), 'y': py(w / (w + l)),
                'c': c, 'ink': '#16181d' if lum > 160 else '#ffffff'})
# nudge overlapping dots apart (a few px at most; the true spot is where the dot's centre started)
for _ in range(300):
    for i, a in enumerate(pts):
        for b in pts[i + 1:]:
            dx, dy = b['x'] - a['x'], b['y'] - a['y']; dist = (dx * dx + dy * dy) ** .5 or .01
            if dist < 2 * R + 1:
                push = (2 * R + 1 - dist) / 2; ux, uy = (dx, dy) if dist > .01 else (0, 1)
                ux, uy = ux / dist if dist > .01 else 0, uy / dist if dist > .01 else 1
                a['x'] -= ux * push; a['y'] -= uy * push; b['x'] += ux * push; b['y'] += uy * push
# least-squares line: the typical win % for a given margin, fit on these 30 teams
n = len(pts); mx = sum(p['d'] for p in pts) / n; my = sum(p['p'] for p in pts) / n
slope = sum((p['d'] - mx) * (p['p'] - my) for p in pts) / sum((p['d'] - mx) ** 2 for p in pts)
icpt = my - slope * mx
line = [[px(d), py(icpt + slope * d)] for d in (-16, 12.5)]
for p in pts:
    p['fit'] = py(icpt + slope * p['d'])

DATA = {'pts': pts, 'line': line, 'box': [X0, X1, Y0, Y1], 'zero': [px(0), py(.5)],
        'xt': [[px(v), ('+' if v > 0 else '') + str(v)] for v in (-15, -10, -5, 0, 5, 10)],
        'yt': [[py(v), f'.{int(round(v * 1000)):03d}'.replace('.1000', '1.000')] for v in (0, .25, .5, .75, 1)],
        **cfg}

HTML = r"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>__TITLE__ | Box & Motion Hoops</title>
<style>__FONTS__
html,body{margin:0;background:#f4f4f2}
.wrap{width:540px;height:960px;margin:0 auto;background:#fff;position:relative;overflow:hidden}
svg{display:block}
.d{font-family:Archivo,sans-serif;font-weight:800;fill:#16181d}
.k{font-family:'IBM Plex Mono',monospace;font-weight:500;letter-spacing:.14em;fill:#FF5A1F}
.b{font-family:'IBM Plex Sans',sans-serif;font-weight:400;fill:#16181d}
.s{font-family:'IBM Plex Sans',sans-serif;font-weight:600;fill:#16181d}
.m{font-family:'IBM Plex Mono',monospace;font-weight:500;fill:#8a8f99}
</style></head><body><div class="wrap"><svg id="sv" width="540" height="960" viewBox="0 0 540 960" role="img" aria-label="__TITLE__"></svg></div>
<script>
(() => {
  const D = __DATA__, NS = 'http://www.w3.org/2000/svg', sv = document.getElementById('sv');
  const S = (tag, at, par) => { const e = document.createElementNS(NS, tag); for (const k in at) e.setAttribute(k, at[k]); (par || sv).appendChild(e); return e; };
  const T = (par, x, y, txt, cls, size, anchor) => { const e = S('text', {x, y, class: cls, 'text-anchor': anchor || 'start'}, par); e.style.fontSize = size + 'px'; e.textContent = txt; return e; };
  const wrap = (el, x, maxW, lh) => { const words = el.textContent.split(' '); el.textContent = ''; let ln = S('tspan', {x}, el), cur = '', n = 0;
    words.forEach((w) => { const tr = cur ? cur + ' ' + w : w; ln.textContent = tr; if (ln.getComputedTextLength() > maxW && cur) { ln.textContent = cur; ln = S('tspan', {x, dy: lh}, el); ln.textContent = w; cur = w; n++; } else cur = tr; }); return n + 1; };
  const cl = (v) => Math.max(0, Math.min(1, v)), ease = (u) => { u = cl(u); return u * u * (3 - 2 * u); };
  const back = (u) => { u = cl(u); const c = 1.7; return 1 + (c + 1) * Math.pow(u - 1, 3) + c * Math.pow(u - 1, 2); };
  const [X0, X1, Y0, Y1] = D.box, M = 30;

  // header
  T(sv, M, 62, D.kicker, 'k', 15);
  const ttl = T(sv, M, 106, D.title, 'd', 36);
  T(sv, M, 140, D.dek, 'b', 17).style.fill = '#5b606b';
  // caption area (one per beat)
  const cap = S('g', {}, sv), capK = T(cap, M, 196, '', 'k', 14), capT = T(cap, M, 234, '', 'd', 28), capB = T(cap, M, 266, '', 'b', 17);
  // axes, quadrant lines and labels
  const ax = S('g', {}, sv);
  S('line', {x1: X0, y1: Y1, x2: X1, y2: Y1, stroke: '#16181d', 'stroke-width': 2}, ax);
  S('line', {x1: X0, y1: Y0, x2: X0, y2: Y1, stroke: '#16181d', 'stroke-width': 2}, ax);
  S('line', {x1: D.zero[0], y1: Y0, x2: D.zero[0], y2: Y1, stroke: '#c9ccd2', 'stroke-width': 1.5, 'stroke-dasharray': '4 5'}, ax);
  S('line', {x1: X0, y1: D.zero[1], x2: X1, y2: D.zero[1], stroke: '#c9ccd2', 'stroke-width': 1.5, 'stroke-dasharray': '4 5'}, ax);
  D.xt.forEach(([x, l]) => T(ax, x, Y1 + 22, l, 'm', 13, 'middle'));
  D.yt.forEach(([y, l]) => T(ax, X0 - 8, y + 4, l, 'm', 13, 'end'));
  T(ax, (X0 + X1) / 2, Y1 + 48, 'POINT DIFFERENTIAL PER GAME', 'k', 12, 'middle').style.fill = '#16181d';
  const yl = T(ax, 0, 0, 'WIN %', 'k', 12, 'middle'); yl.style.fill = '#16181d'; yl.setAttribute('transform', `translate(${X0 - 44},${Y0 + 80}) rotate(-90)`);
  const q = [['WINNING BIG', X1 - 6, Y0 + 18, 'end'], ['WINNING, BARELY', D.zero[0] - 8, Y0 + 18, 'end'], ['LOSING CLOSE', X1 - 6, Y1 - 10, 'end'], ['LOSING BIG', D.zero[0] - 8, Y1 - 10, 'end']]
    .map(([l, x, y, a]) => { const e = T(ax, x, y, l, 'k', 12, a); e.style.fill = '#8a8f99'; return e; });
  // typical-record line
  const lg = S('g', {}, sv);
  const ln = S('line', {x1: D.line[0][0], y1: D.line[0][1], x2: D.line[0][0], y2: D.line[0][1], stroke: '#FF5A1F', 'stroke-width': 3, 'stroke-linecap': 'round', 'stroke-dasharray': '2 8'}, lg);
  const lt = S('g', {}, lg); S('line', {x1: X1 - 236, y1: Y1 - 38, x2: X1 - 206, y2: Y1 - 38, stroke: '#FF5A1F', 'stroke-width': 3, 'stroke-linecap': 'round', 'stroke-dasharray': '2 8'}, lt);
  T(lt, X1 - 6, Y1 - 33, 'typical record for that margin', 's', 13, 'end').style.fill = '#FF5A1F';
  // gap markers (dot to line) for the beat's teams
  const gaps = S('g', {}, sv);
  // dots
  const dots = {};
  D.pts.forEach((p, i) => {
    const g = S('g', {}, sv), ring = S('circle', {r: 22, fill: 'none', stroke: '#FF5A1F', 'stroke-width': 3.5}, g);
    S('circle', {r: 15, fill: p.c, stroke: '#fff', 'stroke-width': 1.5}, g);
    const tx = T(g, 0, 4, p.t, 'd', 10.5, 'middle'); tx.style.fill = p.ink; tx.style.fontWeight = 700;
    const tag = S('g', {}, g), tb = S('rect', {rx: 6, height: 24, fill: '#16181d'}, tag), tt = T(tag, 0, 0, `${p.w}-${p.l}, ${p.d > 0 ? '+' : ''}${p.d.toFixed(1)}`, 's', 13);
    tt.style.fill = '#fff';
    const gap = S('line', {x1: p.x, y1: p.y, x2: p.x, y2: p.fit, stroke: '#FF5A1F', 'stroke-width': 2.5}, gaps);
    dots[p.t] = {p, g, ring, tag, tb, tt, gap, delay: 0.04 * ((p.x - X0) / (X1 - X0) * 20 + (i % 3))};
  });
  // footer
  const ft = T(sv, M, 878, D.sources, 'b', 11.5); ft.style.fill = '#8a8f99'; wrap(ft, M, 540 - 2 * M, 15);
  const dis = T(sv, M, 930, 'Unofficial fan content. Not affiliated with the NBA or any team.', 'b', 11.5); dis.style.fill = '#8a8f99';
  T(sv, 540 - M, 930, 'BOX & MOTION HOOPS', 'k', 11.5, 'end').style.fill = '#16181d';
  [capB].forEach((e) => e.dataset.w = 1);

  const B = D.beats, TOTAL = D.total;
  let lastBeat = -1;
  function render(t) {
    // dots drop in
    Object.values(dots).forEach((o) => { const u = back((t - o.delay) / 0.7), y0 = Y0 - 60;
      o.g.setAttribute('transform', `translate(${o.p.x},${y0 + (o.p.y - y0) * u})`); o.g.style.opacity = ease((t - o.delay) / 0.25); });
    // which beat
    let bi = -1; B.forEach((b, i) => { if (t >= b.t[0] && t < b.t[1]) bi = i; });
    const b = B[bi], inB = b ? ease((t - b.t[0]) / 0.4) * (1 - ease((t - b.t[1] + 0.35) / 0.35)) : 0;
    if (bi !== lastBeat) { lastBeat = bi; capK.textContent = b ? b.kicker : ''; capT.textContent = b ? b.title : ''; capB.textContent = b ? b.text : ''; if (b) wrap(capB, M, 540 - 2 * M, 21); }
    cap.style.opacity = inB;
    const focus = b ? b.teams : [];
    Object.values(dots).forEach((o) => { const on = focus.includes(o.p.t);
      o.g.style.opacity = Math.min(o.g.style.opacity, 1 - (on ? 0 : 0.78 * inB));
      o.ring.style.opacity = on ? inB : 0; o.ring.setAttribute('r', 22 + (on ? 3 * Math.sin(Math.min(1, (t - b.t[0]) / 0.5) * Math.PI) : 0));
      o.tag.style.opacity = on && b.tags !== false ? inB : 0;
      if (on) { const w = o.tt.getComputedTextLength() + 16, right = o.p.x + 28 + w < X1 + 20, x = right ? 26 : -26 - w;
        o.tb.setAttribute('x', x); o.tb.setAttribute('y', -12); o.tb.setAttribute('width', w); o.tt.setAttribute('x', x + 8); o.tt.setAttribute('y', 5); o.g.parentNode.appendChild(o.g); }
      o.gap.style.opacity = on && b.gap ? inB : 0; });
    // the typical-record line draws in on its first beat, then stays
    const lu = ease((t - D.line_in) / 0.9);
    ln.setAttribute('x2', D.line[0][0] + (D.line[1][0] - D.line[0][0]) * lu); ln.setAttribute('y2', D.line[0][1] + (D.line[1][1] - D.line[0][1]) * lu);
    lg.style.opacity = t < D.line_in ? 0 : 1; lt.style.opacity = ease((t - D.line_in - 0.7) / 0.3) * (1 - 0.6 * (b && !b.gap ? inB : 0));
    ln.style.opacity = 1 - 0.6 * (b && !b.gap ? inB : 0);
    q.forEach((e) => e.style.opacity = 1 - 0.7 * inB);
    window.__t = t;
  }
  const start = performance.now();
  function tick() { if (!window.__hold) { render(((performance.now() - start) / 1000) % TOTAL); requestAnimationFrame(tick); } }
  render(0); requestAnimationFrame(tick);
  window.__A = {render, total: TOTAL, loop: {start: D.loop_start, cut: TOTAL}};
})();
</script></body></html>"""

open(out, 'w').write(HTML.replace('__TITLE__', cfg['title']).replace('__FONTS__', FONTS).replace('__DATA__', json.dumps(DATA)))
print(out, 'slope', round(slope, 4), 'icpt', round(icpt, 4))
