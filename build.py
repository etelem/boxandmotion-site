"""Build the Box & Motion Hoops static site from data/*.json into dist/.
Nov 13 2026 revamp (Elan): white Swish-inspired look, "headline first" game cards (team chips in both team colors),
game pages = scroll story -> the play of the game (our drawing) -> full game highlights and postgame interviews.
Team-color fills only for the visitor's followed teams (site.js). No logos, no nba.com/espn.com links."""
import json, os, re, shutil, datetime
from html import escape as E
from urllib.parse import quote_plus

T = json.load(open("data/teams.json"))
S = json.load(open("data/season.json"))
# hand-picked featured games (game of the week candidates) before nightly write-ups are merged in
FEATURED_KEYS = set(S["featured"])
# nightly text recaps written from each fact-checked reel config (kit/make_writeup.py)
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
SHORTDAY = lambda d: datetime.date.fromisoformat(d).strftime("%b %-d")

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
def result_for(g, c):
    me, opp = (g["as_"], g["hs"]) if c == g["away"] else (g["hs"], g["as_"])
    o = g["home"] if c == g["away"] else g["away"]
    where = "at" if c == g["away"] else "vs."
    return ("W" if me > opp else "L"), f"{max(me,opp)}–{min(me,opp)}", f"{where} {T[o]['name']}"
def last_line(c):
    g = team_games(c)[0]; r, sc, opp = result_for(g, c); return f"{r} {sc} {opp}"
def next_game(c):
    for day, tm, a, h in S["upcoming"]:
        if c in (a, h): return f"{day}, {'vs.' if c == h else 'at'} {T[h if c == a else a]['name']}, {tm} ET"
    return ""
def yt(g):
    day = datetime.date.fromisoformat(g["date"]).strftime("%B %-d %Y")
    q = f"{T[g['away']]['name']} vs {T[g['home']]['name']} highlights {day}"
    return "https://www.youtube.com/@NBA/search?query=" + quote_plus(q)

LINKS = json.load(open("data/links.json")) if os.path.isfile("data/links.json") else {}

def _cfg_for(key):
    p = f"kit/configs/{key[:10]}-{key[11:14]}-at-{key[15:18]}.json"
    return json.load(open(p)) if os.path.isfile(p) else None

def ot_label(g):
    if not g["ot"]: return ""
    c = _cfg_for(g["key"]); m = re.search(r"\b([2-9])OT\b", json.dumps(c)) if c else None
    return f"{m.group(1)}OT" if m else "OT"

def ot_words(g):
    return {"": "", "OT": " in overtime", "2OT": " in double overtime", "3OT": " in triple overtime"}.get(ot_label(g), f" in {ot_label(g)}")

LOGO = '<svg width="28" height="28" viewBox="0 0 100 100" aria-hidden="true"><rect x="9" y="9" width="82" height="82" rx="9" fill="none" stroke="#111214" stroke-width="8"/><path d="M24 24L40 40M40 24L24 40" stroke="#111214" stroke-width="8" stroke-linecap="round"/><path d="M33 50C34 62 42 69 53 69" fill="none" stroke="#FF5A1F" stroke-width="6.5" stroke-linecap="round" stroke-dasharray="0 10.5"/><circle cx="68" cy="68" r="9.5" fill="none" stroke="#FF5A1F" stroke-width="7.5"/></svg>'
FAVICON = "data:image/svg+xml," + quote_plus(LOGO.replace('width="28" height="28" ', '').replace('aria-hidden="true"', 'xmlns="http://www.w3.org/2000/svg"')).replace("+", "%20")
MARK = LOGO.replace('width="28" height="28"', 'width="16" height="16"')

# ---- team colors: both of a team's colors, always (Elan, Nov 13: "Lakers are purple AND gold") ----
_LIGHT = {"#FFFFFF", "#C4CED4", "#B8C4CA", "#A1A1A4", "#EEE1C6", "#C4CED3", "#BEC0C2"}
def c2_of(c):
    """A team's second color for the two-tone dot; very light ones (white, silver, cream) fall back to the dark shade."""
    t = T[c]; return t["dark"] if t["c2"].upper() in _LIGHT else t["c2"]
def dot2(c): return f"background:linear-gradient(135deg,{T[c]['c1']} 55%,{c2_of(c)} 55%)"
def grad(c): return f"linear-gradient(90deg,{c2_of(c)} 0 7px,transparent 7px),linear-gradient(120deg,{T[c]['c1']} 0%,{T[c]['dark']} 100%)"
def tchip(c, score, lose=False, name=None):
    return (f'<span class="tchip{" lo" if lose else ""}"><i style="{dot2(c)}"></i>{E(name or T[c]["name"])}'
            + (f' <b>{score}</b>' if score is not None else '') + '</span>')

def page(path, title, body, active=None, desc="Every NBA game, more than the box score: the story, the play that decided it, drawn in motion.", band=""):
    depth = path.count("/"); R = "/" if path == "404.html" else "../" * depth
    nav = [("Last Night", "last-night/index.html"), ("Your Team", "your-team/index.html"), ("Learn", "learn/index.html"),
           ("Odds", "odds/index.html"), ("Teams", "teams/index.html")]
    links = "".join(f'<a href="{R}{h}"{" aria-current=page" if n == active else ""}>{n}</a>' for n, h in nav)
    mlinks = "".join(f'<a href="{R}{h}"{" aria-current=page" if n == active else ""}>{n}</a>' for n, h in
                     [("Home", "index.html")] + nav + [("The Sunday Box", "newsletter/index.html"), ("About", "about/index.html")])
    html = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{E(title)}</title><meta name="description" content="{E(desc)}">
<meta property="og:title" content="{E(title)}"><meta property="og:description" content="{E(desc)}">
<link rel="icon" href="{FAVICON}">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@62..125,100..900&family=Albert+Sans:wght@400;600;700&display=swap">
<link rel="stylesheet" href="{R}assets/site.css"></head>
<body data-root="{R}"><div class="pg">
<header class="top"><div class="w hd">
<a class="brand" href="{R}index.html"><span class="mark">{LOGO}</span><span class="word">Box &amp; Motion <span>Hoops</span></span></a>
<nav class="gnav" aria-label="Main">{links}</nav>
<span class="sp"></span>
<a class="pill sm only-d{' on' if active == 'Sunday Box' else ''}" href="{R}newsletter/index.html">Get The Sunday Box</a>
<button class="burger" type="button" aria-label="Menu" aria-expanded="false" data-burger><svg width="20" height="14" aria-hidden="true"><path d="M1 2h18M1 12h18" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg></button>
</div><div class="w"><nav class="mmenu" aria-label="Menu" data-menu>{mlinks}</nav></div></header>
{band}
<main class="w">{body}</main>
<footer class="w foot"><span class="word">Box &amp; Motion <span>Hoops</span></span>
<div class="fl"><a href="{R}last-night/index.html">Last Night</a><a href="{R}your-team/index.html">Your Team</a><a href="{R}learn/index.html">Learn</a><a href="{R}odds/index.html">Odds</a><a href="{R}teams/index.html">Teams</a><a href="{R}newsletter/index.html">The Sunday Box</a><a href="https://www.youtube.com/@boxandmotion" target="_blank" rel="noopener">YouTube</a><a href="{R}about/index.html">About</a></div>
<div class="legal">Unofficial fan site. Not affiliated with or endorsed by the NBA or any team. Drawings are original, not traced from footage; no logos. Video plays from official uploads only. Updated {S['updated']}.</div></footer>
</div><script src="{R}assets/data.js"></script><script src="{R}assets/site.js"></script></body></html>"""
    full = os.path.join(OUT, path); os.makedirs(os.path.dirname(full) or OUT, exist_ok=True)
    open(full, "w").write(html)
    return R

def closer(R):
    return (f'<section class="closer"><div><h2 class="h2">The week, in one box.</h2><p>The Sunday Box: the games that mattered and the plays behind them. Free, every Sunday.</p></div>'
            f'<a class="pill wht" href="{R}newsletter/index.html">Get The Sunday Box →</a></section>')

# ---- story score: which game leads the night ----
def story_score(g):
    """Facts the recap already verified, never guessed (Nov 13).
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

# ---- game card: headline first (Elan's pick, Nov 13) ----
def headline(g):
    f = S["featured"].get(g["key"])
    if f and f.get("headline"): return f["headline"].rstrip(".")
    ws, lsc = max(g["as_"], g["hs"]), min(g["as_"], g["hs"])
    return f"{T[g['win']]['name']} beat the {T[g['lose']]['name']} {ws}–{lsc}{ot_words(g)}"
