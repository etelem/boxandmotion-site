"""Put a finished reel on the site: reels/<game key>/index.html (game key = YYYY-MM-DD-AWAY-HOME).
Usage (from the repo root): python3 kit/publish_reel.py kit/out/X-reel.html 2026-11-07-SAS-POR
The site's game page then opens with this reel. All reels share one soundtrack at reels/soundtrack.mp3."""
import sys, os, shutil, json
here = os.path.dirname(os.path.abspath(__file__)); root = os.path.dirname(here)
src, key = sys.argv[1], sys.argv[2]
d, a, h = key[:10], key[11:14], key[15:18]
season = json.load(open(os.path.join(root, 'data', 'season.json')))
assert any(g[0] == d and g[1] == a and g[3] == h for g in season['games']), f"{key} is not a game in data/season.json (run the nightly update first, or check away/home order)"
t = open(src).read()
assert "el.src = 'soundtrack.mp3'" in t
t = t.replace("el.src = 'soundtrack.mp3'", "el.src = '../soundtrack.mp3'")
out = os.path.join(root, 'reels', key); os.makedirs(out, exist_ok=True)
open(os.path.join(out, 'index.html'), 'w').write(t)
if not os.path.exists(os.path.join(root, 'reels', 'soundtrack.mp3')):
    shutil.copy(os.path.join(here, 'soundtrack.mp3'), os.path.join(root, 'reels', 'soundtrack.mp3'))
print('published', os.path.relpath(os.path.join(out, 'index.html'), root))
