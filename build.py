"""Build the Box & Motion Hoops static site from data/*.json into dist/."""
import json, os, re, shutil, datetime
from html import escape as E
from urllib.parse import quote_plus

T = json.load(open("data/teams.json"))
S = json.load(open("data/season.json"))
# hand-picked featured games (game of the week candidates) before nightly write-ups are merged in
FEATURED_KEYS = set(S["featured"])
# nightly text recaps written from each fact-checked reel config (kit/make_writeup.py): same page sections as featured games
S.setdefault("linescores", {})
if os.path.isdir("data/writeups"):
    for fn in sorted(os.listdir("data/writeups")):
        if fn.endswith(".json"):
            _k = fn[:-5]; _w = json.load(open(f"data/writeups/{fn}"))
            S["featured"].setdefault(_k, _w)
            if _w.get("linescore") and _k not in S["linescores"]: S["linescores"][_k] = _w["linescore"]
O = json.load(open("data/odds.json"))
NEWSLETTER = "https://boxandmotion.beehiiv.com/subscribe"
OUT = "dist"
WEEKDAY = lambda d: datetime.date.fromisoformat(d).strftime("%a, %b %-d")
CONFNAME = {"East": "East", "West": "West"}

def ordinal(n): return f"{n}{'th' if 11<=n%100<=13 else {1:'st',2:'nd',3:'rd'}.get(n%10,'th')}"
def rec(c): w, l = S["standings"][c]; return f"{w}–{l}"
def seed(c): return f"{ordinal(S['seeds'][c])} in the {T[c]['conf']}"
def chg(n): return "—" if n == 0 else (f"+{n}%" if n > 0 else f"−{abs(n)}%")
def chgcls(n): return "up" if n > 0 else "down" if n < 0 else "dim"

# ---- games with running records ----
before = {k: list(v) for k, v in S["standings"].items()}
for d, a, sa, h, sh, _ in S["games"]:
    w, l = (a, h) if sa > sh else (h, a); before[w][0] -= 1; before[l][1] -= 1
run = {k: list(v) for k, v in before.items()}
GAMES = []
for d, a, sa, h, sh, ot in S["games"]:
    w, l = (a, h) if sa > sh else (h, a)
    run[w][0] += 1; run[l][1] += 1
    key = f"{d}-{a}-{h}"
    GAMES.append(dict(date=d, away=a, home=h, as_=sa, hs=sh, ot=ot, win=w, lose=l, key=key,
                      slug=f"{d}-{T[a]['slug']}-at-{T[h]['slug']}",
                      rec={a: f"{run[a][0]}–{run[a][1]}", h: f"{run[h][0]}–{run[h][1]}"},
                      featured=key in S["featured"], video=None))
LAST_DATE = max(g["date"] for g in GAMES)
LAST = [g for g in GAMES if g["date"] == LAST_DATE]
_ld = datetime.date.fromisoformat(LAST_DATE)
WEEK_START = (_ld - datetime.timedelta(days=_ld.weekday())).isoformat()
VIDEOS = S.get("videos", {})
def video_id(key):
    # a YouTube id written by the morning recap run (reels/<key>/youtube.txt) or set by hand in season.json
    f = f"reels/{key}/youtube.txt"
    if os.path.isfile(f):
        v = open(f).read().strip()
        if v: return v
    return VIDEOS.get(key) or S["featured"].get(key, {}).get("video")
REELS = {d for d in (os.listdir("reels") if os.path.isdir("reels") else []) if os.path.isfile(f"reels/{d}/index.html")}
for _g in GAMES: _g["video"] = video_id(_g["key"]); _g["reel"] = _g["key"] in REELS

def team_games(c): return [g for g in reversed(GAMES) if c in (g["away"], g["home"])]
def next_game(c):
    for day, tm, a, h in S["upcoming"]:
        if c in (a, h):
            return (f"vs. {T[h if c==a else a]['name']}" if c == h else f"at {T[h]['name']}"), f"{day} · {tm} ET"
    return None
def result_for(g, c):
    me, opp = (g["as_"], g["hs"]) if c == g["away"] else (g["hs"], g["as_"])
    o = g["home"] if c == g["away"] else g["away"]
    where = "at" if c == g["away"] else "vs."
    return ("W" if me > opp else "L"), f"{max(me,opp)}–{min(me,opp)}", f"{where} {T[o]['name']}"
def last_line(c):
    g = team_games(c)[0]; r, sc, opp = result_for(g, c); return f"{r} {sc} {opp}"
def yt(g):
    day = datetime.date.fromisoformat(g["date"]).strftime("%B %-d %Y")
    q = f"{T[g['away']]['name']} vs {T[g['home']]['name']} highlights {day}"
    return "https://www.youtube.com/@NBA/search?query=" + quote_plus(q)

LINKS = json.load(open("data/links.json")) if os.path.isfile("data/links.json") else {}
def official_links(g):
    """Bottom-of-recap official video: the NBA channel's full-game highlights and the postgame interviews,
    linked directly when data/links.json has them, otherwise a search scoped to that game."""
    L = LINKS.get(g["key"], {})
    day = datetime.date.fromisoformat(g["date"]).strftime("%B %-d %Y")
    hl = f'https://www.youtube.com/watch?v={L["highlights"]}' if L.get("highlights") else yt(g)
    w, l = g["win"], g["lose"]
    pg = (f'https://www.youtube.com/watch?v={L["postgame"]}' if L.get("postgame") else
          "https://www.youtube.com/results?search_query=" + quote_plus(f'{T[w]["name"]} {T[l]["name"]} postgame interviews {day}'))
    pgl = L.get("postgame_label") or ("Postgame interviews" if L.get("postgame") else f"Find postgame interviews: {T[w]['name']} vs {T[l]['name']}")
    return (f'<section class="sec"><div class="sec" style="gap:6px"><h2 class="h2">Official video</h2><p class="dim" style="margin:0">'
            f'Links to this game\'s official uploads on YouTube. We don\'t host or edit them.</p></div>'
            f'<div class="row" style="gap:10px"><a class="pill on" href="{hl}" target="_blank" rel="noopener">▶ {"Full game highlights (NBA)" if L.get("highlights") else "Game highlights on the NBA\'s channel"}</a>'
            f'<a class="pill" href="{pg}" target="_blank" rel="noopener">▶ {E(pgl)}</a></div></section>')

def watch_links(g):
    """Under the recap (Elan, Nov 13): one quiet "Watch" list with our Short and the official NBA highlights and postgame
    interviews (direct links from data/links.json when we have them, otherwise a search for that game), then a small
    subscribe line. Replaces the three big buttons and the separate "Official video" section."""
    L = LINKS.get(g["key"], {}); v = g["video"]
    day = datetime.date.fromisoformat(g["date"]).strftime("%B %-d %Y")
    w, l = g["win"], g["lose"]
    hl = f'https://www.youtube.com/watch?v={L["highlights"]}' if L.get("highlights") else yt(g)
    pg = (f'https://www.youtube.com/watch?v={L["postgame"]}' if L.get("postgame") else
          "https://www.youtube.com/results?search_query=" + quote_plus(f'{T[w]["name"]} {T[l]["name"]} postgame interviews {day}'))
    def row(href, title, src):
        return (f'<a class="wrow" href="{href}" target="_blank" rel="noopener"><span class="wplay">▶</span>'
                f'<span class="wt">{E(title)}</span><span class="ws">{E(src)} ↗</span></a>')
    rows = (row(f"https://youtube.com/shorts/{v}", "Our recap Short", "@boxandmotion") if v else "")
    rows += row(hl, "Full game highlights", "NBA" if L.get("highlights") else "NBA · search")
    rows += row(pg, L.get("postgame_label") or "Postgame interviews", "YouTube" if L.get("postgame") else "YouTube · search")
    return (f'<div class="watch"><p class="k" style="margin:0 0 2px">Watch</p>{rows}'
            f'<p class="wfine"><a href="https://www.youtube.com/@boxandmotion?sub_confirmation=1" target="_blank" rel="noopener">Subscribe on YouTube</a>'
            f'<span>·</span><a href="{NEWSLETTER}" target="_blank" rel="noopener">Get the newsletter</a></p></div>')

LOGO = '<svg width="28" height="28" viewBox="0 0 100 100" aria-hidden="true"><rect x="9" y="9" width="82" height="82" rx="9" fill="none" stroke="#111214" stroke-width="8"/><path d="M24 24L40 40M40 24L24 40" stroke="#111214" stroke-width="8" stroke-linecap="round"/><path d="M33 50C34 62 42 69 53 69" fill="none" stroke="#FF5A1F" stroke-width="6.5" stroke-linecap="round" stroke-dasharray="0 10.5"/><circle cx="68" cy="68" r="9.5" fill="none" stroke="#FF5A1F" stroke-width="7.5"/></svg>'
FAVICON = "data:image/svg+xml," + quote_plus(LOGO.replace('width="28" height="28" ', '').replace('aria-hidden="true"', 'xmlns="http://www.w3.org/2000/svg"')).replace("+", "%20")

def video_block(v):
    if not v:
        return '<section class="card pad empty"><span class="tag gold">Our recap video</span><p style="margin:8px 0 0">The drawn recap posts to <a href="https://www.youtube.com/@boxandmotion" target="_blank" rel="noopener">@boxandmotion on YouTube</a>. It will play here once it\'s up.</p></section>'
    return (f'<section class="card pad" style="display:flex;flex-wrap:wrap;gap:24px;align-items:center">'
            f'<div style="flex:0 1 340px;width:100%;max-width:340px;aspect-ratio:9/16;border-radius:16px;overflow:hidden;background:#111214">'
            f'<iframe src="https://www.youtube.com/embed/{v}" title="Box &amp; Motion recap video" style="width:100%;height:100%;border:0" loading="lazy" '
            f'allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe></div>'
            f'<div class="sec" style="gap:10px;flex:1 1 240px"><span class="tag gold">Our recap video</span><b class="d" style="font-size:32px">The game in 66 seconds</b>'
            f'<p class="dim" style="margin:0">Drawn play of the game, game flow, the star line and how it was won.</p>'
            f'<a class="pill" style="align-self:flex-start" href="https://youtube.com/shorts/{v}" target="_blank" rel="noopener">▶ Watch on YouTube</a></div></section>')

