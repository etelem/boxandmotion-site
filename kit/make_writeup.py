"""Write a game page's text recap from a finished (fact-checked) reel config.
Usage (from the repo root): python3 kit/make_writeup.py kit/configs/<date>-<AWAY>-at-<HOME>.json "Headline"
Writes data/writeups/<date>-<AWAY>-<HOME>.json: headline, dek, three things that decided it, where it was won, top performers,
and the quarter line score. Everything comes from numbers and captions already verified in the config, so the page and the
video always agree. The headline is the only new text: keep it short, factual, no hype beyond the facts (e.g.
"Brunson and Towns take Cleveland")."""
import json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
cfg_path, headline = sys.argv[1], sys.argv[2].strip().rstrip('.')
c = json.load(open(cfg_path)); D = c['D']
base = os.path.basename(cfg_path)[:-5]                      # 2026-11-07-NYK-at-CLE
date, away, home = base[:10], base[11:14], base[18:21]
key = f'{date}-{away}-{home}'
us = c['team']; them = home if us == away else away

def num(k): return int(re.search(k + r':\s*(\d+)', D).group(1))
quarters = json.loads(re.search(r'quarters:\s*(\[\[.*?\]\])', D).group(1))
scorers = re.findall(r"\{name: '([^']+)', pts: (\d+), note: '([^']*)'\}", D)
edges = [(l, int(a), int(b)) for l, a, b in re.findall(r"\{label: '([^']+)', us: (\d+), them: (\d+)\}", D)]
us_pts, them_pts = num('us'), num('them')

# captions: the right-hand side of each template sub, matched by the template text it replaced
def cap(prefix):
    for a, b in c['subs']:
        if a.startswith(prefix):
            m = re.search(r":\s*\['(.*)'\]\)?\s*$", b)
            if m: return m.group(1).replace("\\'", "'")
    raise SystemExit(f'caption not found for template text {prefix!r}; check the config')
lede = cap("['Luka scored 41.")
flow = cap("['Up 5 at the half,")
star_t, star_d = cap("['Luka’s 41'"), cap("['16 in the first quarter,")
combined = cap("['Luka and Reaves:")
how_t, how_d = cap("['Lost at the line"), cap("['Lakers in gold,")
how_d = re.sub(r'^[^.]*\bin gray\.\s*', '', how_d)              # drop the chart legend ("Knicks in blue, Cavaliers in gray.")

q_us, q_them = [q[0] for q in quarters], [q[1] for q in quarters]
ot_us, ot_them = us_pts - sum(q_us), them_pts - sum(q_them)
if ot_us or ot_them: q_us.append(ot_us); q_them.append(ot_them)
lead_edges = [e for e in edges if e[1] > e[2]][:2]
edge_txt = '; '.join(f'{l.lower()} {a}–{b}' for l, a, b in lead_edges)

w = {
    'headline': headline,
    'dek': lede,
    'three': [
        [star_t, star_d],
        [flow, combined + '.' if not combined.endswith('.') else combined],
        [how_t, (edge_txt[0].upper() + edge_txt[1:] + '. ' if edge_txt else '') + how_d],
    ],
    'battle': [[l, a, b] for l, a, b in edges[:4]],
    'battle_labels': [us, them],
    'top': [[n, us, note.replace(' · ', ', '), int(p)] for n, p, note in scorers[:4]],
    'linescore': {'away': q_us if us == away else q_them, 'home': q_them if us == away else q_us, 'ot': bool(ot_us or ot_them)},
    'source': os.path.relpath(cfg_path, ROOT),
}
# the losing team's side: their top scorers from the box score (config "loser_top": [[name, pts, note], ...])
if c.get('loser_top'):
    w['loser'] = {'top': [[n, them, note, int(p)] for n, p, note in c['loser_top'][:3]], 'source': 'box score'}
out = os.path.join(ROOT, 'data', 'writeups', key + '.json'); os.makedirs(os.path.dirname(out), exist_ok=True)
json.dump(w, open(out, 'w'), indent=1, ensure_ascii=False)
print('wrote', os.path.relpath(out, ROOT))
