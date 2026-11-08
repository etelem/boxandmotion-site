"""Look sheet: every star in kit/looks.json drawn standing in his team's home kit, for Elan to approve.
Usage: python3 kit/make_looksheet.py -> kit/out/looksheet.html"""
import os, sys, json, html
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from looks import LOOKS, LOOK_KEYS, kit_for
base = open(os.path.join(HERE, 'base-reel.html')).read().split('\n')
start = next(i for i, l in enumerate(base) if l.startswith('  const POSES = {'))
end = next(i for i in range(start, len(base)) if base[i] == '  }' and i > start + 12)
FIGURE = '\n'.join(base[start:end + 1])
FIGURE_REAL = open(os.path.join(HERE, 'figure-real.js')).read()
TEAM = {"Luka Dončić": ("LAL", "77"), "Stephen Curry": ("GSW", "30"), "Victor Wembanyama": ("SAS", "1"), "Nikola Jokić": ("DEN", "15"),
        "Giannis Antetokounmpo": ("MIA", ""), "Shai Gilgeous-Alexander": ("OKC", "2"), "Jayson Tatum": ("BOS", "0"), "Jaylen Brown": ("PHI", ""),
        "Anthony Edwards": ("MIN", "5"), "Jalen Brunson": ("NYK", "11"), "Karl-Anthony Towns": ("NYK", "32"), "LeBron James": ("PHI", ""),
        "Kevin Durant": ("HOU", "7"), "Joel Embiid": ("PHI", "21"), "Tyrese Maxey": ("PHI", "0"), "Donovan Mitchell": ("CLE", "45"),
        "Devin Booker": ("PHX", "1"), "Anthony Davis": ("WAS", ""), "Cade Cunningham": ("DET", "2"), "Trae Young": ("WAS", ""),
        "Ja Morant": ("POR", ""), "Kawhi Leonard": ("TOR", ""), "Damian Lillard": ("POR", "0"), "Paolo Banchero": ("ORL", "5"),
        "Jimmy Butler": ("GSW", "10"), "Domantas Sabonis": ("SAC", "11"), "Alperen Şengün": ("HOU", "28"), "Chet Holmgren": ("OKC", "7"),
        "Austin Reaves": ("LAL", "15"), "Lauri Markkanen": ("UTA", "23"), "Zion Williamson": ("NOP", "1"), "De'Aaron Fox": ("SAS", "4")}
people = []
for name, v in LOOKS.items():
    if name.startswith('_'): continue
    team, num = TEAM.get(name, ("GSW", "0"))
    people.append({"team": team, "name": name, "status": v["status"], "num": num, "kit": kit_for(team, True), "look": {k: v[k] for k in LOOK_KEYS if k in v}})
HTML = """<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Star looks · Box &amp; Motion Hoops</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@700;800&family=IBM+Plex+Mono:wght@500&family=IBM+Plex+Sans:wght@400;600&display=swap">
<style>
body{margin:0;background:#111214;color:#f7f8f9;font-family:'IBM Plex Sans',system-ui,sans-serif;padding:24px}
h1{font-family:Archivo;font-weight:800;margin:0 0 6px}p{color:#a9adb4;margin:0 0 20px;max-width:46em}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:14px}
.c{background:radial-gradient(120% 95% at 12% 0%,#2b2e35,#17181b);border-radius:16px;padding:10px 10px 12px;text-align:center}
.c svg{width:100%;height:auto;display:block}.n{font-weight:600;font-size:14px}.s{font-family:'IBM Plex Mono';font-size:11px;letter-spacing:.12em;text-transform:uppercase;margin-top:2px}
.s.approved{color:#5ad17a}.s.proposed{color:#ffb35c}
.fig-o-phi{stroke:#ffd27a;fill:#ffd27a}.fig-skin{stroke:#2a2c31;fill:#2a2c31}.fig-shoe{stroke:#f7f8f9;fill:#f7f8f9}
.fig-num{font-family:Archivo;font-weight:800}.fig-hair{stroke:#2a2c31;fill:#2a2c31}.fig-band{fill:none}
</style></head><body>
<h1>Star looks</h1><p>Every star's look for recaps and Shorts, in his team's home kit. Green = approved, orange = proposed (used until you change it). Faces stay blank. Teams are this season's (2026-27); numbers are left off for players who moved this summer until checked. Tell me any changes by name.</p>
<div class="grid" id="g"></div>
<script>
const P = __P__;
const NS = 'http://www.w3.org/2000/svg';
const S = (tag, attrs, parent) => { const n = document.createElementNS(NS, tag); for (const k in attrs) n.setAttribute(k, attrs[k]); if (parent) parent.appendChild(n); return n; };
const T = (p, x, y, s, cls, size, anchor) => { const n = S('text', {x, y, class: cls, 'text-anchor': anchor || 'start'}, p); n.textContent = s; n.style.fontSize = size + 'px'; return n; };
const clamp = (v) => Math.max(0, Math.min(1, v)), lerp = (a, b, p) => a + (b - a) * p;
__FIGURE__
__FIGURE_REAL__
const g = document.getElementById('g');
P.forEach((p, i) => {
  const c = document.createElement('div'); c.className = 'c'; g.appendChild(c);
  const svg = S('svg', {viewBox: '0 0 200 330'}, c);
  const st = document.createElement('style'); st.textContent = `.k${i} .fig-kit-phi{stroke:${p.kit.jersey};fill:${p.kit.jersey}} .k${i} .fig-num{fill:${p.kit.number}} .k${i} .fig-band{stroke:${p.kit.number}}`; document.head.appendChild(st);
  const grp = S('g', {class: 'k' + i}, svg);
  const f = figureReal(grp, 'phi', 1.08, p.num, p.look);
  f.draw(POSES.dribble, 92, 318, 1.08, 1);
  const n = document.createElement('div'); n.className = 'n'; n.textContent = p.name + ' · ' + p.team; c.appendChild(n);
  const s = document.createElement('div'); s.className = 's ' + p.status; s.textContent = p.status; c.appendChild(s);
});
</script></body></html>"""
out = HTML.replace('__P__', json.dumps(people, ensure_ascii=False)).replace('__FIGURE__', FIGURE).replace('__FIGURE_REAL__', FIGURE_REAL)
os.makedirs(os.path.join(HERE, 'out'), exist_ok=True)
open(os.path.join(HERE, 'out', 'looksheet.html'), 'w').write(out)
print('wrote kit/out/looksheet.html', len(people))