def meta(g): return f"Final{' · ' + ot_label(g) if g['ot'] else ''} · {WEEKDAY(g['date'])} · {T[g['home']]['city']}"

def hf_card(g, R, big=False, top=False, extra_attr=""):
    w, l = g["win"], g["lose"]
    ws, lsc = (g["as_"], g["hs"]) if w == g["away"] else (g["hs"], g["as_"])
    href = f"{R}games/{g['slug']}/index.html"
    split = ""
    if big:
        f = S["featured"].get(g["key"]) or {}
        bits = []
        if f.get("top"):
            n, tm, note, p = f["top"][0]; bits.append(f"<span><b>{E(n)} {p}</b> · {E(note)}</span>")
        if f.get("battle"):
            k, v1, v2 = f["battle"][0]; la, lb = f.get("battle_labels", ["", ""])
            bits.append(f"<span><b>{E(k)}</b> {E(la)} {v1}, {E(lb)} {v2}</span>")
        if bits: split = f'<div class="hfsplit">{"".join(bits)}</div>'
    flags = (f'<span class="flag top-flag">Top game</span>' if top else '') + '<span class="flag mine">★ Your team</span>'
    return (f'<a class="hf{" hfbig" if big else ""}" href="{href}" data-teams="{g["away"]} {g["home"]}" data-key="{g["key"]}"{extra_attr}>'
            f'<div class="hftop">{tchip(w, ws)}{tchip(l, lsc, lose=True)}{flags}</div>'
            f'<div class="hfh">{E(headline(g))}</div>{split}<div class="hfmeta">{E(meta(g))}</div></a>')

def ranked(games): return sorted(games, key=story_score, reverse=True)

def games_block(games, R, show_top=True, three=False):
    """A night's games, best story first; site.js moves a visitor's followed teams to the front and labels them."""
    gs = ranked(games)
    if os.environ.get("BM_DEBUG"): print([(g["key"], story_score(g)) for g in gs])
    cards = "".join(hf_card(g, R, top=(show_top and i == 0)) for i, g in enumerate(gs))
    return f'<div class="hfgrid{" three" if three else ""}" data-games>{cards}</div>'

def star_btn(c, label="Follow"):
    return f'<button type="button" class="pill sm star" data-team="{c}" aria-pressed="false">★ <span class="lbl">{label}</span></button>'

# ---- Learn: deep dives (coach's boards, signature moves, X's and O's, trend boards, scouting reports) ----
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
MOVES = []
for m in DD.get("moves", []):
    cfg = json.load(open(m["config"]))
    MOVES.append(dict(m, steps=cfg.get("steps", []), number=cfg.get("number", "")))
MOVES.sort(key=lambda m: m["published"], reverse=True)
XO = []
for x in DD.get("xo", []):
    cfg = json.load(open(x["config"]))
    XO.append(dict(x, title=cfg["title"], sub=cfg["situation"], beats=cfg["beats"]))
XO.sort(key=lambda x: x["published"], reverse=True)
TRENDS = sorted(DD.get("trends", []), key=lambda x: x["published"], reverse=True)
PLAYERS = []
if os.path.isdir("data/players"):
    for fn in sorted(os.listdir("data/players")):
        if fn.endswith(".json"): PLAYERS.append(json.load(open(f"data/players/{fn}")))
PLAYERS.sort(key=lambda x: x["published"], reverse=True)

def _thumb(anim):
    j = os.path.splitext(anim)[0] + ".jpg"
    return f"posters/learn/{j}" if os.path.isfile(f"src/posters/learn/{j}") else None
# (published, kind, title, meta line, href, thumbnail)
LEARN = ([("2026-11-07", "report", "Luka Dončić: 40 a night", "Scouting report · Lakers", "players/luka-doncic/index.html", _thumb("luka-stepback.html")),
          ("2026-11-07", "board", "JJ Redick: how they closed at Utah", "Coach's board · Lakers", "coaches/jj-redick/index.html", _thumb("lakers-utah-close.html"))]
         + [(b["published"], "board", f'{b["coach"]}: {b["title"]}', f"Coach's board · {T[b['team']]['name']}", f'coaches/{b["coach_slug"]}/index.html', _thumb(b["anim"])) for b in BOARDS]
         + [(m["published"], "move", m["title"], f"Signature move · {m['player']}", f'moves/{m["slug"]}/index.html', _thumb(m["anim"])) for m in MOVES]
         + [(x["published"], "xo", x["title"], "X's & O's · learn the game", f'xo/{x["slug"]}/index.html', _thumb(x["anim"])) for x in XO]
         + [(P["published"], "report", P["name"], f"Scouting report · {T[P['team']]['name']}", f'players/{P["slug"]}/index.html', _thumb(P["move"]["anim"])) for P in PLAYERS]
         + [(x["published"], "trend", x["title"], f"Trend board · {T[x['team']]['name']}", f'trends/{x["slug"]}/index.html', _thumb(x["anim"])) for x in TRENDS])
LEARN.sort(key=lambda x: x[0], reverse=True)
KINDS = [("all", "All"), ("move", "Moves"), ("xo", "X’s & O’s"), ("board", "Coach’s board"), ("trend", "Trends"), ("report", "Scouting reports")]
def learn_card(R, item):
    pub, kind, title, sub, href, img = item
    pic = f'<img src="{R}{img}" alt="" loading="lazy">' if img else '<span class="noimg"></span>'
    return f'<a class="lc" href="{R}{href}" data-kind="{kind}">{pic}<div class="tx"><b>{E(title)}</b><span>{E(sub)}</span></div></a>'

def anim_frame(R, file, label, music=None):
    """An animation page in an iframe that sizes itself (the page posts its height); optional 'Play with sound'."""
    btn = (f'<button type="button" class="pill sm snd" data-snd="{R}{music}" style="align-self:flex-start">▶ Play with sound</button>' if music else '')
    return (f'<div class="anim-wrap" style="display:flex;flex-direction:column;gap:10px">'
            f'<iframe class="anim" src="{R}anim/{file}?embed=1" title="{E(label)}" loading="lazy" style="width:100%;border:0;display:block;height:560px"></iframe>'
            f'{btn}</div>')
def short_btn(v): return f'<a class="pill or" href="https://youtube.com/shorts/{v}" target="_blank" rel="noopener">▶ Watch the Short</a>' if v else ""
def learn_crumbs(R, *rest): return f'<nav aria-label="Breadcrumb" class="crumbs"><a href="{R}learn/index.html">Learn</a>' + "".join(f"<span>/</span>{x}" for x in rest) + '</nav>'

# ---- output dir, copied media, client data ----
shutil.rmtree(OUT, ignore_errors=True)  # start clean so removed pages disappear
if os.path.isdir("reels"): shutil.copytree("reels", f"{OUT}/reels")
if os.path.isdir("src/anim"): shutil.copytree("src/anim", f"{OUT}/anim")
if os.path.isdir("src/posters"): shutil.copytree("src/posters", f"{OUT}/posters")
if os.path.isdir("src/audio"): shutil.copytree("src/audio", f"{OUT}/audio")
os.makedirs(f"{OUT}/assets", exist_ok=True)

# "The play of the game" for games without a Short (Elan, Nov 13): the reel loops just its play scene with ?clip=play.
CLIP_OK = set()
for key in REELS:
    p = f"{OUT}/reels/{key}/index.html"; src = open(p).read()
    a1 = "let t = still ? TOTAL : 0, playing = !still, last = null, shownScene = -1;"
    a2 = "t = Math.max(0, Math.min(TOTAL, t));"
    if a1 in src and a2 in src and "id: 'play'" in src:
        src = src.replace(a1, a1 + " const CLIP = /[?&]clip=play/.test(location.search) ? SCENES.find((s) => s.id === 'play') : null; if (CLIP) { t = CLIP.t0; playing = true; }", 1)
        src = src.replace(a2, a2 + " if (CLIP && (t >= CLIP.t1 || t < CLIP.t0)) { t = CLIP.t0; jumped(); }", 1)
        src = src.replace('<script>if (/[?&]embed=1/.test(location.search)) document.documentElement.classList.add("embed");</script>',
                          '<script>if (/[?&]embed=1/.test(location.search)) document.documentElement.classList.add("embed");if (/[?&]clip=play/.test(location.search)) document.documentElement.classList.add("clip");</script>'
                          '<style>html.clip .transport,html.clip .chips{display:none!important}</style>', 1)
        open(p, "w").write(src); CLIP_OK.add(key)