def page(path, title, body, active=None, desc="Every NBA game, explained in motion. Recaps, playoff odds and scouting reports.", band=""):
    depth = path.count("/"); R = "../" * depth
    nav = [("Teams", "teams/index.html", "Teams"), ("Last Night", "last-night/index.html", "Last Night"), ("Deep Dives", "deep-dives/index.html", "Deep Dives"),
           ("Playoff Odds", "odds/index.html", "Playoff Odds"), ("Newsletter", "newsletter/index.html", "Newsletter"), ("About", "about/index.html", "About")]
    # on phones Newsletter moves up beside My teams (as its own button); About stays the last tab (the row scrolls if it must)
    cls = {"Newsletter": " class=nl"}
    links = "".join(f'<a href="{R}{h}"{" aria-current=page" if n==active else ""}{cls.get(n, "")}>{lbl}</a>' for n, h, lbl in nav)
    html = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{E(title)}</title><meta name="description" content="{E(desc)}">
<meta property="og:title" content="{E(title)}"><meta property="og:description" content="{E(desc)}">
<link rel="icon" href="{FAVICON}">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@62..125,400..900&family=IBM+Plex+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@500&display=swap">
<link rel="stylesheet" href="{R}assets/site.css"></head>
<body data-root="{R}"><div class="pg"><div class="orbs" aria-hidden="true"><span></span><span></span></div>
<header class="glass"><nav aria-label="Main" class="w nav">
<a class="brand" href="{R}index.html">{LOGO}<span class="d">Box &amp; Motion <span class="grad">Hoops</span></span></a>
<div class="links">{links}</div>
<a href="{R}newsletter/index.html" class="pill nl-pill">✉ Newsletter</a><a href="{R}teams/index.html" class="pill hot favcount">★ My teams</a>
</nav></header>
{band}
<main class="w">{body}</main>
<footer class="w"><span>Box &amp; Motion Hoops · unofficial fan coverage, not affiliated with the NBA or any team.</span>
<span>Updated {S['updated']}. Video links go to official uploads only. <a href="{R}about/index.html">About</a></span></footer>
</div><script src="{R}assets/data.js"></script><script src="{R}assets/site.js"></script></body></html>"""
    full = os.path.join(OUT, path); os.makedirs(os.path.dirname(full) or OUT, exist_ok=True)
    open(full, "w").write(html)
    return R

def rel(depth): return "../" * depth

# ---- reusable bits ----
# Game-card images (Elan, Nov 13): "top" = the image only on each night's top card (Last Night, home, archive days);
# "all" = an image on every card. Switching is just this line + a rebuild; every recap gets its poster either way
# (kit/make_posters.py, run by the morning recap runs).
GAME_IMAGES = "top"

def _cfg_for(key):
    p = f"kit/configs/{key[:10]}-{key[11:14]}-at-{key[15:18]}.json"
    return json.load(open(p)) if os.path.isfile(p) else None

def story_score(g):
    """Which game leads the night (Nov 13): facts the recap already verified, never guessed.
    Close finish (<=3 or OT +3, 4-6 +2), comeback (winner down 15+ +3, 10-14 +2), big night (40+ or a triple-double +2,
    50+ +3), upset (winner's record clearly worse: 3+ fewer net wins +2), milestone in the verified headline (streak,
    season/career high +1). Ties: the game that got a YouTube Short, then the closer finish."""
    margin = abs(g["as_"] - g["hs"]); pts = 3 if (margin <= 3 or g["ot"]) else 2 if margin <= 6 else 0
    c = _cfg_for(g["key"]); D = c["D"] if c else ""
    def num(k):
        m = re.search(rf"\b{k}: *(\d+)", D); return int(m.group(1)) if m else 0
    if c:
        deficit = num("leadThem") if c.get("team") == g["win"] else num("leadUs")
        pts += 3 if deficit >= 15 else 2 if deficit >= 10 else 0
        stats = {k: int(v) for k, v in re.findall(r"\['(Points|Rebounds|Assists|Steals|Blocks)', (\d+)", D)}
        sp = stats.get("Points", 0); tens = sum(1 for v in stats.values() if v >= 10)
        pts += 3 if sp >= 50 else 2 if (sp >= 40 or tens >= 3) else 0
    def net(t):
        w, l = (int(x) for x in re.split(r"[-–]", g["rec"][t])); return w - l
    if net(g["win"]) <= net(g["lose"]) - 3: pts += 2
    head = ((S["featured"].get(g["key"]) or {}).get("headline") or "").lower()
    if any(w in head for w in ("straight", "streak", "season-high", "season high", "career-high", "career high")): pts += 1
    return (pts, 1 if g["video"] else 0, -margin)

def games_block(games, R, show_mine=True, images=None):
    """A night's games, best story first; the first card shown is the top card (with its image when images is "top").
    site.js moves a visitor's followed teams to the front and re-picks the top card on their screen."""
    gs = sorted(games, key=story_score, reverse=True)
    if os.environ.get("BM_DEBUG"): print([(g["key"], story_score(g)) for g in gs])
    cards = "".join(game_card(g, R, show_mine=show_mine, hero=(i == 0)) for i, g in enumerate(gs))
    return f'<div class="grid g3 games" data-games data-images="{images or GAME_IMAGES}">{cards}</div>'

def game_card(g, R, show_mine=True, img_on=True, hero=False):
    """Calm game card (Nov 12): white card; the recap's play-of-the-game frame as the image (src/posters/<key>.jpg, like a
    YouTube thumbnail); the story headline; team colors only as a thin edge and small dots; one action (tap the card)."""
    w = g["win"]; wt = T[w]
    href = f"{R}games/{g['slug']}/index.html"
    head = (S["featured"].get(g["key"]) or {}).get("headline") or f"{wt['name']} beat the {T[g['lose']]['name']}"
    lines = ""
    for c, sc in ((g["away"], g["as_"]), (g["home"], g["hs"])):
        lines += (f'<div class="sline {"win" if c==w else "lose"}"><span style="display:flex;align-items:center;gap:8px">'
                  f'<i class="tdot" style="background:{T[c]["c1"]}"></i>{E(T[c]["name"])} <span class="dim rec">{g["rec"][c]}</span></span><span>{sc}</span></div>')
    has_vid = g["video"] or g["reel"]
    poster = img_on and os.path.isfile(f"src/posters/{g['key']}-light.jpg")
    img = (f'<a class="gimg" href="{href}" aria-label="Watch the recap: {E(head)}"><img src="{R}posters/{g["key"]}-light.jpg" alt="" loading="lazy">'
           f'<span class="gplay">▶</span></a>' if poster else '')
    return f'''<div class="card gcard calm{' hero' if hero else ''}" data-teams="{g['away']} {g['home']}" data-key="{g['key']}" style="--team:{wt['c1']}">
{img}<div class="gbody"><div class="row" style="gap:8px;justify-content:space-between"><span class="k gk">Final{' · OT' if g['ot'] else ''} · {WEEKDAY(g['date'])}</span>{'<span class="tag hot mine-tag hidden">Your team</span>' if show_mine else ''}</div>
<a class="ghead" href="{href}">{E(head)}</a>{lines}
<div class="row" style="gap:14px;margin-top:4px"><a class="glink" href="{href}">{'▶ Watch the recap' if has_vid else 'Read the recap'}</a><a class="glink dim" href="{yt(g)}" target="_blank" rel="noopener">Highlights ↗</a></div></div></div>'''

def star_btn(c, big=False, light=False):
    style = f"border-color:{T[c]['c2']};color:#fff" if light else ""
    return f'<button type="button" class="pill star{" " if big else " sm "}" data-team="{c}" aria-pressed="false" style="{style}">★ <span class="lbl">Follow</span></button>'

def team_band(c, kicker, extra=""):
    t = T[c]
    return f'<section class="band" style="background:radial-gradient(90% 140% at 85% 0%,{t["c1"]} 0%,{t["dark"]} 80%)"><div class="w">{kicker}{extra}</div></section>'

# ---- deep dives (coach's boards from kit/boards configs, listed in data/deepdives.json) ----
DD = json.load(open("data/deepdives.json")) if os.path.isfile("data/deepdives.json") else {"boards": []}
BOARDS = []
for b in DD["boards"]:
    cfg = json.load(open(b["config"]))
    BOARDS.append(dict(b, **{k: cfg[k] for k in ("team", "coach", "title", "situation", "beats", "sources", "final", "game")}))
BOARDS.sort(key=lambda b: b["published"], reverse=True)
COACH_PAGES = {}   # team code -> (coach name, page path, latest board)
for b in BOARDS:
    COACH_PAGES.setdefault(b["team"], (b["coach"], f'coaches/{b["coach_slug"]}/index.html', b))
COACH_PAGES.setdefault("LAL", ("JJ Redick", "coaches/jj-redick/index.html", None))

# signature moves (one animation per star, from kit/moves configs, listed under "moves" in data/deepdives.json)
MOVES = []
for m in DD.get("moves", []):
    cfg = json.load(open(m["config"]))
    MOVES.append(dict(m, steps=cfg.get("steps", []), number=cfg.get("number", "")))
MOVES.sort(key=lambda m: m["published"], reverse=True)

# X's and O's: evergreen learn-the-game explainers (kit/xo configs, listed under "xo" in data/deepdives.json)
XO = []
for x in DD.get("xo", []):
    cfg = json.load(open(x["config"]))
    XO.append(dict(x, title=cfg["title"], sub=cfg["situation"], beats=cfg["beats"]))
XO.sort(key=lambda x: x["published"], reverse=True)

# Trend board: good, lucky or in trouble? One team per Short, all 30 teams on the chart (kit/make_team_trend.py, listed
# under "trends" in data/deepdives.json; numbers frozen at publish, sources on the board itself)
TRENDS = sorted(DD.get("trends", []), key=lambda x: x["published"], reverse=True)

