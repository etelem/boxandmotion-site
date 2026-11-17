"""'What changed' Short (Nov 17): one team's turn in ~19 s, 9:16. Hook on the first frame, the before/after card counting up,
the coach's decisions stacking up one at a time (the current one shows its detail), then the verdict.
Usage (repo root): python3 kit/make_whatchanged.py data/whatchanged/<file>.json  -> src/anim/<anim>
Fonts: FONT_DIR=<node_modules with @fontsource/archivo, ibm-plex-sans, ibm-plex-mono> (embedded as base64).
window.__A = {render(t), total, loop} for kit/short_mp4.sh and kit/learn_posters.js; ?embed=1 for the site feed."""
import base64, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
X = json.load(open(sys.argv[1])); S = X["short"]
teams = json.load(open(os.path.join(ROOT, "data", "teams.json"))); TM = teams[X["team"]]
FD = os.environ.get("FONT_DIR", os.path.join(HERE, "node_modules"))
b64 = lambda pkg, f: base64.b64encode(open(os.path.join(FD, "@fontsource", pkg, "files", f), "rb").read()).decode()
FONTS = "".join(f"@font-face{{font-family:'{fam}';font-weight:{w};src:url(data:font/woff2;base64,{b64(pkg, f)}) format('woff2')}}"
                for fam, w, pkg, f in [("Archivo", 800, "archivo", "archivo-latin-800-normal.woff2"),
                                       ("Archivo", 300, "archivo", "archivo-latin-300-normal.woff2"),
                                       ("IBM Plex Sans", 400, "ibm-plex-sans", "ibm-plex-sans-latin-400-normal.woff2"),
                                       ("IBM Plex Sans", 600, "ibm-plex-sans", "ibm-plex-sans-latin-600-normal.woff2"),
                                       ("IBM Plex Mono", 500, "ibm-plex-mono", "ibm-plex-mono-latin-500-normal.woff2")])
D = {"s": S, "cmp": X["compare"], "c": TM["c1"], "total": 19.0}