def play_scene(key):
    """The reel's play scene name and the config's one-line description of it (already fact-checked)."""
    p = f"reels/{key}/index.html"
    name = None
    if os.path.isfile(p):
        m = re.search(r"\{id: 'play', name: '([^']+)'", open(p).read()); name = m.group(1) if m else None
    c = _cfg_for(key); desc = None
    pl = (c or {}).get("play")
    if isinstance(pl, str):
        m = re.search(r"""['"]comment['"]:\s*(['"])(.+?)\1""", pl); pl = {"comment": m.group(2)} if m else {}
    if isinstance(pl, dict):
        name = pl.get("head") or name
        s = (pl.get("comment") or "").split(" An original illustration")[0].strip()
        if s: desc = s.rstrip(".") + "."
    return name, desc

client = {"teams": {c: {"name": T[c]["name"], "city": T[c]["city"], "slug": T[c]["slug"], "c1": T[c]["c1"], "c2": c2_of(c), "dark": T[c]["dark"],
          "conf": T[c]["conf"], "rec": rec(c), "seed": seed(c), "top6": O[c]["top6"], "chg": chg(O[c]["chg"]), "wins": O[c]["wins"],
          "last": last_line(c), "next": next_game(c)} for c in T}}
open(f"{OUT}/assets/data.js", "w").write("window.BM=" + json.dumps(client, ensure_ascii=False) + ";")
shutil.copy("src/site.css", f"{OUT}/assets/site.css"); shutil.copy("src/site.js", f"{OUT}/assets/site.js")

# ---- home ----
R = ""
LAST_R = ranked(LAST)
tabs = "".join(f'<button class="gtab{" on" if i == 0 else ""}" type="button" data-hero-tab="{i}">{g["win"]} {max(g["as_"],g["hs"])} · {g["lose"]} {min(g["as_"],g["hs"])}</button>' for i, g in enumerate(LAST_R))
heroes = "".join(hf_card(g, R, big=True, top=(i == 0), extra_attr=f' data-hero="{i}"' + ('' if i == 0 else ' hidden')) for i, g in enumerate(LAST_R))
# the 50-point nights: verified top-scorer lines from the recaps
BIG = []
for g in GAMES:
    for n, tm, note, p in (S["featured"].get(g["key"]) or {}).get("top", [])[:1]:
        if p >= 50: BIG.append((g["date"], tm, n, p, note, g))
BIG = sorted(BIG, key=lambda x: x[0], reverse=True)[:3]
big_cards = "".join(f'<a class="stat" href="games/{g["slug"]}/index.html"><div class="row"><span class="ab">{tm}</span><small>{SHORTDAY(d)}</small></div>'
                    f'<div><div class="n"{" style=color:var(--warm)" if i == 1 else ""}>{p}</div><div class="who">{E(n.split(" ")[0])}</div><small>{E(note)}</small></div></a>'
                    for i, (d, tm, n, p, note, g) in enumerate(reversed(BIG)))
TONIGHT_DAY = S["upcoming"][0][0] if S["upcoming"] else None
tonight = "".join(f'<a class="tn" href="teams/{T[h]["slug"]}/index.html" data-teams="{a} {h}"><span class="tt">{tm}</span><span class="tteams"><span><i class="dot" style="{dot2(a)}"></i>{E(T[a]["name"])}</span><span class="at">at</span><span><i class="dot" style="{dot2(h)}"></i>{E(T[h]["name"])}</span></span></a>'
                  for day, tm, a, h in S["upcoming"] if day == TONIGHT_DAY)
home = f'''<section class="hero">
<div><p class="k">Unofficial · drawn, not filmed</p>
<h1 class="h1">More than the <b>box score.</b></h1>
<p class="hp">The box score tells you who scored. We show you how the game was won: the run, the matchup, the play that decided it. Plus <a href="learn/index.html">Learn the Game</a> and <a href="newsletter/index.html">The Sunday Box</a>.</p>
<div class="ctas"><a class="pill or" href="last-night/index.html">See last night →</a><a class="pill" href="learn/index.html">Learn the game</a></div></div>
<div><div class="gtabs" role="tablist">{tabs}</div>{heroes}</div>
</section>
<section class="nums">
<a class="num" href="last-night/index.html"><div class="t"><span>01</span><span>↗</span></div><div><b>Last night</b><p>Every game, the story and the play that decided it.</p></div></a>
<a class="num" href="your-team/index.html"><div class="t"><span>02</span><span>↗</span></div><div><b>Your team</b><p>Pick your teams. They show up first, in their colors.</p></div></a>
<a class="num" href="learn/index.html"><div class="t"><span>03</span><span>↗</span></div><div><b>Learn the game</b><p>Moves and plays, drawn step by step.</p></div></a>
<a class="num" href="newsletter/index.html"><div class="t"><span>04</span><span>↗</span></div><div><b>The Sunday Box</b><p>The week in one email.</p></div></a>
</section>
<section>
<div class="shead"><div><p class="k">{WEEKDAY(LAST_DATE)} · {len(LAST)} games</p><h2 class="h2">Last night.</h2><p class="lead">Your teams first. Tap any game for the story and the play.</p></div><a class="pill sm" href="last-night/index.html">All games →</a></div>
{games_block(LAST, R)}
</section>
{f"""<section><div class="shead"><div><p class="k">Tonight · {E(TONIGHT_DAY)} · times ET</p><h2 class="h2">On the schedule.</h2></div><a class="pill sm" href="odds/index.html">What’s at stake →</a></div>
<div class="tonight">{tonight}</div></section>""" if tonight else ""}
{f"""<section class="fifty"><div><p class="k">The 50-point nights</p><h2 class="h2">Big nights,<br>drawn big.</h2><p class="lead">When a player goes off, we draw the shot that got him there and check every number.</p></div>
<div class="stack">{big_cards}</div></section>""" if BIG else ""}
<section><div class="shead"><div><p class="k">Learn the game</p><h2 class="h2">New in the library.</h2></div><a class="pill sm" href="learn/index.html">See all {len(LEARN)} →</a></div>
<div class="rail">{"".join(learn_card(R, x) for x in LEARN[:4])}</div></section>
{closer(R)}'''
page("index.html", "Box & Motion Hoops: every NBA game, more than the box score", home)

# ---- last night ----
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
            d = f"{ym}-{day:02d}"; n = counts.get(d)
            cls = ' class="on"' if d == sel else ''
            cells.append(f'<a{cls} href="{R}days/{d}/index.html" title="{WEEKDAY(d)}: {n} game{"s" if n != 1 else ""}">{day}<i></i></a>' if n else f'<span class="off">{day}</span>')
        out.append(f'<div class="card pad cal"><p class="k">{first.strftime("%B %Y")}</p><div class="cal-g">{"".join(f"<b>{w}</b>" for w in "MTWTFSS")}{"".join(cells)}</div></div>')
    return f'<section class="sec" id="archive"><div><p class="k">Archive</p><h2 class="h2">Every game day.</h2><p class="lead">Pick a date to see that day’s results.</p></div><div class="cal-row">{"".join(out)}</div></section>'

R = "../"
top_g = LAST_R[0]
earlier = sorted({g["date"] for g in GAMES if g["date"] != LAST_DATE and g["date"] >= WEEK_START}, reverse=True)
ear = "".join(f'<section class="sec"><p class="k">{WEEKDAY(d)}</p>{games_block([g for g in GAMES if g["date"]==d], R, show_top=False, three=True)}</section>' for d in earlier)
body = f'''<section><p class="k">{WEEKDAY(LAST_DATE)} · {len(LAST)} games</p><h1 class="h1">Last night.</h1>
<p class="lead">The top game up front, your teams next, then the rest. Tap any game for the full story.</p>
<div class="tabs" style="margin-top:18px"><button class="pill" data-mode="mine">Your teams</button><button class="pill" data-mode="all">All games</button><a class="pill" href="#archive">Archive</a></div></section>
<section style="max-width:780px"><p class="k" style="margin-bottom:10px">Top game of the night</p>{hf_card(top_g, R, big=True, top=True)}</section>
<section><p class="k" style="margin-bottom:12px">The rest of the night</p>{games_block([g for g in LAST if g is not top_g], R, show_top=False, three=True)}
<p class="dim none-note hidden" style="margin:10px 0 0">None of your teams played last night. <button class="pill sm" data-mode="all">Show all games</button></p></section>
{'<section class="sec"><h2 class="h2">Earlier this week.</h2>' + ear + '</section>' if ear else ''}
{calendar(R)}'''
page("last-night/index.html", "Last night · Box & Motion Hoops", body, active="Last Night")