def trend_card(R, x, big=False):
    t = T[x["team"]]
    return (f'<a href="{R}trends/{x["slug"]}/index.html" class="card pad" style="display:flex;flex-direction:column;gap:6px;{"min-height:260px;" if big else ""}justify-content:flex-end;background:#fff">'
            f'<span class="tag hot">Trend board · {E(t["name"])}</span><b class="d" style="font-size:{40 if big else 30}px;margin-top:4px">{E(x["title"])}</b><span class="dim">{E(x["dek"])}</span></a>')

def xo_card(R, x, big=False):
    return (f'<a href="{R}xo/{x["slug"]}/index.html" class="card pad" style="display:flex;flex-direction:column;gap:6px;{"min-height:260px;" if big else ""}justify-content:flex-end;background:#f7f6f1">'
            f'<span class="tag hot">X\'s and O\'s</span><b class="d" style="font-size:{40 if big else 30}px;margin-top:4px">{E(x["title"])}</b><span class="dim">{E(x["dek"])}</span></a>')

def move_card(R, m, big=False):
    t = T[m["team"]]
    return (f'<a href="{R}moves/{m["slug"]}/index.html" class="card pad" style="display:flex;flex-direction:column;gap:6px;{"min-height:260px;" if big else ""}justify-content:flex-end;'
            f'background:radial-gradient(120% 140% at 100% 0%,{t["c1"]} 0%,{t["dark"]} 75%);color:#fff;border:0"><span class="tag gold">Signature move · {E(t["name"])}</span>'
            f'<b class="d" style="font-size:{40 if big else 30}px">{E(m["player"])}: {E(m["title"])}</b><span style="opacity:.85">{E(m["dek"])}</span></a>')

def anim_frame(R, file, label, music=None):
    """An animation page in an iframe that sizes itself (the page posts its height). Boards and X's and O's carry their own
    Film Room button under the court; other animations get a "Play with sound" button here, playing `music` (a site path)."""
    btn = (f'<button type="button" class="pill snd" data-snd="{R}{music}" style="align-self:flex-start">▶ Play with sound</button>' if music else '')
    return (f'<div class="anim-wrap" style="display:flex;flex-direction:column;gap:10px">'
            f'<iframe class="anim" src="{R}anim/{file}?embed=1" title="{E(label)}" loading="lazy" style="width:100%;border:0;display:block;height:560px;border-radius:18px"></iframe>'
            f'{btn}</div>')

def board_card(R, b, big=False):
    t = T[b["team"]]
    return (f'<a href="{R}coaches/{b["coach_slug"]}/index.html" class="card pad" style="display:flex;flex-direction:column;gap:6px;'
            f'{"min-height:260px;justify-content:flex-end;" if big else ""}background:#f7f6f1"><span class="tag">Coach\'s board · {E(t["name"])}</span>'
            f'<b class="d" style="font-size:{40 if big else 30}px;margin-top:4px">{E(b["coach"])}: {E(b["title"])}</b><span class="dim">{E(b["dek"])}</span></a>')

PLAYERS = []
if os.path.isdir("data/players"):
    for fn in sorted(os.listdir("data/players")):
        if fn.endswith(".json"): PLAYERS.append(json.load(open(f"data/players/{fn}")))
PLAYERS.sort(key=lambda x: x["published"], reverse=True)

# the home page's "New" chips: the newest deep dive, plus the next one if it came out within a day of it (two pieces the same night)
_NEW = sorted([("2026-11-07", "players/luka-doncic/index.html", "New: Luka scouting report")]
                   + [(b["published"], f'coaches/{b["coach_slug"]}/index.html', f'New: {b["coach"]}\'s board') for b in BOARDS]
                   + [(m["published"], f'moves/{m["slug"]}/index.html', f'New: {m["player"]}\'s signature move') for m in MOVES]
                   + [(x["published"], f'xo/{x["slug"]}/index.html', f'New X\'s and O\'s: {x["term"]}') for x in XO]
                   + [(P["published"], f'players/{P["slug"]}/index.html', f'New: {P["name"]} scouting report') for P in PLAYERS]
                   + [(x["published"], f'trends/{x["slug"]}/index.html', f'New trend: {x["short"]}') for x in TRENDS],
                   key=lambda x: x[0], reverse=True)
_ts = lambda v: datetime.datetime.fromisoformat(v if "T" in v else v + "T12:00")
LATEST_DD = [_NEW[0]] + [n for n in _NEW[1:2] if (_ts(_NEW[0][0]) - _ts(n[0])).total_seconds() <= 24 * 3600]

def player_card(R, P, big=False):
    t = T[P["team"]]
    return (f'<a href="{R}players/{P["slug"]}/index.html" class="card pad" style="display:flex;flex-direction:column;gap:6px;{"min-height:260px;" if big else ""}justify-content:flex-end;'
            f'background:radial-gradient(120% 140% at 100% 0%,{t["c1"]} 0%,{t["dark"]} 75%);color:#fff;border:0"><span class="tag gold">Scouting report · {E(t["name"])}</span>'
            f'<b class="d" style="font-size:{40 if big else 30}px">{E(P["name"])}</b><span style="opacity:.85">{E(P["card"])}</span></a>')

# ---- data.js for client ----
shutil.rmtree(OUT, ignore_errors=True)  # start clean so removed pages disappear
if os.path.isdir("reels"): shutil.copytree("reels", f"{OUT}/reels")
if os.path.isdir("src/anim"): shutil.copytree("src/anim", f"{OUT}/anim")
if os.path.isdir("src/posters"): shutil.copytree("src/posters", f"{OUT}/posters")
if os.path.isdir("src/audio"): shutil.copytree("src/audio", f"{OUT}/audio")
os.makedirs(f"{OUT}/assets", exist_ok=True)
client = {"teams": {c: {"name": T[c]["name"], "slug": T[c]["slug"], "c1": T[c]["c1"], "c2": T[c]["c2"], "dark": T[c]["dark"],
          "rec": rec(c), "seed": seed(c), "top6": O[c]["top6"], "chg": chg(O[c]["chg"]), "last": last_line(c)} for c in T}}
open(f"{OUT}/assets/data.js", "w").write("window.BM=" + json.dumps(client, ensure_ascii=False) + ";")
shutil.copy("src/site.css", f"{OUT}/assets/site.css"); shutil.copy("src/site.js", f"{OUT}/assets/site.js")

# ---- home ----
R = ""
movers = sorted(T, key=lambda c: -abs(O[c]["chg"]))[:1][0]
_gk = S.get("gotw") or max(FEATURED_KEYS)
gotw = next(g for g in GAMES if g["key"] == _gk)
fz = S["featured"][gotw["key"]]
risers = sorted(T, key=lambda c: -O[c]["chg"])[:3]; fallers = sorted(T, key=lambda c: O[c]["chg"])[:3]
def mini(c): return f'<a href="{R}teams/{T[c]["slug"]}/index.html" style="display:flex;justify-content:space-between;padding:10px 0;border-top:1px solid var(--line);text-decoration:none"><span><b>{E(T[c]["name"])}</b> <span class="dim">{rec(c)}</span></span><span><b>{O[c]["top6"]}%</b> <span class="{chgcls(O[c]["chg"])}">{chg(O[c]["chg"])}</span></span></a>'
home = f'''
<section class="sec">
 <div class="between"><div class="sec" style="gap:8px"><p class="k">Your teams · tap ★ on any team to follow</p><h1 class="h1">The Box Score, <span class="grad" style="white-space:nowrap">in Motion.</span></h1></div>
 <div class="row" style="gap:12px">
  <a class="chip" href="last-night/index.html"><span class="dot"></span>{len(LAST)} games last night</a>
  <a class="chip" href="odds/index.html"><span class="dot"></span>Playoff odds mover: {E(T[movers]['name'])} {chg(O[movers]['chg'])} this week</a>
  {"".join(f'<a class="chip" href="{n[1]}"><span class="dot"></span>{E(n[2])}</a>' for n in LATEST_DD)}
 </div></div>
 <div id="mine" class="grid g3"></div>
 <div id="mine-empty" class="card pad empty hidden"><b class="d" style="font-size:26px">Pick your teams</b><p class="dim" style="margin:6px 0 14px">Follow teams to see their record, odds and last game here. Saved on this device, no sign-up.</p><div class="row"><button class="pill star" data-team="LAL">★ Lakers</button><button class="pill star" data-team="PHI">★ 76ers</button><button class="pill star" data-team="NYK">★ Knicks</button><a class="pill" href="teams/index.html">All 30 teams →</a></div></div>
</section>
<section class="sec">
 <div class="between"><div class="sec" style="gap:6px"><p class="k">{WEEKDAY(LAST_DATE)}</p><h2 class="h2">Last night</h2></div>
 <div class="tabs"><button class="pill" data-mode="mine">Your teams</button><button class="pill" data-mode="all">All {len(LAST)} games</button></div></div>
 {games_block(LAST, R)}
 <p class="dim none-note hidden" style="margin:0">None of your teams played last night. <button class="pill sm" data-mode="all">Show all games</button></p>
 <a href="last-night/index.html" style="font-weight:600">All of last night and earlier this week →</a>
</section>
<section class="card" style="overflow:hidden;display:flex;flex-wrap:wrap">
 <a href="games/{gotw['slug']}/index.html" style="flex:1 1 360px;min-height:260px;background:radial-gradient(120% 140% at 100% 0%,{T[gotw['win']]['c1']} 0%,#111214 75%);color:#fff;padding:28px;display:flex;flex-direction:column;justify-content:flex-end;text-decoration:none">
  <span class="k" style="color:#c4ced4">Game of the week · {WEEKDAY(gotw['date'])}</span><span class="d" style="font-size:clamp(40px,6vw,64px)">{E(T[gotw['win']]['name'])} {max(gotw['as_'],gotw['hs'])}<br>{E(T[gotw['lose']]['name'])} {min(gotw['as_'],gotw['hs'])}</span></a>
 <div style="flex:1 1 360px;padding:28px;display:flex;flex-direction:column;gap:10px;justify-content:center">
  <span class="tag gold">Featured recap</span><b class="d" style="font-size:34px">{E(fz['headline'])}</b><p style="margin:0;font-size:18px">{E(fz['dek'])}</p>
  <a class="pill" style="align-self:flex-start" href="games/{gotw['slug']}/index.html">Read the recap →</a></div>
</section>
<section class="grid g2">
 <div class="sec"><h2 class="h2">Playoff odds this week</h2><p class="dim" style="margin:0">Chance of a top-6 seed, and how much it moved since Monday.</p>
  <div><p class="k" style="margin-top:6px">Risers</p>{"".join(mini(c) for c in risers)}</div>
  <div><p class="k" style="margin-top:6px">Fallers</p>{"".join(mini(c) for c in fallers)}</div>
  <a href="odds/index.html" style="font-weight:600">All 30 teams →</a></div>
 <div class="sec"><h2 class="h2">Deep dives</h2>
  {player_card(R, PLAYERS[0]) if PLAYERS else '<a href="players/luka-doncic/index.html" class="card pad" style="display:flex;flex-direction:column;gap:6px;background:radial-gradient(120% 140% at 100% 0%,#552583 0%,#1c0b32 75%);color:#fff;border:0"><span class="tag gold">Scouting report</span><b class="d" style="font-size:30px;margin-top:4px">Luka Dončić: 40 a night</b><span style="opacity:.85">Game log, hot and quiet nights, the step-back</span></a>'}
  {board_card(R, BOARDS[0]) if BOARDS else ''}
 </div>
</section>
<section class="card cta"><div><p class="k">Free · every Sunday</p><b class="d" style="font-size:clamp(30px,5vw,40px)">The Sunday Box</b><p style="margin:6px 0 0;color:#d5d6d9">The week's best game, playoff odds movers and one deep dive, in four minutes.</p></div>
<a class="pill hot" href="{NEWSLETTER}" target="_blank" rel="noopener">Subscribe free</a></section>
'''
page("index.html", "Box & Motion Hoops: every NBA game, explained", home)