HTML = r"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>__TITLE__ | Box & Motion Hoops</title>
<style>__FONTS__
html,body{margin:0;background:#f4f4f2}.wrap{width:540px;height:960px;margin:0 auto;background:#fff;position:relative;overflow:hidden}svg{display:block}
.d{font-family:Archivo,sans-serif;font-weight:800;fill:#16181d}.l{font-family:Archivo,sans-serif;font-weight:300;fill:#16181d}
.k{font-family:'IBM Plex Mono',monospace;font-weight:500;letter-spacing:.14em;fill:#FF5A1F}
.b{font-family:'IBM Plex Sans',sans-serif;font-weight:400;fill:#16181d}.s{font-family:'IBM Plex Sans',sans-serif;font-weight:600;fill:#16181d}
</style></head><body><div class="wrap"><svg id="sv" width="540" height="960" viewBox="0 0 540 960" role="img" aria-label="__TITLE__"></svg></div>
<script>
(() => {
  if (/[?&]embed=1/.test(location.search)) { const w0 = document.querySelector('.wrap'); document.documentElement.style.background = 'transparent'; document.body.style.background = 'transparent';
    const fit = () => { const s = Math.min(1, document.documentElement.clientWidth / 540); w0.style.transformOrigin = 'top left'; w0.style.transform = `scale(${s})`;
      w0.style.marginLeft = Math.max(0, (document.documentElement.clientWidth - 540 * s) / 2) + 'px'; document.body.style.height = (960 * s) + 'px'; document.body.style.overflow = 'hidden';
      if (window.parent !== window) window.parent.postMessage({bmH: Math.ceil(960 * s)}, '*'); };
    w0.style.margin = '0'; fit(); window.addEventListener('resize', fit); }
  const D = __DATA__, S = D.s, NS = 'http://www.w3.org/2000/svg', sv = document.getElementById('sv'), C = D.c, OR = '#FF5A1F', M = 30;
  const E = (tag, at, par) => { const e = document.createElementNS(NS, tag); for (const k in at) e.setAttribute(k, at[k]); (par || sv).appendChild(e); return e; };
  const T = (par, x, y, txt, cls, size, anchor) => { const e = E('text', {x, y, class: cls, 'text-anchor': anchor || 'start'}, par); e.style.fontSize = size + 'px'; e.textContent = txt; return e; };
  const wrap = (el, x, maxW, lh) => { const words = el.textContent.split(' '); el.textContent = ''; let ln = E('tspan', {x}, el), cur = '';
    words.forEach((w) => { const tr = cur ? cur + ' ' + w : w; ln.textContent = tr; if (ln.getComputedTextLength() > maxW && cur) { ln.textContent = cur; ln = E('tspan', {x, dy: lh}, el); ln.textContent = w; cur = w; } else cur = tr; }); };
  const cl = (v) => Math.max(0, Math.min(1, v)), ease = (u) => { u = cl(u); return u * u * (3 - 2 * u); };
  const back = (u) => { u = cl(u); const c = 1.7; return 1 + (c + 1) * Math.pow(u - 1, 3) + c * Math.pow(u - 1, 2); };
  const win = (t, a, b, f) => ease((t - a) / (f || 0.4)) * (1 - ease((t - b + (f || 0.4)) / (f || 0.4)));   // fade in at a, out by b
  const fmt = (s, k) => { const m = /^([+−-]?)(\d+(?:\.\d+)?)(%?)$/.exec(s); if (!m) return s; const dec = (m[2].split('.')[1] || '').length; return m[1] + (+m[2] * k).toFixed(dec) + m[3]; };
  const cnt = (k) => 1 - Math.pow(1 - cl(k), 3);

  // header: the hook stays the whole Short (and is the first frame)
  T(sv, M, 54, S.kicker, 'k', 14);
  T(sv, M, 106, S.hook[0], 'd', 40);
  const h2 = T(sv, M, 154, S.hook[1], 'd', 40); h2.style.fill = OR;

  // beat 1 (0-4.6 s): before / after cards counting up
  const B1 = E('g', {}), cols = [];
  T(B1, M, 214, 'BEFORE AND AFTER THE CHANGE', 'k', 13).style.fill = '#16181d';
  D.cmp.cols.forEach((col, i) => { const x = M + i * 246, g = E('g', {}, B1), hot = !!col.hot;
    E('rect', {x, y: 236, width: 234, height: 330, rx: 26, fill: hot ? C : '#f5f4f2'}, g);
    const lab = T(g, x + 22, 274, col.label.toUpperCase(), 'k', 13); lab.style.fill = hot ? 'rgba(255,255,255,.8)' : '#5f6168';
    const rec = T(g, x + 20, 366, col.rec, 'l', 84); rec.style.fill = hot ? '#fff' : '#16181d';
    const rows = col.rows.map(([a, v], j) => { const y = 418 + j * 48;
      E('line', {x1: x + 22, x2: x + 212, y1: y - 26, y2: y - 26, stroke: hot ? 'rgba(255,255,255,.3)' : 'rgba(17,18,20,.12)'}, g);
      T(g, x + 22, y, a, 'b', 18).style.fill = hot ? '#fff' : '#16181d';
      const vt = T(g, x + 212, y, v, 's', 20, 'end'); vt.style.fill = hot ? '#fff' : '#16181d'; return [vt, v]; });
    cols.push({g, rec, recS: col.rec, rows, at: 0.25 + i * 1.0}); });
  const n1 = T(B1, M, 604, D.cmp.note, 'b', 15); n1.style.fill = '#8a8f99';

  // beat 2 (4.6-14.8 s): the coach's decisions stack up; the current one is big with its detail
  const B2 = E('g', {}), N = S.decisions.length, DT = 2.5, D0 = 4.7;
  const k2 = T(B2, M, 214, "THE COACH'S DECISIONS", 'k', 13); k2.style.fill = '#16181d';
  const rows2 = S.decisions.map((d, i) => { const y = 238 + i * 66, g = E('g', {}, B2);
    const dot = E('circle', {cx: M + 20, cy: y + 26, r: 20, fill: '#fff', stroke: '#d5d6da', 'stroke-width': 2.5}, g);
    const num = T(g, M + 20, y + 33, String(i + 1), 'd', 20, 'middle');
    const tt = T(g, M + 56, y + 34, d.title, 'd', 26);
    return {g, dot, num, tt, at: D0 + i * DT}; });
  // detail panel for the current decision
  const P = E('g', {}); const py = 238 + N * 66 + 20;
  E('rect', {x: M - 6, y: py, width: 540 - 2 * M + 12, height: 250, rx: 22, fill: '#f5f4f2'}, P);
  const details = S.decisions.map((d, i) => { const g = E('g', {}, P);
    const ln = T(g, M + 16, py + 46, d.line, 'b', 22); wrap(ln, M + 16, 540 - 2 * M - 30, 30);
    const v = d.viz, vy = py + 170, parts = {};
    if (v[0] === 'out') { const o = T(g, M + 16, vy, v[1], 's', 30); o.style.fill = '#8a8f99'; o.style.textDecoration = 'line-through';
      const ow = 30 + v[1].length * 15; const ar = T(g, M + 16 + ow + 10, vy, '→', 's', 30); ar.style.fill = '#8a8f99';
      const inn = T(g, M + 16 + ow + 58, vy, v[3], 'd', 34); inn.style.fill = C; parts.inn = inn; }
    if (v[0] === 'num') { const nn = T(g, M + 16, vy + 10, v[1], 'l', 72); nn.style.fill = C; T(g, M + 170, vy, v[2], 's', 20); parts.num = [nn, v[1]]; }
    if (v[0] === 'text') { const tx = T(g, M + 16, vy, v[1], 's', 22); tx.style.fill = C; }
    if (v[0] === 'bars') { parts.bars = [v[1], v[2]].map((pc, j) => { const y = vy - 46 + j * 38;
        T(g, M + 16, y + 14, j ? 'Last 5' : 'First 7', 's', 16);
        E('rect', {x: M + 96, y, width: 300, height: 18, rx: 9, fill: '#e3e4e8'}, g);
        const br = E('rect', {x: M + 96, y, width: 0, height: 18, rx: 9, fill: j ? C : '#b9bcc4'}, g);
        const lt = T(g, M + 470, y + 15, pc + '%', 'd', 18, 'end'); return {br, lt, pc: +pc, j}; }); }
    return {g, parts, at: D0 + i * DT}; });

  // beat 3 (14.9-19 s): the verdict
  const B3 = E('g', {});
  T(B3, M, 214, 'THE VERDICT', 'k', 13).style.fill = '#16181d';
  const v1 = T(B3, M, 300, S.verdict[0], 'd', 46), v2 = T(B3, M, 356, S.verdict[1], 'd', 46); v2.style.fill = C;
  const vl = T(B3, M, 420, S.verdict_line, 'b', 21); wrap(vl, M, 540 - 2 * M, 29);
  const chk = E('g', {}, B3);
  S.decisions.forEach((d, i) => { const y = 520 + i * 44; E('circle', {cx: M + 12, cy: y - 7, r: 12, fill: OR}, chk);
    T(chk, M + 12, y - 2, '✓', 's', 15, 'middle').style.fill = '#fff'; T(chk, M + 36, y, d.title, 's', 20); });

  // footer
  const ft = T(sv, M, 872, 'Sources: ' + S.sources, 'b', 11.5); ft.style.fill = '#8a8f99'; wrap(ft, M, 540 - 2 * M, 15);
  T(sv, M, 930, 'Unofficial fan content. Not affiliated with the NBA or any team.', 'b', 11.5).style.fill = '#8a8f99';
  T(sv, 540 - M, 930, 'BOX & MOTION HOOPS', 'k', 11.5, 'end').style.fill = '#16181d';

  const TOTAL = D.total, E2 = D0 + N * DT;
  function render(t) {
    // beat 1
    B1.style.opacity = 1 - ease((t - 4.25) / 0.4);
    cols.forEach((c) => { const u = back((t - c.at) / 0.55); c.g.style.opacity = cl((t - c.at) / 0.2);
      c.g.setAttribute('transform', `translate(0,${(1 - u) * 40})`); const k = cnt((t - c.at - 0.2) / 1.1);
      const [a, b] = c.recS.split('-'); c.rec.textContent = Math.round(+a * k) + '-' + Math.round(+b * k);
      c.rows.forEach(([el, v], j) => { el.textContent = fmt(v, cnt((t - c.at - 0.35 - j * 0.2) / 1.0)); }); });
    n1.style.opacity = cl((t - 2.2) / 0.4);
    // beat 2
    B2.style.opacity = win(t, D0 - 0.2, E2 + 0.2, 0.4); P.style.opacity = B2.style.opacity;
    let off = -(N - 1) * 66; for (let i = 1; i < N; i++) off += ease((t - (D0 + i * DT)) / 0.45) * 66; P.setAttribute('transform', `translate(0,${off})`);
    rows2.forEach((r, i) => { const on = t >= r.at, cur = on && t < r.at + DT, u = back((t - r.at) / 0.45);
      r.g.style.opacity = cl((t - r.at) / 0.2); r.g.setAttribute('transform', `translate(${(1 - u) * -30},0)`);
      r.dot.setAttribute('fill', on ? OR : '#fff'); r.dot.setAttribute('stroke', on ? OR : '#d5d6da'); r.num.style.fill = on ? '#fff' : '#16181d';
      r.tt.style.fill = cur ? '#16181d' : '#8a8f99'; });
    details.forEach((d) => { const a = win(t, d.at + 0.15, d.at + DT + 0.05, 0.3); d.g.style.opacity = a; const k = cnt((t - d.at - 0.3) / 0.9);
      if (d.parts.num) d.parts.num[0].textContent = fmt(d.parts.num[1], k);
      if (d.parts.inn) d.parts.inn.setAttribute('transform', `translate(${(1 - back((t - d.at - 0.5) / 0.5)) * 30},0)`), d.parts.inn.style.opacity = cl((t - d.at - 0.5) / 0.25);
      if (d.parts.bars) d.parts.bars.forEach((b) => { const kb = cnt((t - d.at - 0.35 - b.j * 0.45) / 0.9); b.br.setAttribute('width', 300 * b.pc / 50 * kb); b.lt.textContent = (b.pc * kb).toFixed(1) + '%'; }); });
    // beat 3
    B3.style.opacity = cl((t - E2 - 0.1) / 0.4);
    v1.style.opacity = cl((t - E2 - 0.2) / 0.3); v2.style.opacity = cl((t - E2 - 0.6) / 0.3); vl.style.opacity = cl((t - E2 - 1.0) / 0.3);
    [...chk.children].forEach((el, j) => { el.style.opacity = cl((t - E2 - 1.4 - Math.floor(j / 3) * 0.25) / 0.2); });
    window.__t = t;
  }
  const start = performance.now();
  function tick() { if (!window.__hold) { render(((performance.now() - start) / 1000) % TOTAL); requestAnimationFrame(tick); } }
  render(0); requestAnimationFrame(tick);
  window.__A = {render, total: TOTAL, loop: {start: 0.5, cut: TOTAL}, poster: 2.6};
})();
</script></body></html>"""
out = os.path.join(ROOT, "src", "anim", X["anim"])
open(out, "w").write(HTML.replace("__TITLE__", X["title"]).replace("__FONTS__", FONTS).replace("__DATA__", json.dumps(D, ensure_ascii=False)))
print(out)