# ---- archive: one page per game date ----
DATES = sorted({g["date"] for g in GAMES})
for i, d in enumerate(DATES):
    R = "../../"
    prev_l = f'<a class="pill sm" href="{R}days/{DATES[i-1]}/index.html">← {WEEKDAY(DATES[i-1])}</a>' if i > 0 else ''
    next_l = f'<a class="pill sm" href="{R}days/{DATES[i+1]}/index.html">{WEEKDAY(DATES[i+1])} →</a>' if i + 1 < len(DATES) else ''
    day_games = [g for g in GAMES if g["date"] == d]
    body = f'''<nav aria-label="Breadcrumb" class="crumbs"><a href="{R}last-night/index.html">Games</a><span>/</span><span>{WEEKDAY(d)}</span></nav>
<section><p class="k">{len(day_games)} game{'s' if len(day_games) != 1 else ''}</p><h1 class="h1">{WEEKDAY(d)}.</h1><div class="row">{prev_l}{next_l}</div></section>
<section>{games_block(day_games, R, three=True).replace(" data-games", "")}</section>
{calendar(R, d)}'''
    page(f"days/{d}/index.html", f"NBA games, {WEEKDAY(d)} · Box & Motion Hoops", body, active="Last Night",
         desc=f"Every NBA result from {WEEKDAY(d)}, with the story and the play that decided it.")

# ---- game pages: scroll story -> the play of the game -> full game highlights and postgame interviews ----
ORD = ["first", "second", "third", "fourth"]
def got_away(lq, wq, ot):
    """One line, from the losing team's side, on where the game got away. Uses only the line score."""
    n = len(lq); m = [a - b for a, b in zip(lq, wq)]
    name = lambda i: f"the {ORD[i]} quarter" if i < 4 else ("overtime" if i == 4 else f"the {i - 3}{'nd' if i == 5 else 'rd' if i == 6 else 'th'} overtime")
    after3 = sum(m[:3])
    if ot: return f"Forced overtime, then lost {name(n - 1)} {lq[-1]}–{wq[-1]}."
    if after3 >= 0:
        lead = f"Led by {after3} after three quarters" if after3 > 0 else "Tied after three quarters"
        return f"{lead}, then lost the fourth {lq[3]}–{wq[3]}."
    k = min(range(n), key=lambda i: m[i])
    if k == 3 and after3 >= -5: return f"Within {-after3} after three quarters, then lost the fourth {lq[3]}–{wq[3]}."
    rl, rw = sum(lq[k + 1:]), sum(wq[k + 1:])
    if k < n - 1 and rl - rw >= 5: return f"Lost {name(k)} {lq[k]}–{wq[k]}, then won the rest of the game {rl}–{rw}."
    if all(x < 0 for x in m): return f"Trailed in every quarter; the biggest gap was {name(k)}, {lq[k]}–{wq[k]}."
    return f"Lost {name(k)} {lq[k]}–{wq[k]}, the stretch that decided it."

def period_names(g, n):
    if n <= 4: return ["Q1", "Q2", "Q3", "Q4"][:n]
    if n == 5: return ["Q1", "Q2", "Q3", "Q4", "OTs" if ot_label(g) not in ("", "OT") else "OT"]
    return ["Q1", "Q2", "Q3", "Q4"] + ["OT" if i == 0 else f"{i+1}OT" for i in range(n - 4)]

def lead_chart(g, wq, lq, shown):
    """Winner's lead after each period: bars up in the winner's color, down in the loser's; a ring for a tie."""
    w, l = g["win"], g["lose"]; leads = []; cw = cl = 0
    for x, y in zip(wq, lq): cw += x; cl += y; leads.append(cw - cl)
    mx = max(1, max(abs(v) for v in leads)); names = period_names(g, len(leads)); cols = ""
    for i, v in enumerate(leads):
        up = round(v / mx * 88) if v > 0 else 0; dn = round(-v / mx * 88) if v < 0 else 0
        cols += (f'<div class="lcol{" off" if i >= shown else ""}"><div class="lup"><span class="lv">{("+" + str(v)) if v > 0 else ("Tied" if v == 0 else "")}</span>'
                 + ('<span class="ltie"></span>' if v == 0 else '') + f'<span class="lbar" style="height:{up}px;background:{T[w]["c1"]}"></span></div>'
                 f'<div class="ldn"><span class="lbar" style="height:{dn}px;background:{T[l]["c1"]}"></span><span class="lv">{("+" + str(-v)) if v < 0 else ""}</span></div>'
                 f'<span class="lq">{names[i]}</span></div>')
    return (f'<div class="lleg"><span style="color:{T[w]["c1"]}">↑ {E(T[w]["name"])} lead</span><span style="color:{T[l]["c1"]}">{E(T[l]["name"])} lead ↓</span></div>'
            f'<div class="lchart"><span class="zero"></span>{cols}</div>')

def score_after(g, wq, lq, n):
    w, l = g["win"], g["lose"]; sw, sl = sum(wq[:n]), sum(lq[:n])
    if sw == sl: return f"Tied {sw}–{sl}"
    return f"{T[w]['name'] if sw > sl else T[l]['name']} {max(sw, sl)}–{min(sw, sl)}"