# ---- teams index ----
R = "../"
blocks = ""
for conf in ("East", "West"):
    divs = {}
    for c in T:
        if T[c]["conf"] == conf: divs.setdefault(T[c]["div"], []).append(c)
    cols = ""
    for dv in sorted(divs):
        rows = "".join(f'''<div style="display:flex;align-items:center;justify-content:space-between;gap:10px;padding:10px 0;border-top:1px solid var(--line)">
<a href="{T[c]['slug']}/index.html" style="text-decoration:none;display:flex;align-items:center;gap:10px;flex:1 1 auto;min-width:0"><span style="width:14px;height:14px;border-radius:4px;background:{T[c]['c1']};flex:none"></span><span style="display:flex;flex-wrap:wrap;align-items:baseline;column-gap:8px;row-gap:0;min-width:0"><b>{E(T[c]['city'])} {E(T[c]['name'])}</b><span class="dim" style="white-space:nowrap">{rec(c)}</span></span></a><span style="flex:none">{star_btn(c)}</span></div>''' for c in sorted(divs[dv], key=lambda c: S["seeds"][c]))
        cols += f'<div class="card pad"><p class="k">{dv}</p>{rows}</div>'
    blocks += f'<section class="sec"><h2 class="h2">{conf}</h2><div class="grid g3">{cols}</div></section>'
page("teams/index.html", "Teams · Box & Motion Hoops", f'<div class="sec" style="gap:8px"><p class="k">All 30 teams · ★ to follow</p><h1 class="h1">Teams</h1><p class="dim" style="margin:0;font-size:18px">Follow your teams and they move to the top of the home page and Last Night. Saved on this device.</p></div>{blocks}', active="Teams")

# ---- team pages ----
LUKA_PPG = None
for c, t in T.items():
    R = "../../"
    nx = next_game(c)
    nxt = f'<div><span class="d" style="font-size:clamp(24px,3vw,30px)">{E(nx[0])}</span><br><span style="opacity:.8">Next: {nx[1]}</span></div>' if nx else f'<div><span class="d" style="font-size:30px">Schedule</span><br><a href="https://www.nba.com/{ {"76ers":"sixers","trail-blazers":"blazers"}.get(t["slug"], t["slug"]) }/schedule" target="_blank" rel="noopener" style="opacity:.8">Full schedule on NBA.com →</a></div>'
    band = f'''<section class="band" style="background:radial-gradient(90% 140% at 85% 0%,{t['c1']} 0%,{t['dark']} 80%)"><div class="w">
<div class="between"><div class="sec" style="gap:8px"><p class="k" style="color:rgba(255,255,255,.75)">{E(t['city'])} · {t['div']} division</p><h1 class="h1" style="font-size:clamp(56px,10vw,124px);color:{t['c2'] if t['c2']!='#FFFFFF' else '#fff'}">{E(t['name'])}</h1></div>
<button type="button" class="pill star" data-team="{c}" aria-pressed="false" style="background:#fff;border-color:#fff;color:#111214">★ <span class="lbl">Follow</span></button></div>
<div class="stats"><div><span class="d">{rec(c)}</span><br><span style="opacity:.8">{seed(c)}</span></div>
<a href="{R}odds/index.html"><span class="d">{O[c]['top6']}%</span><br><span style="opacity:.8">top-6 odds · {chg(O[c]['chg'])} this week →</span></a>
<div><span class="d">{O[c]['wins']}</span><br><span style="opacity:.8">projected wins</span></div>{nxt}</div></div></section>'''
    rows = ""
    for g in team_games(c):
        r, sc, opp = result_for(g, c)
        rows += f'''<a href="{R}games/{g['slug']}/index.html" class="card" style="display:flex;flex-wrap:wrap;gap:16px;align-items:center;padding:14px 18px">
<span style="flex:1 1 240px;display:flex;flex-direction:column;gap:2px"><span class="k">{WEEKDAY(g['date'])}</span>
<span class="row" style="gap:6px 14px;align-items:baseline"><b class="d" style="font-size:28px;color:{t['c1'] if r=='W' else '#5c5f66'}">{r} {sc}</b><b style="font-size:18px">{E(opp)}</b>{' <span class="dim">OT</span>' if g['ot'] else ''}</span>
<span class="dim">Record after: {g['rec'][c]}</span></span>
<span class="tag {'gold' if g['featured'] else ''}">{'Featured recap' if g['featured'] else 'Recap'}</span></a>'''
    moves = "".join(move_card(R, m) for m in MOVES if m["team"] == c)   # signature moves sit with the team's players
    if c == "LAL":
        players = moves + f'<a href="{R}players/luka-doncic/index.html" class="card pad" style="display:flex;flex-direction:column;gap:6px;min-height:200px;justify-content:flex-end;background:radial-gradient(120% 140% at 100% 0%,#552583 0%,#1c0b32 75%);color:#fff;border:0"><span class="tag gold">Scouting report</span><b class="d" style="font-size:30px">Luka Dončić</b><span style="opacity:.85">No. 77 · 40.1 points per game</span></a><div class="card pad empty" style="min-height:200px;display:flex;flex-direction:column;justify-content:flex-end"><b class="d" style="font-size:26px">Austin Reaves</b><span class="dim">Report coming</span></div><div class="card pad empty" style="min-height:200px;display:flex;flex-direction:column;justify-content:flex-end"><b class="d" style="font-size:26px">Walker Kessler</b><span class="dim">Report coming</span></div>'
    elif any(P["team"] == c for P in PLAYERS):
        players = moves + "".join(player_card(R, P) for P in PLAYERS if P["team"] == c)
    elif moves:
        players = moves
    else:
        players = f'<div class="card pad empty"><b class="d" style="font-size:26px">Scouting reports are coming</b><p class="dim" style="margin:6px 0 0">Every week we put the league\'s hottest player in motion. Follow the {E(t["name"])} to see theirs here first.</p></div>'
    if c in COACH_PAGES:
        cn, cp, cb = COACH_PAGES[c]
        sub = f'{E(cb["title"])}: {E(cb["dek"])}' if cb else "How the Lakers closed at Utah, on the board."
        coach = f'<a href="{R}{cp}" class="card pad" style="display:flex;flex-direction:column;gap:8px"><span class="tag">Coach\'s board</span><b class="d" style="font-size:40px">{E(cn)}</b><span class="dim" style="font-size:18px">{sub}</span><span style="font-weight:600">Open the board →</span></a>'
    else:
        coach = f'<div class="card pad empty"><b class="d" style="font-size:26px">Coach\'s board coming</b><p class="dim" style="margin:6px 0 0">When a team draws up a play worth seeing again, we put it on the board. Every action is backed by a cited source.</p></div>'
    body = f'''<div class="tabs" data-tabs="team"><button class="pill on" data-tab="games">Games</button><button class="pill" data-tab="players">Players</button><button class="pill" data-tab="coach">Coach</button></div>
<section class="sec" data-pane="team" data-value="games"><p class="k">Newest first · coverage starts Mon, Nov 2</p>{rows or '<p class="dim">No games yet this week.</p>'}</section>
<section class="grid g3 hidden" data-pane="team" data-value="players">{players}</section>
<section class="hidden" data-pane="team" data-value="coach">{coach}</section>'''
    page(f"teams/{t['slug']}/index.html", f"{t['city']} {t['name']} · Box & Motion Hoops", body, active="Teams",
         desc=f"{t['city']} {t['name']}: record, playoff odds, game recaps and scouting reports.", band=band)

ORD = ["first", "second", "third", "fourth"]
def got_away(lq, wq, ot):
    """One line, from the losing team's side, on where the game got away. Uses only the line score."""
    n = len(lq); m = [a - b for a, b in zip(lq, wq)]
    name = lambda i: f"the {ORD[i]} quarter" if i < 4 else ("overtime" if i == 4 else f"the {i - 3}{'nd' if i == 5 else 'rd' if i == 6 else 'th'} overtime")
    after3 = sum(m[:3])
    if ot:
        return f"Forced overtime, then lost {name(n - 1)} {lq[-1]}–{wq[-1]}."
    if after3 >= 0:
        lead = f"Led by {after3} after three quarters" if after3 > 0 else "Tied after three quarters"
        return f"{lead}, then lost the fourth {lq[3]}–{wq[3]}."
    k = min(range(n), key=lambda i: m[i])
    if k == 3 and after3 >= -5:
        return f"Within {-after3} after three quarters, then lost the fourth {lq[3]}–{wq[3]}."
    rl, rw = sum(lq[k + 1:]), sum(wq[k + 1:])
    if k < n - 1 and rl - rw >= 5:
        return f"Lost {name(k)} {lq[k]}–{wq[k]}, then won the rest of the game {rl}–{rw}."
    if all(x < 0 for x in m):
        return f"Trailed in every quarter; the biggest gap was {name(k)}, {lq[k]}–{wq[k]}."
    return f"Lost {name(k)} {lq[k]}–{wq[k]}, the stretch that decided it."

