"""Light-court poster frames for the game cards (src/posters/<key>-light.jpg, 720x360).
Usage (repo root): python3 kit/make_posters.py            -> makes any missing poster for reels/<key>/
                   python3 kit/make_posters.py <key> ...  -> (re)makes those
Each poster is the recap reel's play-of-the-game moment (kit/poster.js drives the reel to the play scene, hides the
header text and re-skins it on the site's light gray). Framing depends on the play (kit/configs/<date>-<AWAY>-at-<HOME>.json
play.subP): a three is a wide shot with the ball in flight, a drive is tight on the rim and players, a free throw or
jumper sits in between."""
import glob, json, os, re, subprocess, sys, tempfile
from PIL import Image

CROP = {'three': (240, 140, 1480, 760), 'jumper': (380, 190, 1480, 740), 'ft': (380, 190, 1480, 740), 'drive': (560, 300, 1480, 760)}
FRAC = {'three': 0.55, 'jumper': 0.55, 'ft': 0.55, 'drive': 0.62}


def kind(sub):
    s = sub.lower()
    if 'at the line' in s: return 'ft'
    if any(w in s for w in ('drive', 'lane', 'baseline', 'dunk', 'layup')): return 'drive'
    m = re.search(r'from (\d+) feet', s)
    if 'three' in s or (m and int(m.group(1)) >= 22): return 'three'
    return 'jumper'


def config_for(key):
    d, a, h = key[:10], key[11:14], key[15:18]
    p = f'kit/configs/{d}-{a}-at-{h}.json'
    return json.load(open(p)) if os.path.isfile(p) else {}


def make(key):
    k = kind(config_for(key).get('play', {}).get('subP', ''))
    raw = os.path.join(tempfile.gettempdir(), f'poster-{key}.png')
    subprocess.run(['node', 'kit/poster.js', os.path.abspath(f'reels/{key}/index.html'), raw, str(FRAC[k]), '1'], check=True)
    Image.open(raw).convert('RGB').crop(CROP[k]).resize((720, 360), Image.LANCZOS).save(f'src/posters/{key}-light.jpg', quality=80, optimize=True)
    print(key, k)


os.makedirs('src/posters', exist_ok=True)
keys = sys.argv[1:] or [os.path.basename(os.path.dirname(p)) for p in sorted(glob.glob('reels/*/index.html'))
                        if not os.path.isfile(f'src/posters/{os.path.basename(os.path.dirname(p))}-light.jpg')]
for key in keys:
    try: make(key)
    except Exception as e: print('poster failed', key, e)