def scroll_story(g, f, ls, R):
    a, h, w, l = g["away"], g["home"], g["win"], g["lose"]
    wq, lq = (ls["away"], ls["home"]) if w == a else (ls["home"], ls["away"])
    ws, lsc = sum(wq), sum(lq)
    q1w, q1l, hw, hl = wq[0], lq[0], sum(wq[:2]), sum(lq[:2])
    def lead_txt(n, when):
        sw, sl = sum(wq[:n]), sum(lq[:n])
        if sw == sl: return f"tied {sw}–{sl} {when}"
        lead = T[w]["name"] if sw > sl else T[l]["name"]
        return f"the {lead} led {max(sw,sl)}–{min(sw,sl)} {when}"
    s1 = (lead_txt(1, "after one quarter") + ". At the half, " + lead_txt(2, "").strip() + ".").replace(" .", ".")
    s1 = s1[0].upper() + s1[1:]
    three = f.get("three") or []
    top = (f.get("top") or [None])[0]
    panes, steps = [], []
    # 1 · first half: lead bars through the half
    panes.append(f'<div class="phead"><span class="hn">{hw}–{hl}</span><span class="hc">{E(T[w]["name"])}–{E(T[l]["name"])} at the half</span></div>{lead_chart(g, wq, lq, 2)}')
    steps.append(("First half", "How it started.", s1))
    # 2 · the first of the recap's three things, with the top scorer's number
    if three:
        if top:
            n, tm, note, p = top
            panes.append(f'<div class="bignum" style="--team-grad:{grad(tm)}"><div class="k" style="color:rgba(255,255,255,.85)">{E(n.upper())} · {E(T[tm]["name"].upper())}</div><div class="bn">{p}</div><div class="bl">{E(note)}</div></div>')
        else:
            panes.append(f'<div class="phead"><span class="hn">{ws}–{lsc}</span></div>{lead_chart(g, wq, lq, len(wq))}')
        steps.append(("The difference", three[0][0], three[0][1]))
    # 3 · the second thing, with the whole game's lead bars
    if len(three) > 1:
        panes.append(f'<div class="phead"><span class="hn">{sum(wq[:3])}–{sum(lq[:3])}</span><span class="hc">{E(T[w]["name"])}–{E(T[l]["name"])} after three</span></div>{lead_chart(g, wq, lq, len(wq))}')
        steps.append(("How it turned", three[1][0], three[1][1]))
    # 4 · the third thing, with where it was won
    if len(three) > 2 and f.get("battle"):
        la, lb = f.get("battle_labels", [w, l])
        ca, cb = (T[la]["c1"] if la in T else "#111214"), (T[lb]["c1"] if lb in T else "#8a8c92")
        rows = "".join(f'<div class="tw"><span class="lbl">{E(k)}</span><span class="v" style="color:{ca}">{v1}</span><div class="tr"><span style="flex:{max(v1,0.5)};background:{ca}"></span><span style="flex:{max(v2,0.5)};background:{cb}"></span></div><span class="v" style="color:{cb};text-align:right">{v2}</span></div>' for k, v1, v2 in f["battle"])
        panes.append(f'<div style="flex:1;display:flex;flex-direction:column;justify-content:center"><div class="lleg"><span style="color:{ca}">{E(la)}</span><span style="color:{cb}">{E(lb)}</span></div>{rows}</div>')
        steps.append(("Where it was won", three[2][0], three[2][1]))
    # 5 · final: line score, the other side, what it meant
    names = period_names(g, len(wq))
    tbl = (f'<div class="tbox"><table class="lines"><tr><th></th>{"".join(f"<th>{n}</th>" for n in names)}<th>F</th></tr>'
           f'<tr><td><i class="dot" style="{dot2(a)}"></i>{a}</td>{"".join(f"<td>{x}</td>" for x in ls["away"])}<td><b>{g["as_"]}</b></td></tr>'
           f'<tr><td><i class="dot" style="{dot2(h)}"></i>{h}</td>{"".join(f"<td>{x}</td>" for x in ls["home"])}<td><b>{g["hs"]}</b></td></tr></table></div>')
    meant = (f'<p><b>What it meant:</b> the {E(T[w]["name"])} are {rec(w)}, {seed(w)}, with {O[w]["top6"]}% top-6 odds now. '
             f'The {E(T[l]["name"])} are {rec(l)}, {seed(l)}, at {O[l]["top6"]}%.</p>')
    other = f'<p><b>From the {E(T[l]["name"])}’ side:</b> {E(got_away(lq, wq, g["ot"]))}</p>'
    panes.append(f'<div class="phead"><span class="hn">{ws}–{lsc}</span><span class="hc">{E(meta(g).split(" · ")[0])}{" · " + ot_label(g) if g["ot"] else ""}</span></div>{lead_chart(g, wq, lq, len(wq))}')
    steps.append(("Final" + (f", {ot_label(g)}" if g["ot"] else ""), f"{T[w]['name']} {ws}, {T[l]['name']} {lsc}.", tbl + other + meant))
    dots = "".join(f'<button type="button" data-go="{i}" aria-label="Part {i+1}"{" class=on" if i == 0 else ""}><i></i></button>' for i in range(len(steps)))
    pane_html = "".join(f'<div class="pane{" on" if i == 0 else ""}" data-pane-i="{i}">{p}</div>' for i, p in enumerate(panes))
    step_html = ""
    for i, (k, h3, txt) in enumerate(steps):
        body = txt if txt.startswith("<") else f"<p>{E(txt)}</p>"
        hint = '<span class="hint">Scroll to keep going ↓</span>' if i == 0 else ''
        step_html += f'<div class="step"><span class="sk">{i+1} · {E(k)}</span><h3>{E(h3)}</h3>{body}{hint}</div>'
    return (f'<div class="sr" data-story><div class="vis"><div class="top"><span>THE STORY · {len(steps)} PARTS</span><span class="dots">{dots}</span></div>{pane_html}</div>'
            f'<div class="scroller">{step_html}</div></div>')

COURT = '<svg class="pcourt" viewBox="0 0 350 197" preserveAspectRatio="xMidYMid slice" fill="none" aria-hidden="true"><g stroke="rgba(255,255,255,.14)" stroke-width="1.5"><path d="M175 0V197"/><circle cx="175" cy="98" r="34"/><rect x="0" y="62" width="62" height="72"/><rect x="288" y="62" width="62" height="72"/><path d="M0 18H24A86 86 0 0 1 24 178H0M350 18H326A86 86 0 0 0 326 178H350"/></g></svg>'
for g in GAMES:
    R = "../../"
    a, h, w, l = g["away"], g["home"], g["win"], g["lose"]
    ws, lsc = max(g["as_"], g["hs"]), min(g["as_"], g["hs"])
    margin = ws - lsc
    auto = f"{T[w]['city']} beat {T[l]['city']} {ws}–{lsc}{ot_words(g)}, a {'one-point' if margin == 1 else str(margin) + '-point'} {'road' if w == a else 'home'} win. The {T[w]['name']} move to {g['rec'][w]}; the {T[l]['name']} fall to {g['rec'][l]}."
    f = S["featured"].get(g["key"]); ls = S["linescores"].get(g["key"])
    def _words(t): return set(re.findall(r"[a-z0-9]+", t.lower())) - {"a", "an", "the", "in", "of", "it", "and", "to"}
    dek = (f or {}).get("dek") or ""
    if not dek or len(_words(headline(g)) & _words(dek)) >= 0.6 * max(1, len(_words(headline(g)))): dek = auto
    L = LINKS.get(g["key"], {})
    v = g["video"]
    # 2 · the play of the game: our Short's animation when there is one, else the reel's play scene on a loop
    clip = None
    if os.path.isfile(f"src/anim/short-{g['key']}.html"):
        clip = f"{R}anim/short-{g['key']}.html?short=1"
    elif g["key"] in CLIP_OK:
        clip = f"{R}reels/{g['key']}/index.html?embed=1&clip=play"
    pname, pdesc = play_scene(g["key"])
    nsec = 0
    story = ""
    if f and ls and f.get("three"):
        nsec += 1
        story = f'''<section id="story"><p class="k">{nsec} · What happened</p><h2 class="h2">The game, in {len(f.get("three", []))+2 if f.get("battle") else len(f.get("three", []))+1} parts.</h2>
{scroll_story(g, f, ls, R)}</section>'''
    play = ""
    if clip:
        nsec += 1
        play = f'''<section id="play"><div class="playsec"><div><p class="k">{nsec} · The play of the game</p>
<h2 class="h2">{E(pname or "The play, drawn")}.</h2>
{f'<p class="lead" style="font-size:16px">{E(pdesc)}</p>' if pdesc else ''}
<div class="ctas" style="margin-top:18px">{f'<a class="pill sm or" href="https://youtube.com/shorts/{v}" target="_blank" rel="noopener">▶ Our Short on YouTube</a>' if v else ''}</div>
<p class="dim" style="font-size:13px;margin:14px 0 0">Original illustration, drawn from written accounts. Not traced from footage, not to scale.</p></div>
<div class="phone"><iframe src="{clip}" title="The play of the game, drawn: {E(T[a]['name'])} at {E(T[h]['name'])}" loading="lazy" allow="autoplay"></iframe></div></div></section>'''
    nsec += 1
    day = datetime.date.fromisoformat(g["date"]).strftime("%B %-d %Y")
    pg = (f'https://www.youtube.com/watch?v={L["postgame"]}' if L.get("postgame") else
          "https://www.youtube.com/results?search_query=" + quote_plus(f'{T[w]["name"]} {T[l]["name"]} postgame interviews {day}'))
    hl_url = (f'https://www.youtube.com/watch?v={L["highlights"]}' + (f'&t={int(L["start"])}s' if L.get("start") else '')) if L.get("highlights") else yt(g)
    se = (f' data-start="{int(L["start"])}"' if L.get("start") is not None else '') + (f' data-end="{int(L["end"])}"' if L.get("end") else '')
    from_txt = f'From the NBA’s nightly recap. Tap to play here.' if L.get("from") else 'Tap to play here.'
    embed = (f'<button type="button" class="player" data-yt="{E(L["highlights"])}"{se} style="--team-grad:linear-gradient(135deg,{T[w]["c1"]} 0%,{T[w]["dark"]} 58%,{T[l]["dark"]} 82%,{T[l]["c1"]} 100%)" aria-label="Play the official {E(T[a]["name"])} at {E(T[h]["name"])} highlights">'
             f'{COURT}<span class="pchip">OFFICIAL · NBA ON YOUTUBE</span><span class="pb"><svg width="24" height="26" viewBox="0 0 24 26" aria-hidden="true"><path d="M3 2L22 13L3 24Z" fill="#111214"/></svg></span>'
             f'<span class="pcap"><b>{E(T[a]["name"])} at {E(T[h]["name"])} · full game highlights</b><span>{from_txt}</span></span></button>') if L.get("highlights") else ""
    watch = f'''<section><div class="watchsec"><p class="k">{nsec} · Full game highlights and postgame</p><h2 class="h2">Full game highlights.</h2>{embed}
<a class="wrow" href="{hl_url}" target="_blank" rel="noopener"><span class="ic">▶</span><span class="tx">Full game highlights on YouTube</span><span class="ar">↗</span></a>
<a class="wrow" href="{pg}" target="_blank" rel="noopener"><span class="ic">▶</span><span class="tx">Postgame interviews on YouTube</span><span class="ar">↗</span></a></div></section>'''
    top_flag = '<span class="flag" style="margin-left:8px">Top game</span>' if g in LAST_R[:1] else ''
    head = f'''<nav aria-label="Breadcrumb" class="crumbs"><a href="{R}last-night/index.html">Games</a><span>/</span><a href="{R}teams/{T[a]["slug"]}/index.html">{E(T[a]["name"])}</a><span>at</span><a href="{R}teams/{T[h]["slug"]}/index.html">{E(T[h]["name"])}</a></nav>
<section><div class="hftop">{tchip(w, ws)}{tchip(l, lsc, lose=True)}{top_flag}</div>
<h1 class="gh1">{E(headline(g))}</h1><div class="hfmeta" style="margin-bottom:10px">{E(meta(g))}</div>
<p class="lead">{E(dek)}</p>{'<a class="jump" href="#play">▶ Jump to the play</a>' if clip and story else ''}</section>'''
    body = head + story + play + watch + closer(R)
    page(f"games/{g['slug']}/index.html", f"{T[a]['name']} {g['as_']}, {T[h]['name']} {g['hs']} · Box & Motion Hoops", body, active="Last Night", desc=dek)