def next_game(c):
    for day, tm, a, h in S["upcoming"]:
        if c in (a, h): return f"{day}, {'vs.' if c == h else 'at'} {T[h if c == a else a]['name']}, {tm} ET"
    return ""

# ---- game pages ----
for g in GAMES:
    R = "../../"
    a, h, w, l = g["away"], g["home"], g["win"], g["lose"]
    city = T[h]["city"]
    ls = S["linescores"].get(g["key"])
    lsh = ""
    if ls:
        def tr(c, q, tot): return f'<tr><th>{E(T[c]["name"])}</th>' + "".join(f"<td>{x}</td>" for x in q) + f'<td><b>{tot}</b></td></tr>'
        ot_cols = "".join(f"<th>{'OT' if i == 4 else f'{i-3}OT'}</th>" for i in range(4, len(ls["away"])))
        lsh = f'<div class="scroll"><table class="lines"><tr class="k"><th></th><th>Q1</th><th>Q2</th><th>Q3</th><th>Q4</th>{ot_cols}<th>Final</th></tr>{tr(a, ls["away"], g["as_"])}{tr(h, ls["home"], g["hs"])}</table></div>'
    ws, lsc = max(g["as_"], g["hs"]), min(g["as_"], g["hs"])
    margin = ws - lsc
    auto = f"{T[w]['city']} beat {T[l]['city']} {ws}–{lsc}{' in overtime' if g['ot'] else ''}"
    auto += f", a {'one-point' if margin==1 else str(margin)+'-point'} {'road' if w==a else 'home'} win. The {T[w]['name']} move to {g['rec'][w]}; the {T[l]['name']} fall to {g['rec'][l]}."
    f = S["featured"].get(g["key"])
    feat = ""
    if f:
        la, lb = f["battle_labels"]
        three = "".join(f'<div class="card pad step"><span class="num-badge">{i+1}</span><b class="d" style="font-size:24px">{E(x)}</b><span class="dim">{E(y)}</span></div>' for i, (x, y) in enumerate(f["three"]))
        battle = "".join(f'<div class="kv"><span>{E(k)}</span>' + (f"<b>{v1}</b><span>{v2}</span>" if v1 > v2 else f"<span>{v1}</span><b>{v2}</b>") + "</div>" for k, v1, v2 in f["battle"])
        top = "".join(f'<div style="display:flex;justify-content:space-between;align-items:center;padding:10px 0;border-top:1px solid var(--line)"><span><b>{("<a href=" + chr(34) + R + "players/luka-doncic/index.html" + chr(34) + ">" + E(n) + "</a>") if n=="Luka Dončić" else E(n)}</b><br><span class="dim" style="font-size:14px">{tm} · {E(note)}</span></span><b class="d" style="font-size:34px;color:{T[tm]["c1"]}">{pts}</b></div>' for n, tm, note, pts in f["top"])
        feat = f'''<section class="sec"><h2 class="h2">Three things that decided it</h2><div class="grid g3">{three}</div></section>
<section class="grid g2"><div class="sec" style="gap:6px"><h2 class="h2">Where it was won</h2><div class="kv k" style="border:0"><span></span><span>{la}</span><span>{lb}</span></div>{battle}</div>
<div class="sec" style="gap:6px"><h2 class="h2">Top performers</h2>{top}</div></section>'''
    lede = f'<p style="margin:0;font-size:22px;max-width:38em"><b>{E(f["headline"])}.</b> {E(f["dek"])}</p>' if f else f'<p style="margin:0;font-size:20px;max-width:38em">{E(auto)}</p>'
    def team_link(c): return f'<a href="{R}teams/{T[c]["slug"]}/index.html">{E(T[c]["name"])}</a>'
    meant = "".join(f'<div style="flex:1 1 240px"><b class="d" style="font-size:28px">{E(T[c]["name"])}: {O[c]["top6"]}%</b><p style="margin:4px 0 0;color:#d5d6d9">top-6 odds now · {seed(c)} at {rec(c)}</p></div>' for c in (w, l))
    crumbs = f'<nav aria-label="Breadcrumb" class="crumbs"><a href="{R}last-night/index.html">Games</a><span>/</span>{team_link(a)}<span>at</span>{team_link(h)}</nav>'
    kicker = f'<p class="k">Final{" · OT" if g["ot"] else ""} · {WEEKDAY(g["date"])} · {E(city)}</p>'
    names = f'<span style="color:{"#111214" if w==a else "#8a8c92"}">{E(T[a]["name"])} {g["as_"]}</span><span style="color:{"#111214" if w==h else "#8a8c92"}">{E(T[h]["name"])} {g["hs"]}</span>'
    v = g["video"]
    # three actions under every recap: watch the Short, subscribe on YouTube, subscribe to the newsletter
    yt_btn = watch_links(g)
    if g["reel"]:
        # our drawn recap plays right on the page (no YouTube frame); the YouTube Short is one tap away
        hero = f'''<span class="tag gold" style="align-self:flex-start;margin-bottom:-28px">▶ Our recap video · 66 seconds</span>
<section style="display:flex;flex-wrap:wrap;gap:28px;align-items:flex-start">
<div style="flex:0 1 360px;width:100%;max-width:360px;display:flex;flex-direction:column;gap:12px">
<div style="aspect-ratio:9/14.4;border-radius:18px;overflow:hidden;background:#111214;box-shadow:0 10px 30px rgba(17,18,20,.18)">
<iframe src="{R}reels/{g['key']}/index.html?embed=1" title="Box &amp; Motion recap: {E(T[a]['name'])} at {E(T[h]['name'])}" loading="lazy" style="width:100%;height:100%;border:0" allow="autoplay"></iframe></div>
{yt_btn}</div>
<div class="sec" style="flex:1 1 320px;gap:16px">{kicker}
<h1 class="h1" style="display:flex;flex-wrap:wrap;gap:4px 24px;font-size:clamp(40px,6vw,72px)">{names}</h1>
{lede}{lsh}</div></section>'''
    elif v:
        # only the YouTube Short exists: embed it
        hero = f'''<span class="tag gold" style="align-self:flex-start;margin-bottom:-28px">▶ Our recap video · 66 seconds</span>
<section style="display:flex;flex-wrap:wrap;gap:28px;align-items:flex-start">
<div style="flex:0 1 360px;width:100%;max-width:360px;aspect-ratio:9/16;border-radius:18px;overflow:hidden;background:#111214;box-shadow:0 10px 30px rgba(17,18,20,.18)">
<iframe src="https://www.youtube.com/embed/{v}" title="Box &amp; Motion recap: {E(T[a]['name'])} at {E(T[h]['name'])}" style="width:100%;height:100%;border:0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe></div>
<div class="sec" style="flex:1 1 320px;gap:16px">{kicker}
<h1 class="h1" style="display:flex;flex-wrap:wrap;gap:4px 24px;font-size:clamp(40px,6vw,72px)">{names}</h1>
{lede}{lsh}{yt_btn}</div></section>'''
    else:
        hero = f'''<section class="sec" style="gap:18px">{kicker}
<h1 class="h1" style="display:flex;flex-wrap:wrap;gap:4px 28px;font-size:clamp(48px,8vw,100px)">{names}</h1>
{lede}{lsh}{yt_btn}</section>'''
    # the other side: where it got away for the losing team, their top performers, and their next game
    lose_html = ""
    if ls:
        lq, wq = (ls["away"], ls["home"]) if l == a else (ls["home"], ls["away"])
        ltop = ((f or {}).get("loser") or {}).get("top") or [x for x in (f or {}).get("top", []) if x[1] == l]
        rows = "".join(f'<div style="display:flex;justify-content:space-between;align-items:center;gap:12px;padding:10px 0;border-top:1px solid var(--line)"><span><b>{E(n)}</b><br><span class="dim" style="font-size:14px">{E(note)}</span></span><b class="d" style="font-size:34px;color:{T[l]["c1"]}">{pts}</b></div>' for n, tm, note, pts in ltop[:3])
        nx = next_game(l)
        lose_html = f'''<section class="card pad" style="display:flex;flex-direction:column;gap:10px"><p class="k">From the {E(T[l]['name'])}' side</p>
<p style="margin:0;font-size:20px;font-weight:600;max-width:36em">{E(got_away(lq, wq, g['ot']))}</p>
{('<div>' + rows + '</div>') if rows else ''}
<span class="dim">{E(T[l]['name'])} fall to {g['rec'][l]}.{(' Next: ' + E(nx) + '.') if nx else ''} <a href="{R}teams/{T[l]['slug']}/index.html">{E(T[l]['name'])} page →</a></span></section>'''
    feat += lose_html
    if f and not v and not g["reel"]:
        feat += video_block(None)
    body = f'''{crumbs}
{hero}
{feat}
<section class="card cta"><div style="display:flex;flex-wrap:wrap;gap:20px;flex:1 1 400px"><div style="flex-basis:100%"><p class="k">What it meant</p></div>{meant}</div>
<a class="pill hot" href="{R}odds/index.html">All playoff odds</a></section>'''
    page(f"games/{g['slug']}/index.html", f"{T[a]['name']} {g['as_']}, {T[h]['name']} {g['hs']} · Box & Motion Hoops", body, active="Last Night",
         desc=(f["dek"] if f else auto))

