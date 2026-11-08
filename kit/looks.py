"""Shared look + kit helpers for every recap reel and Short.
look_for(name) -> the star's look keys from kit/looks.json (empty dict if none on file yet).
kit_for(team, home) -> {"jersey", "number"}: home = white with the team colour number, away = team colour with a white number."""
import os, json, unicodedata
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
LOOKS = json.load(open(os.path.join(HERE, 'looks.json')))
TEAMS = json.load(open(os.path.join(ROOT, 'data', 'teams.json')))
LOOK_KEYS = ('skin', 'hair', 'hairColor', 'beard', 'stubble', 'wristband', 'legSleeve', 'kneeSleeve', 'kneeSleeveFront', 'ankleBrace', 'frame')
AWAY_NUM = {'LAL': '#FDB927', 'GSW': '#FFC72C', 'DEN': '#FEC524', 'IND': '#FDBB30', 'CLE': '#FDBB30', 'UTA': '#F9A01B'}

def _key(s):
    return ''.join(c for c in unicodedata.normalize('NFKD', s) if not unicodedata.combining(c)).lower().replace('.', '').replace("'", '').strip()

def look_for(name):
    for k, v in LOOKS.items():
        if not k.startswith('_') and _key(k) == _key(name or ''):
            return {x: v[x] for x in LOOK_KEYS if x in v}, v.get('status'), v.get('signature')
    return {}, None, None

def kit_for(team, home=True):
    c1 = TEAMS[team]['c1']
    dark = c1.lower() in ('#3d3f45',)
    if home and team == 'LAL':  # the Lakers wear gold at home
        return {'jersey': '#FDB927', 'number': '#552583'}
    if home:
        return {'jersey': '#F4F4F2', 'number': '#111214' if dark else c1}
    return {'jersey': '#17181b' if dark else c1, 'number': AWAY_NUM.get(team, '#FFFFFF')}

def kit_css(kit):
    return f".fig-kit-phi{{stroke:{kit['jersey']};fill:{kit['jersey']}}}\n.fig-num{{fill:{kit['number']}}}\n.fig-band{{stroke:{kit['number']}}}"