# ---- your team ----
R = "../"
picker = "".join(star_btn(c, T[c]["name"]).replace('<span class="lbl">', '<span>').replace("pill sm star", "star") for c in sorted(T, key=lambda c: T[c]["name"]))
body = f'''<section><p class="k">Your team</p><h1 class="h1">Your teams, first.</h1>
<p class="lead">Pick the teams you follow. They lead the home page and Last Night, and show up in their colors across the site. Saved on this device, no sign-up.</p></section>
<section><div class="picker">{picker}</div></section>
<section><p class="dim" id="yt-empty">Pick a team above to see it here.</p><div class="ytgrid" id="yt-cards"></div></section>'''
page("your-team/index.html", "Your team · Box & Motion Hoops", body, active="Your Team")

# ---- teams index ----
def tcard2(c, R):
    return (f'<div class="tcard2" data-team-card="{c}" style="--team-grad:{grad(c)}"><span class="tseed">{S["seeds"][c]}</span>'
            f'<a class="tinfo" href="{R}teams/{T[c]["slug"]}/index.html"><div class="tnm"><i class="dot" style="{dot2(c)}"></i>{E(T[c]["city"])} {E(T[c]["name"])}</div><div class="trc">{rec(c)} · top-6 odds {O[c]["top6"]}%</div></a>{star_btn(c)}</div>')
R = "../"
panes = "".join(f'<div class="tgrid{" hidden" if conf == "West" else ""}" data-pane="conf" data-value="{conf}">{"".join(tcard2(c, R) for c in sorted([c for c in T if T[c]["conf"] == conf], key=lambda c: S["seeds"][c]))}</div>' for conf in ("East", "West"))
body = f'''<section><p class="k">Standings · after {S['updated'].replace('after ', '')}</p><h1 class="h1">All 30 teams.</h1>
<p class="lead">In order by conference. Follow a team and it turns its colors here and everywhere on the site.</p>
<div class="tabs" data-tabs="conf" style="margin-top:18px"><button class="pill on" data-tab="East">East</button><button class="pill" data-tab="West">West</button></div></section>
<section>{panes}</section>'''
page("teams/index.html", "Teams · Box & Motion Hoops", body, active="Teams")

# ---- team pages ----
for c, t in T.items():
    R = "../../"
    nx = next_game(c)
    band = f'''<section class="band" style="background:radial-gradient(90% 140% at 85% 0%,{t['c1']} 0%,{t['dark']} 80%)"><div class="w">
<div class="between"><div><p class="k">{E(t['city'])} · {t['div']} division</p><h1 class="h1" style="font-size:clamp(56px,10vw,120px);margin-bottom:0">{E(t['name'])}</h1></div>
<button type="button" class="pill star" data-team="{c}" aria-pressed="false">★ <span class="lbl">Follow</span></button></div>
<div class="stats"><div><span class="n">{rec(c)}</span><br><span style="opacity:.8">{seed(c)}</span></div>
<a href="{R}odds/index.html"><span class="n">{O[c]['top6']}%</span><br><span style="opacity:.8">top-6 odds · {chg(O[c]['chg']) if O[c]['chg'] else 'no change'} this week →</span></a>
<div><span class="n">{O[c]['wins']}</span><br><span style="opacity:.8">projected wins</span></div>
{f'<div><span class="n" style="font-size:22px">Next</span><br><span style="opacity:.85">{E(nx)}</span></div>' if nx else ''}</div></div></section>'''
    cards = "".join(hf_card(g, R) for g in team_games(c))
    learn = [x for x in LEARN if (x[3].endswith("· " + t["name"]) or (c == "LAL" and "Luka" in x[2]))]
    for m in MOVES:
        if m["team"] == c and not any(x[4].endswith(m["slug"] + "/index.html") for x in learn):
            learn.append((m["published"], "move", m["title"], f"Signature move · {m['player']}", f'moves/{m["slug"]}/index.html', _thumb(m["anim"])))
    learn_html = ('<div class="lib">' + "".join(learn_card(R, x) for x in learn) + '</div>') if learn else f'<div class="card pad empty"><b>Moves and plays coming</b><p class="dim" style="margin:6px 0 0">When a {E(t["name"])} player or coach does something worth seeing again, we draw it. Follow the {E(t["name"])} to see it first.</p></div>'
    body = f'''<section><div class="shead"><div><p class="k">Every game · newest first</p><h2 class="h2">Games.</h2></div></div>
<div class="hfgrid">{cards or '<p class="dim">No games yet.</p>'}</div></section>
<section><div class="shead"><div><p class="k">Players and coach</p><h2 class="h2">Drawn.</h2></div></div>{learn_html}</section>'''
    page(f"teams/{t['slug']}/index.html", f"{t['city']} {t['name']} · Box & Motion Hoops", body, active="Teams",
         desc=f"{t['city']} {t['name']}: record, playoff odds, every game's story and the plays that decided them.", band=band)

# ---- odds ----
R = "../"
def otable(conf, hidden=False):
    rows = "".join(f'''<tr data-team="{c}" style="--team-grad:{grad(c)};--tc:{T[c]['c1']}"><td><a href="{R}teams/{T[c]['slug']}/index.html"><i class="dot" style="{dot2(c)}"></i><b>{E(T[c]['name'])}</b></a></td><td class="dim">{rec(c)}</td>
<td style="width:36%"><div class="bar"><span style="width:{O[c]['top6']}%"></span></div></td><td class="num"><b class="n" style="font-size:18px">{O[c]['top6']}%</b></td>
<td class="num hide-sm">{O[c]['top10']}%</td><td class="num hide-sm">{O[c]['wins']}</td><td class="num {chgcls(O[c]['chg'])}">{chg(O[c]['chg'])}</td></tr>''' for c in sorted([c for c in T if T[c]["conf"] == conf], key=lambda c: (-O[c]["top6"], -O[c]["top10"])))
    return f'<div class="tbox{" hidden" if hidden else ""}" data-pane="conf" data-value="{conf}"><div class="scroll"><table class="otable"><tr><th>Team</th><th>Record</th><th>Top-6 seed</th><th></th><th class="num hide-sm">Play-in+</th><th class="num hide-sm">Proj. wins</th><th class="num">This week</th></tr>{rows}</table></div></div>'
body = f'''<section><p class="k">Playoff odds · updated {S['updated']}</p><h1 class="h1">Who’s in, who’s sweating.</h1>
<p class="lead">Each team’s chance of a top-6 seed (a guaranteed playoff spot) and of the play-in or better. “This week” is the change since Monday morning. Your teams are in color.</p>
<div class="tabs" data-tabs="conf" style="margin-top:18px"><button class="pill on" data-tab="East">East</button><button class="pill" data-tab="West">West</button></div></section>
<section>{otable("East")}{otable("West", True)}</section>
<section class="card pad"><b>How the odds work</b><p class="dim" style="margin:6px 0 0">Each team starts from a projected win total and is updated with every result (the projection counts like 30 games, so early records move it but don't take over). We then simulate the rest of the 82-game season 20,000 times, with some uncertainty in every team's strength, and count how often each team finishes top six and top ten in its conference. This is model v0: it uses records only, not injuries, schedule strength or point differential.</p></section>'''
page("odds/index.html", "Playoff odds · Box & Motion Hoops", body, active="Odds")