# ---- calendar archive (below the current week on Last Night, and on every date page) ----
def calendar(R, sel=None):
    counts = {}
    for g in GAMES: counts[g["date"]] = counts.get(g["date"], 0) + 1
    months = sorted({d[:7] for d in counts}, reverse=True)
    out = []
    for ym in months:
        y, m = map(int, ym.split("-"))
        first = datetime.date(y, m, 1)
        nxt = datetime.date(y + (m == 12), m % 12 + 1, 1)
        cells = ['<span></span>'] * first.weekday()
        for day in range(1, (nxt - first).days + 1):
            d = f"{ym}-{day:02d}"
            n = counts.get(d)
            cls = ' class="on"' if d == sel else ''
            cells.append(f'<a{cls} href="{R}days/{d}/index.html" title="{WEEKDAY(d)}: {n} game{"s" if n != 1 else ""}">{day}<i></i></a>' if n else f'<span class="off">{day}</span>')
        out.append(f'<div class="card pad cal"><p class="k">{first.strftime("%B %Y")}</p><div class="cal-g">{"".join(f"<b>{w}</b>" for w in "MTWTFSS")}{"".join(cells)}</div></div>')
    return f'<section class="sec" id="archive"><div class="sec" style="gap:6px"><p class="k">Archive</p><h2 class="h2">Every game day</h2><p class="dim" style="margin:0">Pick a date to see that day\'s results.</p></div><div class="cal-row">{"".join(out)}</div></section>'

# ---- last night ----
R = "../"
LN_CARDS = games_block(LAST, R)
earlier = sorted({g["date"] for g in GAMES if g["date"] != LAST_DATE and g["date"] >= WEEK_START}, reverse=True)
ear = "".join(f'<section class="sec"><p class="k">{WEEKDAY(d)}</p>{games_block([g for g in GAMES if g["date"]==d], R, images="none")}</section>' for d in earlier)
body = f'''<div class="between"><div class="sec" style="gap:8px"><p class="k">{WEEKDAY(LAST_DATE)} · {len(LAST)} games</p><h1 class="h1">Last night</h1></div>
<div class="tabs"><button class="pill" data-mode="mine">Your teams</button><button class="pill" data-mode="all">All games</button><a class="pill" href="#archive">📅 Archive</a></div></div>
<section class="sec">{LN_CARDS}<p class="dim none-note hidden" style="margin:0">None of your teams played last night. <button class="pill sm" data-mode="all">Show all games</button></p></section>
{'<h2 class="h2">Earlier this week</h2>' + ear if ear else ''}
{calendar(R)}'''
page("last-night/index.html", "Last night · Box & Motion Hoops", body, active="Last Night")

# ---- archive: one page per game date, reached from the calendar ----
DATES = sorted({g["date"] for g in GAMES})
for i, d in enumerate(DATES):
    R = "../../"
    prev_l = f'<a class="pill sm" href="{R}days/{DATES[i-1]}/index.html">← {WEEKDAY(DATES[i-1])}</a>' if i > 0 else ''
    next_l = f'<a class="pill sm" href="{R}days/{DATES[i+1]}/index.html">{WEEKDAY(DATES[i+1])} →</a>' if i + 1 < len(DATES) else ''
    day_games = [g for g in GAMES if g["date"] == d]
    body = f'''<nav aria-label="Breadcrumb" class="crumbs"><a href="{R}last-night/index.html">Games</a><span>/</span><span>{WEEKDAY(d)}</span></nav>
<div class="between"><div class="sec" style="gap:8px"><p class="k">{len(day_games)} game{'s' if len(day_games) != 1 else ''}</p><h1 class="h1">{WEEKDAY(d)}</h1></div>
<div class="row">{prev_l}{next_l}</div></div>
<section class="sec">{games_block(day_games, R, show_mine=False).replace(" data-games", "")}</section>
{calendar(R, d)}'''
    page(f"days/{d}/index.html", f"NBA games, {WEEKDAY(d)} · Box & Motion Hoops", body, active="Last Night",
         desc=f"Every NBA result from {WEEKDAY(d)}, with recaps in motion.")

# ---- odds ----
R = "../"
def otable(conf, hidden=False):
    rows = "".join(f'''<tr data-team="{c}"><td><a href="{R}teams/{T[c]['slug']}/index.html" style="text-decoration:none;color:inherit">{E(T[c]['name'])}</a></td><td class="dim">{rec(c)}</td>
<td style="width:40%"><div class="bar"><span style="width:{O[c]['top6']}%"></span></div></td><td class="num"><b class="d" style="font-size:22px">{O[c]['top6']}%</b></td>
<td class="num hide-sm">{O[c]['top10']}%</td><td class="num hide-sm">{O[c]['wins']}</td><td class="num {chgcls(O[c]['chg'])}">{chg(O[c]['chg'])}</td></tr>''' for c in sorted([c for c in T if T[c]["conf"] == conf], key=lambda c: (-O[c]["top6"], -O[c]["top10"])))
    return f'<div class="card{" hidden" if hidden else ""}" style="padding:6px 16px" data-pane="conf" data-value="{conf}"><div class="scroll"><table class="otable"><tr><th>Team</th><th>Record</th><th>Top-6 seed</th><th></th><th class="num hide-sm">Play-in+</th><th class="num hide-sm">Proj. wins</th><th class="num">This week</th></tr>{rows}</table></div></div>'
west, east = otable("West"), otable("East", True)
body = f'''<div class="sec" style="gap:8px"><p class="k">All 30 teams · updated {S['updated']}</p><h1 class="h1">Playoff odds</h1>
<p class="dim" style="margin:0;font-size:18px;max-width:46em">Chance of a top-6 seed (a guaranteed playoff spot) and of the play-in or better. "This week" is the change since Monday morning.</p></div>
<div class="tabs" data-tabs="conf"><button class="pill on" data-tab="West">West</button><button class="pill" data-tab="East">East</button></div>
{west}{east}
<section class="card pad"><b>How the odds work</b><p class="dim" style="margin:6px 0 0">Each team starts from a projected win total and is updated with every result (the projection counts like 30 games, so early records move it but don't take over). We then simulate the rest of the 82-game season 20,000 times, with some uncertainty in every team's strength, and count how often each team finishes top six and top ten in its conference. This is model v0: it uses records only, not injuries, schedule strength or point differential.</p></section>'''
page("odds/index.html", "Playoff odds · Box & Motion Hoops", body, active="Playoff Odds")

# ---- deep dives ----
R = "../"
# every deep dive, newest first (ties keep this order)
DD_ITEMS = ([("2026-11-07", f'''<a href="{R}players/luka-doncic/index.html" class="card pad" style="min-height:260px;display:flex;flex-direction:column;justify-content:flex-end;gap:6px;background:radial-gradient(120% 140% at 100% 0%,#552583 0%,#1c0b32 75%);color:#fff;border:0"><span class="tag gold">Scouting report · Lakers</span><b class="d" style="font-size:40px">Luka Dončić</b><span style="opacity:.85">40.1 points a game, the hot and quiet nights, and the step-back</span></a>'''), ("2026-11-07", f'''<a href="{R}coaches/jj-redick/index.html" class="card pad" style="min-height:260px;display:flex;flex-direction:column;justify-content:flex-end;gap:6px"><span class="tag">Coach's whiteboard · Lakers</span><b class="d" style="font-size:40px">JJ Redick</b><span class="dim">How the Lakers closed out the Utah comeback</span></a>''')]
            + [(b["published"], board_card(R, b, big=True)) for b in BOARDS]
            + [(m["published"], move_card(R, m, big=True)) for m in MOVES]
            + [(x["published"], xo_card(R, x, big=True)) for x in XO]
            + [(P["published"], player_card(R, P, big=True)) for P in PLAYERS]
            + [(x["published"], trend_card(R, x, big=True)) for x in TRENDS])
DD_CARDS = "\n".join(html for _, html in sorted(DD_ITEMS, key=lambda x: x[0], reverse=True))
body = f'''<div class="sec" style="gap:8px"><p class="k">New every week</p><h1 class="h1">Deep dives</h1><p class="dim" style="margin:0;font-size:18px;max-width:44em">Scouting reports on the league's hottest players, coach's boards when a team draws up a play worth seeing again, stars' signature moves, and X's and O's that teach the game. All in motion.</p></div>
<section class="grid g2 dd-grid">{DD_CARDS}</section>'''
page("deep-dives/index.html", "Deep dives · Box & Motion Hoops", body, active="Deep Dives")

# ---- player: Luka ----
R = "../../"
LOG = [("Oct 21","vs. Warriors","W 127–105",28,8,7,"7–18","5–12",6,None),("Oct 23","vs. Clippers","W 125–117",23,6,7,"8–21","2–8",11,None),
       ("Oct 25","at Jazz","W 132–123",52,8,10,"17–30","8–18",4,None),("Oct 27","vs. Blazers","L 129–136",41,5,9,"12–22","6–15",2,None),
       ("Oct 28","at Clippers","W 103–87",None,None,None,None,None,None,"DNP · back tightness"),("Oct 30","at Warriors","L 95–112",37,None,None,None,None,None,None),
       ("Nov 1","vs. Raptors","W 131–125",45,15,6,"12–23","8–12",None,None),("Nov 2","vs. Heat","W 138–117",42,7,13,"14–24","6–15",2,None),
       ("Nov 4","at Kings","W 116–103",40,9,7,"11–23","6–13",6,None),("Nov 6","vs. Blazers","W 124–118",53,5,5,"17–33","5–15",3,"2026-11-06-trail-blazers-at-lakers")]
pts = [x[3] for x in LOG if x[3] is not None]; avg = sum(pts) / len(pts)
def flag(p):
    if p is None: return '<span class="tag ghost">DNP</span>'
    if p - avg >= 10: return '<span class="tag hot">Hot night</span>'
    if avg - p >= 10: return '<span class="tag ghost">Quiet night</span>'
    return ""