# ---- Learn (the old Deep dives page lives on at /deep-dives/ too) ----
R = "../"
chips = "".join(f'<button type="button" class="chip{" on" if k == "all" else ""}" data-filter="{k}">{E(lbl)}</button>' for k, lbl in KINDS if k == "all" or any(x[1] == k for x in LEARN))
learn_body = lambda R: f'''<section><p class="k">Learn the game</p><h1 class="h1">See how the game works.</h1>
<p class="lead">Signature moves, set plays, coach’s boards, trends and scouting reports, drawn so you can actually see them.</p></section>
<section><div class="row" style="margin-bottom:18px">{chips}</div><div class="lib" data-lib>{"".join(learn_card(R, x) for x in LEARN)}</div></section>
{closer(R)}'''
page("learn/index.html", "Learn the game · Box & Motion Hoops", learn_body(R), active="Learn")
page("deep-dives/index.html", "Learn the game · Box & Motion Hoops", learn_body(R), active="Learn")

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
body = f'''{learn_crumbs(R, f'<a href="{R}teams/lakers/index.html">Lakers</a>', '<span>Luka Dončić</span>')}
<section style="display:flex;flex-wrap:wrap;gap:32px;align-items:flex-end"><div class="sec" style="flex:999 1 480px;gap:12px"><p class="k">Scouting report · games through Nov 6</p>
<h1 class="h1">Luka Dončić.</h1>
<p class="lead" style="font-size:20px;max-width:34em">The league's leading scorer. He makes defenses choose between the drive and the step-back, then punishes whichever they pick. He has scored 40 or more in six of his last seven games.</p>
<p class="dim" style="margin:0">No. 77 · Lakers · 6′8″ · 9th NBA season</p></div>
<div style="flex:1 1 280px;display:grid;grid-template-columns:1fr 1fr;gap:12px">
<div class="card pad"><span class="n" style="font-size:44px;color:#552583">{avg:.1f}</span><br><span class="dim">points per game</span></div>
<div class="card pad"><span class="n" style="font-size:44px">{len(pts)}</span><br><span class="dim">games played</span></div>
<div class="card pad"><span class="n" style="font-size:44px">53</span><br><span class="dim">season high</span></div>
<div class="card pad"><span class="n" style="font-size:44px">{rec('LAL')}</span><br><span class="dim">Lakers record</span></div></div></section>
<section class="sec"><div><p class="k">Signature move</p><h2 class="h2">The step-back three.</h2>
<p class="lead">He sells the drive with a hard jab, crosses the ball back between his legs to his left as he hops back off both feet, and rises before the defender recovers. At 6-foot-8 he releases over most guards, so a late contest rarely bothers the shot.</p></div>
{anim_frame(R, "luka-stepback.html", "Animated illustration of Luka Dončić's step-back three", "reels/soundtrack.mp3")}
<div class="row">{short_btn("5FgwWO0aF8s")}</div></section>
<section class="sec"><h2 class="h2">Game log.</h2>
<div class="tbox"><div class="scroll"><table class="otable" style="min-width:720px"><tr><th>Date</th><th>Game</th><th>Result</th><th class="num">Pts</th><th class="num">Reb</th><th class="num">Ast</th><th class="num">FG</th><th class="num">3PT</th><th class="num">TO</th><th>Flag</th></tr>{logrows}</table></div></div>
<p class="dim" style="margin:0;font-size:14px">Flags are automatic: any game 10 or more points from his season average ({avg:.1f}). Hot nights so far: {HOTS}. A dash means the stat isn't in our feed yet.</p></section>'''
page("players/luka-doncic/index.html", "Luka Dončić scouting report · Box & Motion Hoops", body, active="Learn",
     desc=f"Luka Dončić: {avg:.1f} points per game, game log, hot and quiet nights, and the step-back.")

# ---- player reports from data/players/<slug>.json (the weekly hot-player report) ----
for P in PLAYERS:
    c = P["team"]; t = T[c]
    stats = "".join(f'<div class="card pad"><span class="n" style="font-size:44px{";color:" + t["c1"] if i == 0 else ""}">{E(v)}</span><br><span class="dim">{E(l)}</span></div>' for i, (v, l) in enumerate(P["stats"]))
    logrows = "".join("<tr>" + "".join(f'<td{" class=num" if 3 <= j else ""}>{"<b>" + E(str(v)) + "</b>" if j == 3 else E("—" if v is None else str(v))}</td>' for j, v in enumerate(r)) + "</tr>" for r in P["log"])
    steps = "".join(f'<li><b>{E(a)}.</b> {E(b2)}</li>' for a, b2 in P["move"]["steps"])
    srcs = "".join(f'<li><a href="{E(u)}" target="_blank" rel="noopener">{E(l)}</a></li>' for l, u in P["sources"])
    body = f'''{learn_crumbs(R, f'<a href="{R}teams/{t["slug"]}/index.html">{E(t["name"])}</a>', f'<span>{E(P["name"])}</span>')}
<section style="display:flex;flex-wrap:wrap;gap:32px;align-items:flex-end"><div class="sec" style="flex:999 1 480px;gap:12px"><p class="k">Scouting report · {E(P['week'])}</p>
<h1 class="h1">{E(P['name'])}.</h1><p class="lead" style="font-size:20px">{E(P['lede'])}</p><p class="dim" style="margin:0">{E(P['bio'])}</p></div>
<div style="flex:1 1 280px;display:grid;grid-template-columns:1fr 1fr;gap:12px">{stats}</div></section>
<section class="sec"><div><p class="k">Signature move</p><h2 class="h2">{E(P['move']['title'])}.</h2><p class="lead">{E(P['move']['text'])}</p></div>
{anim_frame(R, P['move']['anim'], P['name'] + ': ' + P['move']['title'], "reels/soundtrack.mp3")}
<ol class="beats">{steps}</ol><div class="row">{short_btn(P["move"].get("youtube"))}</div></section>
<section class="sec"><h2 class="h2">His week.</h2>
<div class="tbox"><div class="scroll"><table class="otable" style="min-width:640px"><tr><th>Date</th><th>Game</th><th>Result</th><th class="num">Pts</th><th class="num">Reb</th><th class="num">Ast</th><th class="num">FG</th><th class="num">3PT</th></tr>{logrows}</table></div></div></section>
<section class="card pad"><b>Sources</b><ul style="margin:8px 0 0;padding-left:20px;display:flex;flex-direction:column;gap:4px">{srcs}</ul></section>'''
    page(f"players/{P['slug']}/index.html", f"{P['name']} scouting report · Box & Motion Hoops", body, active="Learn", desc=P["lede"])

# ---- signature moves ----
for m in MOVES:
    t = T[m["team"]]
    steps = "".join(f'<li><b>{E(a)}.</b> {E(b2)}</li>' for a, b2 in m["steps"])
    body = f'''{learn_crumbs(R, f'<a href="{R}teams/{t["slug"]}/index.html">{E(t["name"])}</a>', f'<span>{E(m["player"])}</span>')}
<section><p class="k">Signature move · {E(t['city'])} {E(t['name'])}{' · No. ' + E(m['number']) if m['number'] else ''}</p>
<h1 class="h1">{E(m['title'])}.</h1><p class="lead" style="font-size:20px">{E(m['dek'])}</p></section>
<section class="sec">{anim_frame(R, m['anim'], m['player'] + ': ' + m['title'], "reels/soundtrack.mp3")}
<ol class="beats">{steps}</ol>
<div class="row">{short_btn(m.get("youtube"))}<a class="pill" href="{R}teams/{t['slug']}/index.html">{E(t['name'])} page →</a></div></section>
{closer(R)}'''
    page(f"moves/{m['slug']}/index.html", f"{m['player']}: {m['title']} · Box & Motion Hoops", body, active="Learn", desc=m["dek"])

# ---- X's and O's explainers ----
for x in XO:
    body = f'''{learn_crumbs(R, "<span>X’s &amp; O’s</span>")}
<section><p class="k">X’s &amp; O’s · learn the game</p><h1 class="h1">{E(x['title'])}</h1><p class="lead" style="font-size:20px">{E(x['sub'])}.</p></section>
<section class="sec">{anim_frame(R, x['anim'], x['title'])}
<div class="row">{short_btn(x.get("youtube"))}<a class="pill" href="{R}learn/index.html">More to learn →</a></div></section>
{closer(R)}'''
    page(f"xo/{x['slug']}/index.html", f"{x['title']} · Box & Motion Hoops", body, active="Learn", desc=f"{x['title']} {x['sub']}, explained in motion.")