dash = lambda v: "—" if v is None else v
logrows = "".join(f'<tr><td>{d}</td><td>{o}</td><td>{r}</td><td class="num"><b>{"DNP" if p is None else p}</b></td><td class="num">{dash(rb)}</td><td class="num">{dash(a)}</td><td class="num">{dash(fg)}</td><td class="num">{dash(tp)}</td><td class="num">{dash(to)}</td><td>{flag(p)}</td></tr>' for d,o,r,p,rb,a,fg,tp,to,n in reversed(LOG))
hot = [x for x in LOG if x[3] is not None and x[3]-avg >= 10]
HOTS = ", ".join(str(x[3]) + " " + x[1] for x in hot)
body = f'''<nav aria-label="Breadcrumb" class="crumbs"><a href="{R}deep-dives/index.html">Deep dives</a><span>/</span><a href="{R}teams/lakers/index.html">Lakers</a><span>/</span><span>Luka Dončić</span></nav>
<section style="display:flex;flex-wrap:wrap;gap:32px;align-items:flex-end"><div class="sec" style="flex:999 1 480px;gap:12px"><p class="k">Scouting report · updated {S['updated_short']}</p>
<h1 class="h1" style="font-size:clamp(64px,10vw,120px)">Luka<br>Dončić</h1>
<p style="margin:0;font-size:20px;max-width:34em">The league's leading scorer. He makes defenses choose between the drive and the step-back, then punishes whichever they pick. He has scored 40 or more in six of his last seven games.</p>
<p class="dim" style="margin:0">No. 77 · Lakers · 6-8 · 9th NBA season</p></div>
<div style="flex:1 1 280px;display:grid;grid-template-columns:1fr 1fr;gap:12px">
<div class="card pad"><span class="d" style="font-size:44px;color:#552583">{avg:.1f}</span><br><span class="dim">points per game</span></div>
<div class="card pad"><span class="d" style="font-size:44px">{len(pts)}</span><br><span class="dim">games played</span></div>
<div class="card pad"><span class="d" style="font-size:44px">53</span><br><span class="dim">season high</span></div>
<div class="card pad"><span class="d" style="font-size:44px">{rec('LAL')}</span><br><span class="dim">Lakers record</span></div></div></section>
<section class="sec"><div class="sec" style="gap:6px"><p class="k">Signature move</p><h2 class="h2">The step-back three</h2>
<p style="margin:0;max-width:44em">He sells the drive with a hard jab, crosses the ball back between his legs to his left as he hops back off both feet, and rises before the defender recovers. At 6-8 he releases over most guards, so a late contest rarely bothers the shot.</p></div>
{anim_frame(R, "luka-stepback.html", "Animated illustration of Luka Dončić's step-back three", "reels/soundtrack.mp3")}
<div class="row"><a class="pill on" href="https://youtube.com/shorts/5FgwWO0aF8s" target="_blank" rel="noopener">▶ Watch the Short</a></div></section>
<section class="sec"><h2 class="h2">Game log</h2>
<div class="card" style="padding:6px 16px"><div class="scroll"><table class="otable" style="min-width:720px"><tr><th>Date</th><th>Game</th><th>Result</th><th class="num">Pts</th><th class="num">Reb</th><th class="num">Ast</th><th class="num">FG</th><th class="num">3PT</th><th class="num">TO</th><th>Flag</th></tr>{logrows}</table></div></div>
<p class="dim" style="margin:0;font-size:14px">Flags are automatic: any game 10 or more points from his season average ({avg:.1f}). Hot nights so far: {HOTS}. A dash means the stat isn't in our feed yet.</p></section>'''
page("players/luka-doncic/index.html", "Luka Dončić scouting report · Box & Motion Hoops", body, active="Deep Dives",
     desc=f"Luka Dončić: {avg:.1f} points per game, game log, hot and quiet nights, and the step-back.")

# ---- player reports from data/players/<slug>.json (the weekly hot-player report) ----
for P in PLAYERS:
    c = P["team"]; t = T[c]
    stats = "".join(f'<div class="card pad"><span class="d" style="font-size:44px{";color:" + t["c1"] if i == 0 else ""}">{E(v)}</span><br><span class="dim">{E(l)}</span></div>' for i, (v, l) in enumerate(P["stats"]))
    logrows = "".join("<tr>" + "".join(f'<td{" class=num" if 3 <= j else ""}>{"<b>" + E(str(v)) + "</b>" if j == 3 else E("—" if v is None else str(v))}</td>' for j, v in enumerate(r)) + "</tr>" for r in P["log"])
    steps = "".join(f'<li><b>{E(a)}.</b> {E(b2)}</li>' for a, b2 in P["move"]["steps"])
    srcs = "".join(f'<li><a href="{E(u)}" target="_blank" rel="noopener">{E(l)}</a></li>' for l, u in P["sources"])
    body = f'''<nav aria-label="Breadcrumb" class="crumbs"><a href="{R}deep-dives/index.html">Deep dives</a><span>/</span><a href="{R}teams/{t['slug']}/index.html">{E(t['name'])}</a><span>/</span><span>{E(P['name'])}</span></nav>
<section style="display:flex;flex-wrap:wrap;gap:32px;align-items:flex-end"><div class="sec" style="flex:999 1 480px;gap:12px"><p class="k">Scouting report · {E(P['week'])}</p>
<h1 class="h1" style="font-size:clamp(56px,9vw,112px)">{E(P['name'])}</h1>
<p style="margin:0;font-size:20px;max-width:34em">{E(P['lede'])}</p>
<p class="dim" style="margin:0">{E(P['bio'])}</p></div>
<div style="flex:1 1 280px;display:grid;grid-template-columns:1fr 1fr;gap:12px">{stats}</div></section>
<section class="sec"><div class="sec" style="gap:6px"><p class="k">Signature move</p><h2 class="h2">{E(P['move']['title'])}</h2>
<p style="margin:0;max-width:44em">{E(P['move']['text'])}</p></div>
{anim_frame(R, P['move']['anim'], P['name'] + ': ' + P['move']['title'], "reels/soundtrack.mp3")}
<ol style="margin:0;padding-left:22px;display:flex;flex-direction:column;gap:6px;max-width:46em">{steps}</ol>
{f'<div class="row"><a class="pill on" href="https://youtube.com/shorts/{P["move"]["youtube"]}" target="_blank" rel="noopener">▶ Watch the Short</a></div>' if P["move"].get("youtube") else ""}</section>
<section class="sec"><h2 class="h2">His week</h2>
<div class="card" style="padding:6px 16px"><div class="scroll"><table class="otable" style="min-width:640px"><tr><th>Date</th><th>Game</th><th>Result</th><th class="num">Pts</th><th class="num">Reb</th><th class="num">Ast</th><th class="num">FG</th><th class="num">3PT</th></tr>{logrows}</table></div></div></section>
<section class="card pad"><b>Sources</b><ul style="margin:8px 0 0;padding-left:20px;display:flex;flex-direction:column;gap:4px">{srcs}</ul></section>'''
    page(f"players/{P['slug']}/index.html", f"{P['name']} scouting report · Box & Motion Hoops", body, active="Deep Dives", desc=P["lede"])

# ---- signature moves ----
for m in MOVES:
    t = T[m["team"]]
    steps = "".join(f'<li><b>{E(a)}.</b> {E(b2)}</li>' for a, b2 in m["steps"])
    yt = f'<a class="pill cta-btn" style="background:#FF0033;border-color:#FF0033;color:#fff" href="https://youtube.com/shorts/{m["youtube"]}" target="_blank" rel="noopener">▶ Watch the Short</a>' if m.get("youtube") else ""
    body = f'''<nav aria-label="Breadcrumb" class="crumbs"><a href="{R}deep-dives/index.html">Deep dives</a><span>/</span><a href="{R}teams/{t['slug']}/index.html">{E(t['name'])}</a><span>/</span><span>{E(m['player'])}</span></nav>
<section class="sec" style="gap:12px"><p class="k">Signature move · {E(t['city'])} {E(t['name'])}{' · No. ' + E(m['number']) if m['number'] else ''}</p>
<h1 class="h1" style="font-size:clamp(56px,9vw,112px)">{E(m['title'])}</h1>
<p style="margin:0;font-size:20px;max-width:34em">{E(m['dek'])}</p></section>
<section class="sec">{anim_frame(R, m['anim'], m['player'] + ': ' + m['title'], "reels/soundtrack.mp3")}
<ol style="margin:0;padding-left:22px;display:flex;flex-direction:column;gap:6px;max-width:46em">{steps}</ol>
<div class="row" style="gap:8px">{yt}<a class="pill" href="{R}teams/{t['slug']}/index.html">{E(t['name'])} page →</a></div></section>'''
    page(f"moves/{m['slug']}/index.html", f"{m['player']}: {m['title']} · Box & Motion Hoops", body, active="Deep Dives", desc=m["dek"])

# ---- X's and O's explainers ----
for x in XO:
    yt = f'<a class="pill cta-btn" style="background:#FF0033;border-color:#FF0033;color:#fff" href="https://youtube.com/shorts/{x["youtube"]}" target="_blank" rel="noopener">▶ Watch the Short</a>' if x.get("youtube") else ""
    body = f'''<nav aria-label="Breadcrumb" class="crumbs"><a href="{R}deep-dives/index.html">Deep dives</a><span>/</span><span>X's and O's</span></nav>
<section class="sec" style="gap:12px"><p class="k">X's and O's · learn the game</p>
<h1 class="h1" style="font-size:clamp(48px,8vw,96px)">{E(x['title'])}</h1>
<p style="margin:0;font-size:20px;max-width:34em">{E(x['sub'])}.</p></section>
<section class="sec">{anim_frame(R, x['anim'], x['title'])}
<div class="row" style="gap:8px">{yt}<a class="pill" href="{R}deep-dives/index.html">More deep dives →</a></div></section>'''
    page(f"xo/{x['slug']}/index.html", f"{x['title']} · Box & Motion Hoops", body, active="Deep Dives", desc=f"{x['title']} {x['sub']}, explained in motion.")

# ---- trend boards ----
for x in TRENDS:
    t = T[x["team"]]
    yt = f'<a class="pill cta-btn" style="background:#FF0033;border-color:#FF0033;color:#fff" href="https://youtube.com/shorts/{x["youtube"]}" target="_blank" rel="noopener">▶ Watch the Short</a>' if x.get("youtube") else ""
    body = f'''<nav aria-label="Breadcrumb" class="crumbs"><a href="{R}deep-dives/index.html">Deep dives</a><span>/</span><a href="{R}teams/{t['slug']}/index.html">{E(t['name'])}</a><span>/</span><span>Trend board</span></nav>
<section class="sec" style="gap:12px"><p class="k">Trend board · good, lucky or in trouble?</p>
<h1 class="h1" style="font-size:clamp(44px,7vw,88px)">{E(x['title'])}</h1>
<p style="margin:0;font-size:20px;max-width:34em">{E(x['dek'])}</p></section>
<section class="sec" style="max-width:560px">{anim_frame(R, x['anim'], x['title'], "reels/soundtrack.mp3")}
<div class="row" style="gap:8px">{yt}<a class="pill" href="{R}teams/{t['slug']}/index.html">{E(t['name'])} page →</a><a class="pill" href="{R}deep-dives/index.html">More deep dives →</a></div></section>'''
    page(f"trends/{x['slug']}/index.html", f"{x['title']} · Box & Motion Hoops", body, active="Deep Dives", desc=x["dek"])