# ---- trend boards ----
for x in TRENDS:
    t = T[x["team"]]
    body = f'''{learn_crumbs(R, f'<a href="{R}teams/{t["slug"]}/index.html">{E(t["name"])}</a>', "<span>Trend board</span>")}
<section><p class="k">Trend board · good, lucky or in trouble?</p><h1 class="h1">{E(x['title'])}</h1><p class="lead" style="font-size:20px">{E(x['dek'])}</p></section>
<section class="sec" style="max-width:560px">{anim_frame(R, x['anim'], x['title'], "reels/soundtrack.mp3")}
<div class="row">{short_btn(x.get("youtube"))}<a class="pill" href="{R}teams/{t['slug']}/index.html">{E(t['name'])} page →</a></div></section>
{closer(R)}'''
    page(f"trends/{x['slug']}/index.html", f"{x['title']} · Box & Motion Hoops", body, active="Learn", desc=x["dek"])

# ---- coach: Redick ----
body = f'''{learn_crumbs(R, f'<a href="{R}teams/lakers/index.html">Lakers</a>', "<span>JJ Redick</span>")}
<section><p class="k">Coach’s board</p><h1 class="h1">JJ Redick.</h1>
<p class="lead">Lakers head coach since 2024. The Lakers are {rec('LAL')}, {seed('LAL')}.</p></section>
<section class="sec"><div><p class="k">From the games · Lakers at Jazz, Oct 25</p><h2 class="h2">How they closed at Utah.</h2>
<p class="lead">Down three with 4:17 left, the Lakers closed on a 19–7 run to win 132–123, with Luka Dončić scoring 52. Every possession of the finish, on the board.</p></div>
{anim_frame(R, "lakers-utah-close.html", "Whiteboard breakdown of the Lakers' last 4:17 at Utah", "audio/film-room.mp3")}</section>
{closer(R)}'''
page("coaches/jj-redick/index.html", "JJ Redick coach's board · Box & Motion Hoops", body, active="Learn")

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
    recap = short_btn(b.get("youtube")) + (f'<a class="pill" href="{R}games/{g["slug"]}/index.html">Game recap →</a>' if g else "")
    body = f'''{learn_crumbs(R, f'<a href="{R}teams/{t["slug"]}/index.html">{E(t["name"])}</a>', f'<span>{E(b["coach"])}</span>')}
<section><p class="k">Coach’s board · {E(t['city'])} {E(t['name'])}</p><h1 class="h1">{E(b['coach'])}.</h1>
<p class="lead">{E(t['name'])} head coach since {E(b['since'])}. The {E(t['name'])} are {rec(c)}, {seed(c)}.</p></section>
<section class="sec"><div><p class="k">{E(b['situation'])}</p><h2 class="h2">{E(b['title'])}.</h2><p class="lead">{E(b['dek'])}</p></div>
{anim_frame(R, b["anim"], b["coach"] + ": " + b["title"])}
<ol class="beats">{steps}</ol><div class="row">{recap}</div></section>
<section class="card pad"><b>Sources</b><p class="dim" style="margin:4px 0 8px">Every action on the board comes from these game stories. Where they don't say where a player stood, the spot is our illustration.</p><ul style="margin:0;padding-left:20px;display:flex;flex-direction:column;gap:4px">{srcs}</ul></section>
{f'<section class="sec"><h2 class="h2">Earlier boards.</h2><ul>{more}</ul></section>' if more else ''}'''
    page(f"coaches/{cslug}/index.html", f"{b['coach']}: {b['title']} · Box & Motion Hoops", body, active="Learn",
         desc=f"{b['coach']}'s {b['title'].lower()}: {b['dek']}")

# ---- newsletter ----
R = "../"
body = f'''<section class="closer" style="grid-template-columns:minmax(0,1fr)"><div><p class="k" style="color:rgba(255,255,255,.85)">The newsletter · free · every Sunday</p>
<h1 class="h1" style="color:#fff;margin-bottom:10px">The Sunday Box.</h1>
<p style="font-size:19px">The week in basketball, in one email you can read with your coffee: the games that mattered, the plays behind them, and what to watch next.</p>
<div class="ctas" style="margin-top:22px"><a class="pill wht" href="{NEWSLETTER}" target="_blank" rel="noopener">Subscribe free →</a></div>
<p style="font-size:14px;opacity:.85">Unsubscribe anytime.</p></div></section>
<section class="nums">
<div class="num"><div class="t"><span>01</span></div><div><b>The games that mattered</b><p>Not every score. The few that changed something, and why.</p></div></div>
<div class="num"><div class="t"><span>02</span></div><div><b>One play, drawn</b><p>The week’s best play as a drawing you can follow step by step.</p></div></div>
<div class="num"><div class="t"><span>03</span></div><div><b>The trend board</b><p>One team’s hot or cold start, checked against the numbers.</p></div></div>
<div class="num"><div class="t"><span>04</span></div><div><b>What to watch</b><p>The games worth your time this week, with what’s at stake.</p></div></div>
</section>'''
page("newsletter/index.html", "The Sunday Box newsletter · Box & Motion Hoops", body, active="Sunday Box")

# ---- about + 404 ----
body = f'''<section style="max-width:46em"><p class="k">About Box &amp; Motion</p>
<h1 class="h1">We want more out of our box scores.</h1>
<p class="lead" style="font-size:20px">A box score tells you who scored. It doesn’t tell you how the game was won: the run that flipped it, the matchup a coach kept going back to, the play drawn up out of a timeout.</p></section>
<section class="grid g2">
<div class="card pad" style="display:flex;flex-direction:column;gap:8px"><p class="k">Who we are</p><b class="d" style="font-size:30px">Fans with a day job in data</b>
<p style="margin:0">Our team has a background in analytics and AI enablement. We love basketball, and we don’t have time to watch every game anymore. We still want to know what actually happened.</p></div>
<div class="card pad" style="display:flex;flex-direction:column;gap:8px"><p class="k">What we make</p><b class="d" style="font-size:30px">The story of the game, in motion</b>
<p style="margin:0">Every game, told through the numbers and simple X’s and O’s: where it was won, who carried it, and the play that decided it, drawn so you can see it in about a minute.</p></div></section>
<section class="nums">
<a class="num" href="{R}last-night/index.html"><div class="t"><span>01</span><span>↗</span></div><div><b>Every game</b><p>The story, the play that decided it, and the official highlights.</p></div></a>
<a class="num" href="{R}odds/index.html"><div class="t"><span>02</span><span>↗</span></div><div><b>Playoff odds</b><p>Our own model, updated every morning.</p></div></a>
<a class="num" href="{R}learn/index.html"><div class="t"><span>03</span><span>↗</span></div><div><b>Learn the game</b><p>Moves, plays, coach’s boards and trends, drawn.</p></div></a>
<a class="num" href="{R}newsletter/index.html"><div class="t"><span>04</span><span>↗</span></div><div><b>The Sunday Box</b><p>The week in one email. Free.</p></div></a></section>
<section style="max-width:46em" class="sec"><h2 class="h2">How we make it.</h2>
<p style="margin:0">Scores and records come from league stats, and every number in a recap is checked against the box score or a named game story. The plays are original illustrations drawn from written accounts, not traced from footage and not to scale. We use AI tools to help draw and publish it all, and we skip anything we can’t verify rather than guess.</p>
<p class="dim" style="margin:0">Box &amp; Motion is unofficial fan coverage and is not affiliated with the NBA or any team. Team names are used to identify teams; we don’t use team logos. Official video plays from the league’s own uploads; we never re-upload it.</p>
<p style="margin:0">Contact: <a href="mailto:boxandmotionhoops@gmail.com">boxandmotionhoops@gmail.com</a></p></section>'''
page("about/index.html", "About · Box & Motion Hoops", body, active="About", desc="We want more out of our box scores: every NBA game, told through the numbers and simple X’s and O’s, in motion.")
page("404.html", "Not found · Box & Motion Hoops", '<section><h1 class="h1">Air ball.</h1><p class="lead">That page doesn\'t exist. <a href="/">Back to the home page</a>.</p></section>')

n = sum(len(fs) for _, _, fs in os.walk(OUT))
print("built", n, "files")