# ---- coach: Redick ----
body = f'''<nav aria-label="Breadcrumb" class="crumbs"><a href="{R}deep-dives/index.html">Deep dives</a><span>/</span><a href="{R}teams/lakers/index.html">Lakers</a><span>/</span><span>JJ Redick</span></nav>
<section class="sec" style="gap:12px"><p class="k">Coach's whiteboard · updated every few weeks</p><h1 class="h1" style="font-size:clamp(64px,10vw,120px)">JJ Redick</h1>
<p class="dim" style="margin:0;font-size:18px">Lakers head coach since 2024. The Lakers are {rec('LAL')}, {seed('LAL')}.</p></section>
<section class="sec"><div class="sec" style="gap:6px"><p class="k">From the games · Lakers at Jazz, Oct 25</p><h2 class="h2">How they closed at Utah</h2>
<p style="margin:0;max-width:44em;font-size:18px">Down three with 4:17 left, the Lakers closed on a 19–7 run to win 132–123, with Luka Dončić scoring 52. Every possession of the finish, on the board.</p></div>
{anim_frame(R, "lakers-utah-close.html", "Whiteboard breakdown of the Lakers' last 4:17 at Utah", "audio/film-room.mp3")}</section>
<section class="sec"><div class="sec" style="gap:6px"><h2 class="h2">What he likes to run</h2><p class="dim" style="margin:0;max-width:46em">Each set gets drawn on the board and backed by a source: his own interviews or film from this season's games. Nothing goes up without one.</p></div>
<div class="grid g3"><div class="card pad empty"><span class="tag ghost">Go-to set</span><p class="dim" style="margin:10px 0 0">Being drawn</p></div><div class="card pad empty"><span class="tag ghost">After a timeout</span><p class="dim" style="margin:10px 0 0">Being drawn</p></div><div class="card pad empty"><span class="tag ghost">Defense</span><p class="dim" style="margin:10px 0 0">Being drawn</p></div></div></section>'''
page("coaches/jj-redick/index.html", "JJ Redick coach's whiteboard · Box & Motion Hoops", body, active="Deep Dives")

# ---- coach's boards (one page per coach, newest board first) ----
R = "../../"
by_coach = {}
for b in BOARDS: by_coach.setdefault(b["coach_slug"], []).append(b)
for cslug, bl in by_coach.items():
    b = bl[0]; c = b["team"]; t = T[c]
    g = next((x for x in GAMES if x["slug"] == b["game"]), None)
    steps = "".join(f'<li><b>{E(x["title"])}.</b> {E(x["text"])}</li>' for x in b["beats"])
    srcs = "".join(f'<li><a href="{E(u)}" target="_blank" rel="noopener">{E(l)}</a></li>' for l, u in b["sources"])
    more = "".join(f'<li>{E(x["title"])} ({E(x["situation"])})</li>' for x in bl[1:])
    recap = f'<a class="pill" href="{R}games/{g["slug"]}/index.html">Game recap →</a>' if g else ""
    if b.get("youtube"): recap = f'<a class="pill on" href="https://youtube.com/shorts/{b["youtube"]}" target="_blank" rel="noopener">▶ Watch the Short</a>' + recap
    body = f'''<nav aria-label="Breadcrumb" class="crumbs"><a href="{R}deep-dives/index.html">Deep dives</a><span>/</span><a href="{R}teams/{t['slug']}/index.html">{E(t['name'])}</a><span>/</span><span>{E(b['coach'])}</span></nav>
<section class="sec" style="gap:12px"><p class="k">Coach's board · {E(t['city'])} {E(t['name'])}</p><h1 class="h1" style="font-size:clamp(56px,9vw,112px)">{E(b['coach'])}</h1>
<p class="dim" style="margin:0;font-size:18px">{E(t['name'])} head coach since {E(b['since'])}. The {E(t['name'])} are {rec(c)}, {seed(c)}.</p></section>
<section class="sec"><div class="sec" style="gap:6px"><p class="k">{E(b['situation'])}</p><h2 class="h2">{E(b['title'])}</h2>
<p style="margin:0;max-width:44em;font-size:18px">{E(b['dek'])}</p></div>
{anim_frame(R, b["anim"], b["coach"] + ": " + b["title"])}
<ol style="margin:0;padding-left:22px;display:flex;flex-direction:column;gap:8px;max-width:46em;font-size:17px">{steps}</ol>
<div class="row" style="gap:10px">{recap}</div></section>
<section class="card pad"><b>Sources</b><p class="dim" style="margin:4px 0 8px">Every action on the board comes from these game stories. Where they don't say where a player stood, the spot is our illustration.</p><ul style="margin:0;padding-left:20px;display:flex;flex-direction:column;gap:4px">{srcs}</ul></section>
{f'<section class="sec"><h2 class="h2">Earlier boards</h2><ul>{more}</ul></section>' if more else ''}'''
    page(f"coaches/{cslug}/index.html", f"{b['coach']}: {b['title']} · Box & Motion Hoops", body, active="Deep Dives",
         desc=f"{b['coach']}'s {b['title'].lower()}: {b['dek']}")

# ---- newsletter ----
R = "../"
body = f'''<section style="display:flex;flex-wrap:wrap;gap:32px;align-items:center"><div class="sec" style="flex:1 1 420px;gap:12px"><p class="k">Free · every Sunday</p><h1 class="h1">The Sunday Box</h1>
<p style="margin:0;font-size:20px;max-width:32em">The week in four minutes: the game of the week, the playoff odds movers, one deep dive and the games to watch.</p>
<div class="row"><a class="pill hot" href="{NEWSLETTER}" target="_blank" rel="noopener">Subscribe free</a><span class="dim">Unsubscribe anytime.</span></div></div>
<div class="card pad" style="flex:1 1 320px;display:flex;flex-direction:column;gap:10px"><p class="k">This week's issue</p><b class="d" style="font-size:30px">Two 50-point nights</b>
<ol style="margin:0;padding-left:20px;display:flex;flex-direction:column;gap:6px"><li>The week in one line</li><li>Game of the week: Spurs 112, Mavericks 111</li><li>Playoff race movers</li><li>Deep dive: Luka Dončić</li><li>Games to watch this week</li></ol></div></section>'''
page("newsletter/index.html", "The Sunday Box newsletter · Box & Motion Hoops", body, active="Newsletter")

# ---- about + 404 ----
body = f'''<section class="sec" style="gap:14px;max-width:46em"><p class="k">About Box &amp; Motion</p>
<h1 class="h1" style="font-size:clamp(48px,8vw,96px)">We want more out of our box scores.</h1>
<p style="font-size:20px;margin:0">A box score tells you who scored. It doesn’t tell you how the game was won: the run that flipped it, the matchup a coach kept going back to, the play drawn up out of a timeout.</p></section>
<section class="grid g2">
<div class="card pad" style="display:flex;flex-direction:column;gap:8px"><p class="k">Who we are</p><b class="d" style="font-size:28px">Fans with a day job in data</b>
<p style="margin:0">Our team has a background in analytics and AI enablement. We love basketball, and we don’t have time to watch every game anymore. We still want to know what actually happened.</p></div>
<div class="card pad" style="display:flex;flex-direction:column;gap:8px"><p class="k">What we make</p><b class="d" style="font-size:28px">The story of the game, in motion</b>
<p style="margin:0">Every game, told through the numbers and simple X’s and O’s: where it was won, who carried it, and the play that decided it, drawn so you can see it in about a minute.</p></div></section>
<section class="sec" style="gap:10px"><h2 class="h2">What’s here</h2>
<div class="grid g2">
<a class="card pad" href="{R}last-night/index.html" style="display:flex;flex-direction:column;gap:4px;text-decoration:none"><b>Recaps for every game</b><span class="dim">Each night’s games, in motion, with the box score behind them.</span></a>
<a class="card pad" href="{R}odds/index.html" style="display:flex;flex-direction:column;gap:4px;text-decoration:none"><b>Playoff odds</b><span class="dim">Our own model, updated every morning, with who moved this week.</span></a>
<a class="card pad" href="{R}deep-dives/index.html" style="display:flex;flex-direction:column;gap:4px;text-decoration:none"><b>Deep dives</b><span class="dim">Scouting reports, coach’s boards and stars’ signature moves.</span></a>
<a class="card pad" href="{R}newsletter/index.html" style="display:flex;flex-direction:column;gap:4px;text-decoration:none"><b>The Sunday Box</b><span class="dim">The week in one email, every Sunday morning. Free.</span></a></div></section>
<section class="sec" style="gap:10px;max-width:46em"><h2 class="h2">How we make it</h2>
<p style="margin:0">Scores and records come from league stats, and every number in a recap is checked against the box score or a named game story. The plays are original illustrations drawn from written accounts, not traced from footage and not to scale. We use AI tools to help draw and publish it all, and we skip anything we can’t verify rather than guess.</p>
<p class="dim" style="margin:0">Box &amp; Motion is unofficial fan coverage and is not affiliated with the NBA or any team. Team names are used to identify teams. We link to official video uploads and never re-upload them.</p>
<p style="margin:0">Contact: <a href="mailto:boxandmotionhoops@gmail.com">boxandmotionhoops@gmail.com</a></p></section>'''
page("about/index.html", "About · Box & Motion Hoops", body, active="About", desc="We want more out of our box scores: every NBA game, told through the numbers and simple X’s and O’s, in motion.")
page("404.html", "Not found · Box & Motion Hoops", '<div class="sec"><h1 class="h1">Air ball.</h1><p class="dim" style="font-size:18px;margin:0">That page doesn\'t exist. <a href="/">Back to the home page</a>.</p></div>')

n = sum(len(fs) for _, _, fs in os.walk(OUT))
print("built", n, "files")
