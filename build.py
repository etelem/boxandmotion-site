"""Build the Box & Motion Hoops static site from data/*.json into dist/."""
import json, os, shutil, datetime
from html import escape as E
from urllib.parse import quote_plus

T = json.load(open("data/teams.json"))
S = json.load(open("data/season.json"))
O = json.load(open("data/odds.json"))
NEWSLETTER = "https://elans-newsletter-ae8074.beehiiv.com/subscribe"
OUT = "dist"
WEEKDAY = lambda d: datetime.date.fromisoformat(d).strftime("%a, %b %-d")
CONFNAME = {"East": "East", "West": "West"}

def ordinal(n): return f"{n}{'th' if 11<=n%100<=13 else {1:'st',2:'nd',3:'rd'}.get(n%10,'th')}"
def rec(c): w, l = S["standings"][c]; return f"{w}–{l}"
def seed(c): return f"{ordinal(S['seeds'][c])} in the {T[c]['conf']}"
def chg(n): return "—" if n == 0 else (f"+{n}" if n > 0 else f"−{abs(n)}")
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

def page(path, title, body, active=None, desc="Every NBA game, explained in animation. Recaps, playoff odds and scouting reports.", band=""):
    depth = path.count("/"); R = "../" * depth
    nav = [("Teams", "teams/index.html"), ("Last Night", "last-night/index.html"), ("Deep Dives", "deep-dives/index.html"), ("Playoff Odds", "odds/index.html"), ("Newsletter", "newsletter/index.html")]
    links = "".join(f'<a href="{R}{h}"{" aria-current=page" if n==active else ""}>{n}</a>' for n, h in nav)
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
<a href="{R}teams/index.html" class="pill hot favcount">★ My teams</a>
</nav></header>
{band}
<main class="w">{body}</main>
<footer class="w"><span><b>The box score, in motion.</b> Box &amp; Motion Hoops · unofficial fan coverage, not affiliated with the NBA or any team.</span>
<span>Updated {S['updated']}. Video links go to official uploads only. <a href="{R}about/index.html">About</a></span></footer>
</div><script src="{R}assets/data.js"></script><script src="{R}assets/site.js"></script></body></html>"""
    full = os.path.join(OUT, path); os.makedirs(os.path.dirname(full) or OUT, exist_ok=True)
    open(full, "w").write(html)
    return R

def rel(depth): return "../" * depth

# ---- reusable bits ----
def game_card(g, R, show_mine=True):
    w, l = g["win"], g["lose"]
    wt = T[w]
    lines = ""
    for c, sc in ((g["away"], g["as_"]), (g["home"], g["hs"])):
        lines += f'<div class="sline {"win" if c==w else "lose"}"><span>{E(T[c]["name"])} <span class="dim" style="font-size:13px;font-weight:500">{g["rec"][c]}</span></span><span>{sc}</span></div>'
    tag = '<span class="tag gold">▶ Recap video</span>' if (g["video"] or g["reel"]) else ('<span class="tag gold">Featured recap</span>' if g["featured"] else "")
    return f'''<div class="card gcard" data-teams="{g['away']} {g['home']}">
<a class="gtop" href="{R}games/{g['slug']}/index.html" style="background:radial-gradient(120% 140% at 100% 0%,{wt['c1']} 0%,{wt['dark']} 75%)">
<span class="k">Final{' · OT' if g['ot'] else ''} · {WEEKDAY(g['date'])}</span><span class="d" style="font-size:30px">{E(wt['name'])} {max(g['as_'],g['hs'])}–{min(g['as_'],g['hs'])}</span></a>
<div class="gbody"><div class="row" style="gap:6px">{'<span class="tag hot mine-tag hidden">Your team</span>' if show_mine else ''}{tag}</div>{lines}
<div class="row" style="gap:8px;margin-top:6px"><a class="pill on sm" href="{R}games/{g['slug']}/index.html">{'▶ Watch recap' if (g['video'] or g['reel']) else 'Recap'}</a><a class="pill sm" href="{yt(g)}" target="_blank" rel="noopener">▶ Highlights</a></div></div></div>'''

def star_btn(c, big=False, light=False):
    style = f"border-color:{T[c]['c2']};color:#fff" if light else ""
    return f'<button type="button" class="pill star{" " if big else " sm "}" data-team="{c}" aria-pressed="false" style="{style}">★ <span class="lbl">Follow</span></button>'

def team_band(c, kicker, extra=""):
    t = T[c]
    return f'<section class="band" style="background:radial-gradient(90% 140% at 85% 0%,{t["c1"]} 0%,{t["dark"]} 80%)"><div class="w">{kicker}{extra}</div></section>'

# ---- data.js for client ----
shutil.rmtree(OUT, ignore_errors=True)  # start clean so removed pages disappear
if os.path.isdir("reels"): shutil.copytree("reels", f"{OUT}/reels")
os.makedirs(f"{OUT}/assets", exist_ok=True)
client = {"teams": {c: {"name": T[c]["name"], "slug": T[c]["slug"], "c1": T[c]["c1"], "c2": T[c]["c2"], "dark": T[c]["dark"],
          "rec": rec(c), "seed": seed(c), "top6": O[c]["top6"], "chg": chg(O[c]["chg"]), "last": last_line(c)} for c in T}}
open(f"{OUT}/assets/data.js", "w").write("window.BM=" + json.dumps(client, ensure_ascii=False) + ";")
shutil.copy("src/site.css", f"{OUT}/assets/site.css"); shutil.copy("src/site.js", f"{OUT}/assets/site.js")

# ---- home ----
R = ""
movers = sorted(T, key=lambda c: -abs(O[c]["chg"]))[:1][0]
_gk = S.get("gotw") or max(S["featured"])
gotw = next(g for g in GAMES if g["key"] == _gk)
fz = S["featured"][gotw["key"]]
risers = sorted(T, key=lambda c: -O[c]["chg"])[:3]; fallers = sorted(T, key=lambda c: O[c]["chg"])[:3]
def mini(c): return f'<a href="{R}teams/{T[c]["slug"]}/index.html" style="display:flex;justify-content:space-between;padding:10px 0;border-top:1px solid var(--line);text-decoration:none"><span><b>{E(T[c]["name"])}</b> <span class="dim">{rec(c)}</span></span><span><b>{O[c]["top6"]}%</b> <span class="{chgcls(O[c]["chg"])}">{chg(O[c]["chg"])}</span></span></a>'
home = f'''
<section class="tagline"><h1 class="d">The box score, <span class="grad">in motion.</span></h1><p>Every NBA game, explained in animation.</p></section>
<section class="sec">
 <div class="between"><div class="sec" style="gap:8px"><p class="k">Your teams · tap ★ on any team to follow</p><h2 class="h1" id="greet">Good morning.</h2></div>
 <div class="row" style="gap:12px">
  <a class="chip" href="last-night/index.html"><span class="dot"></span>{len(LAST)} games last night</a>
  <a class="chip" href="odds/index.html"><span class="dot"></span>Biggest mover: {E(T[movers]['name'])} {chg(O[movers]['chg'])}</a>
  <a class="chip" href="players/luka-doncic/index.html"><span class="dot"></span>New: Luka scouting report</a>
 </div></div>
 <div id="mine" class="grid g3"></div>
 <div id="mine-empty" class="card pad empty hidden"><b class="d" style="font-size:26px">Pick your teams</b><p class="dim" style="margin:6px 0 14px">Follow teams to see their record, odds and last game here. Saved on this device, no sign-up.</p><div class="row"><button class="pill star" data-team="LAL">★ Lakers</button><button class="pill star" data-team="PHI">★ 76ers</button><button class="pill star" data-team="NYK">★ Knicks</button><a class="pill" href="teams/index.html">All 30 teams →</a></div></div>
</section>
<section class="sec">
 <div class="between"><div class="sec" style="gap:6px"><p class="k">{WEEKDAY(LAST_DATE)}</p><h2 class="h2">Last night</h2></div>
 <div class="tabs"><button class="pill" data-mode="mine">Your teams</button><button class="pill" data-mode="all">All {len(LAST)} games</button></div></div>
 <div class="grid g3" data-games>{"".join(game_card(g, R) for g in LAST)}</div>
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
  <a href="players/luka-doncic/index.html" class="card pad" style="display:flex;flex-direction:column;gap:6px;background:radial-gradient(120% 140% at 100% 0%,#552583 0%,#1c0b32 75%);color:#fff;border:0"><span class="tag gold">Scouting report</span><b class="d" style="font-size:30px;margin-top:4px">Luka Dončić: 40 a night</b><span style="opacity:.85">Game log, hot and quiet nights, the step-back</span></a>
  <a href="coaches/jj-redick/index.html" class="card pad" style="display:flex;flex-direction:column;gap:6px"><span class="tag">Coach's whiteboard</span><b class="d" style="font-size:30px;margin-top:4px">JJ Redick: how they close</b><span class="dim">The Utah comeback, on the board</span></a>
 </div>
</section>
<section class="card cta"><div><p class="k">Free · every Sunday</p><b class="d" style="font-size:clamp(30px,5vw,40px)">The Sunday Box</b><p style="margin:6px 0 0;color:#d5d6d9">The week's best game, playoff odds movers and one deep dive, in four minutes.</p></div>
<a class="pill hot" href="{NEWSLETTER}" target="_blank" rel="noopener">Subscribe free</a></section>
'''
page("index.html", "Box & Motion Hoops: the box score, in motion", home)

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
    if c == "LAL":
        players = f'<a href="{R}players/luka-doncic/index.html" class="card pad" style="display:flex;flex-direction:column;gap:6px;min-height:200px;justify-content:flex-end;background:radial-gradient(120% 140% at 100% 0%,#552583 0%,#1c0b32 75%);color:#fff;border:0"><span class="tag gold">Scouting report</span><b class="d" style="font-size:30px">Luka Dončić</b><span style="opacity:.85">No. 77 · 40.1 points per game</span></a><div class="card pad empty" style="min-height:200px;display:flex;flex-direction:column;justify-content:flex-end"><b class="d" style="font-size:26px">Austin Reaves</b><span class="dim">Report coming</span></div><div class="card pad empty" style="min-height:200px;display:flex;flex-direction:column;justify-content:flex-end"><b class="d" style="font-size:26px">Walker Kessler</b><span class="dim">Report coming</span></div>'
        coach = f'<a href="{R}coaches/jj-redick/index.html" class="card pad" style="display:flex;flex-direction:column;gap:8px"><span class="tag">Coach\'s whiteboard</span><b class="d" style="font-size:40px">JJ Redick</b><span class="dim" style="font-size:18px">Head coach since 2024. How the Lakers closed at Utah, on the board.</span><span style="font-weight:600">Open the whiteboard →</span></a>'
    else:
        players = f'<div class="card pad empty"><b class="d" style="font-size:26px">Scouting reports are coming</b><p class="dim" style="margin:6px 0 0">We publish one player report a week, rotating through all 30 teams. Follow the {E(t["name"])} to see theirs here first.</p></div>'
        coach = f'<div class="card pad empty"><b class="d" style="font-size:26px">Whiteboard coming</b><p class="dim" style="margin:6px 0 0">Coach whiteboards rotate through the league, one every week or two. Every set is backed by a cited source.</p></div>'
    body = f'''<div class="tabs" data-tabs="team"><button class="pill on" data-tab="games">Games</button><button class="pill" data-tab="players">Players</button><button class="pill" data-tab="coach">Coach</button></div>
<section class="sec" data-pane="team" data-value="games"><p class="k">Newest first · coverage starts Mon, Nov 2</p>{rows or '<p class="dim">No games yet this week.</p>'}</section>
<section class="grid g3 hidden" data-pane="team" data-value="players">{players}</section>
<section class="hidden" data-pane="team" data-value="coach">{coach}</section>'''
    page(f"teams/{t['slug']}/index.html", f"{t['city']} {t['name']} · Box & Motion Hoops", body, active="Teams",
         desc=f"{t['city']} {t['name']}: record, playoff odds, game recaps and scouting reports.", band=band)

# ---- game pages ----
for g in GAMES:
    R = "../../"
    a, h, w, l = g["away"], g["home"], g["win"], g["lose"]
    city = T[h]["city"]
    ls = S["linescores"].get(g["key"])
    lsh = ""
    if ls:
        def tr(c, q, tot): return f'<tr><th>{E(T[c]["name"])}</th>' + "".join(f"<td>{x}</td>" for x in q) + f'<td><b>{tot}</b></td></tr>'
        lsh = f'<div class="scroll"><table class="lines"><tr class="k"><th></th><th>Q1</th><th>Q2</th><th>Q3</th><th>Q4</th><th>Final</th></tr>{tr(a, ls["away"], g["as_"])}{tr(h, ls["home"], g["hs"])}</table></div>'
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
    if v:
        # the recap video leads the page: video first, score and story beside it
        hero = f'''<section style="display:flex;flex-wrap:wrap;gap:28px;align-items:flex-start">
<div style="flex:0 1 360px;width:100%;max-width:360px;aspect-ratio:9/16;border-radius:18px;overflow:hidden;background:#111214;box-shadow:0 10px 30px rgba(17,18,20,.18)">
<iframe src="https://www.youtube.com/embed/{v}" title="Box &amp; Motion recap: {E(T[a]['name'])} at {E(T[h]['name'])}" style="width:100%;height:100%;border:0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe></div>
<div class="sec" style="flex:1 1 320px;gap:16px"><span class="tag gold" style="align-self:flex-start">▶ Our recap video · 66 seconds</span>{kicker}
<h1 class="h1" style="display:flex;flex-wrap:wrap;gap:4px 24px;font-size:clamp(40px,6vw,72px)">{names}</h1>
{lede}{lsh}<a class="pill" style="align-self:flex-start" href="https://youtube.com/shorts/{v}" target="_blank" rel="noopener">▶ Watch on YouTube</a></div></section>'''
    elif g["reel"]:
        # our drawn recap reel, hosted on this site, leads the page
        hero = f'''<section style="display:flex;flex-wrap:wrap;gap:28px;align-items:flex-start">
<div style="flex:0 1 360px;width:100%;max-width:360px;aspect-ratio:9/14.4;border-radius:18px;overflow:hidden;background:#111214;box-shadow:0 10px 30px rgba(17,18,20,.18)">
<iframe src="{R}reels/{g['key']}/index.html?embed=1" title="Box &amp; Motion recap: {E(T[a]['name'])} at {E(T[h]['name'])}" style="width:100%;height:100%;border:0" allow="autoplay"></iframe></div>
<div class="sec" style="flex:1 1 320px;gap:16px"><span class="tag gold" style="align-self:flex-start">▶ Our recap · 66 seconds</span>{kicker}
<h1 class="h1" style="display:flex;flex-wrap:wrap;gap:4px 24px;font-size:clamp(40px,6vw,72px)">{names}</h1>
{lede}{lsh}<a class="pill" style="align-self:flex-start" href="{R}reels/{g['key']}/index.html" target="_blank" rel="noopener">Open full screen, with sound</a></div></section>'''
    else:
        hero = f'''<section class="sec" style="gap:18px">{kicker}
<h1 class="h1" style="display:flex;flex-wrap:wrap;gap:4px 28px;font-size:clamp(48px,8vw,100px)">{names}</h1>
{lede}{lsh}</section>'''
    if f and not v and not g["reel"]:
        feat += video_block(None)
    body = f'''{crumbs}
{hero}
<section class="sec"><div class="sec" style="gap:6px"><h2 class="h2">Official video</h2><p class="dim" style="margin:0">We link to the official uploads on YouTube. We don't host or edit them.</p></div>
<div class="row"><a class="pill on" href="{yt(g)}" target="_blank" rel="noopener">▶ Game highlights on the NBA's channel</a></div></section>
{feat}
<section class="card cta"><div style="display:flex;flex-wrap:wrap;gap:20px;flex:1 1 400px"><div style="flex-basis:100%"><p class="k">What it meant</p></div>{meant}</div>
<a class="pill hot" href="{R}odds/index.html">All playoff odds</a></section>'''
    page(f"games/{g['slug']}/index.html", f"{T[a]['name']} {g['as_']}, {T[h]['name']} {g['hs']} · Box & Motion Hoops", body, active="Last Night",
         desc=(f["dek"] if f else auto))

# ---- last night ----
R = "../"
earlier = sorted({g["date"] for g in GAMES if g["date"] != LAST_DATE and g["date"] >= WEEK_START}, reverse=True)
ear = "".join(f'<section class="sec"><p class="k">{WEEKDAY(d)}</p><div class="grid g3" data-games>{"".join(game_card(g, R) for g in GAMES if g["date"]==d)}</div></section>' for d in earlier)
body = f'''<div class="between"><div class="sec" style="gap:8px"><p class="k">{WEEKDAY(LAST_DATE)} · {len(LAST)} games</p><h1 class="h1">Last night</h1></div>
<div class="tabs"><button class="pill" data-mode="mine">Your teams</button><button class="pill" data-mode="all">All games</button></div></div>
<section class="sec"><div class="grid g3" data-games>{"".join(game_card(g, R) for g in LAST)}</div><p class="dim none-note hidden" style="margin:0">None of your teams played last night. <button class="pill sm" data-mode="all">Show all games</button></p></section>
<h2 class="h2">Earlier this week</h2>{ear}'''
page("last-night/index.html", "Last night · Box & Motion Hoops", body, active="Last Night")

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
body = f'''<div class="sec" style="gap:8px"><p class="k">Every week or two</p><h1 class="h1">Deep dives</h1><p class="dim" style="margin:0;font-size:18px;max-width:44em">Player scouting reports and coach whiteboards, rotating through all 30 teams.</p></div>
<section class="grid g2">
<a href="{R}players/luka-doncic/index.html" class="card pad" style="min-height:260px;display:flex;flex-direction:column;justify-content:flex-end;gap:6px;background:radial-gradient(120% 140% at 100% 0%,#552583 0%,#1c0b32 75%);color:#fff;border:0"><span class="tag gold">Scouting report · Lakers</span><b class="d" style="font-size:40px">Luka Dončić</b><span style="opacity:.85">40.1 points a game, the hot and quiet nights, and the step-back</span></a>
<a href="{R}coaches/jj-redick/index.html" class="card pad" style="min-height:260px;display:flex;flex-direction:column;justify-content:flex-end;gap:6px"><span class="tag">Coach's whiteboard · Lakers</span><b class="d" style="font-size:40px">JJ Redick</b><span class="dim">How the Lakers closed out the Utah comeback</span></a>
<div class="card pad empty" style="min-height:200px;display:flex;flex-direction:column;justify-content:flex-end"><span class="tag ghost">Up next</span><b class="d" style="font-size:30px;margin-top:6px">Victor Wembanyama</b><span class="dim">Scouting report in progress</span></div>
</section>'''
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
<p style="margin:0;max-width:44em">He sells the drive with a hard jab, hops back off both feet, and rises before the defender recovers. At 6-8 he releases over most guards, so a late contest rarely bothers the shot.</p></div>
<div class="grid g3"><div class="card pad step"><span class="num-badge">1</span><b class="d" style="font-size:24px">The jab</b><span class="dim">The defender has to respect the drive.</span></div>
<div class="card pad step"><span class="num-badge">2</span><b class="d" style="font-size:24px">The hop back</b><span class="dim">Both feet, landing already set.</span></div>
<div class="card pad step"><span class="num-badge">3</span><b class="d" style="font-size:24px">The rise</b><span class="dim">A high release over the closeout.</span></div></div></section>
<section class="sec"><h2 class="h2">Game log</h2>
<div class="card" style="padding:6px 16px"><div class="scroll"><table class="otable" style="min-width:720px"><tr><th>Date</th><th>Game</th><th>Result</th><th class="num">Pts</th><th class="num">Reb</th><th class="num">Ast</th><th class="num">FG</th><th class="num">3PT</th><th class="num">TO</th><th>Flag</th></tr>{logrows}</table></div></div>
<p class="dim" style="margin:0;font-size:14px">Flags are automatic: any game 10 or more points from his season average ({avg:.1f}). Hot nights so far: {HOTS}. A dash means the stat isn't in our feed yet.</p></section>
<section class="card pad empty"><b>Season shot chart</b><p class="dim" style="margin:6px 0 0">The filterable shot chart (every shot, by game) arrives once our licensed shot-location feed is connected.</p></section>'''
page("players/luka-doncic/index.html", "Luka Dončić scouting report · Box & Motion Hoops", body, active="Deep Dives",
     desc=f"Luka Dončić: {avg:.1f} points per game, game log, hot and quiet nights, and the step-back.")

# ---- coach: Redick ----
body = f'''<nav aria-label="Breadcrumb" class="crumbs"><a href="{R}deep-dives/index.html">Deep dives</a><span>/</span><a href="{R}teams/lakers/index.html">Lakers</a><span>/</span><span>JJ Redick</span></nav>
<section class="sec" style="gap:12px"><p class="k">Coach's whiteboard · updated every few weeks</p><h1 class="h1" style="font-size:clamp(64px,10vw,120px)">JJ Redick</h1>
<p class="dim" style="margin:0;font-size:18px">Lakers head coach since 2024. The Lakers are {rec('LAL')}, {seed('LAL')}.</p></section>
<section class="card" style="overflow:hidden;display:flex;flex-wrap:wrap">
<div style="flex:1 1 360px;min-height:280px;background:#f6f6f2;display:flex;align-items:center;justify-content:center;padding:24px">
<svg viewBox="0 0 300 220" width="100%" style="max-width:380px" aria-label="Whiteboard sketch of a half court"><rect x="10" y="10" width="280" height="200" rx="8" fill="none" stroke="#111214" stroke-width="3"/><rect x="105" y="10" width="90" height="110" fill="none" stroke="#111214" stroke-width="3"/><circle cx="150" cy="120" r="30" fill="none" stroke="#111214" stroke-width="3"/><path d="M30 10 V70 A120 120 0 0 0 270 70 V10" fill="none" stroke="#111214" stroke-width="3"/><circle cx="150" cy="28" r="7" fill="none" stroke="#FF5A1F" stroke-width="3"/>
<text x="140" y="175" font-family="Archivo" font-weight="800" font-size="22" fill="#111214">1</text><path d="M150 168 C 175 150, 200 120, 215 95" fill="none" stroke="#FF5A1F" stroke-width="3" stroke-dasharray="6 6"/><text x="222" y="92" font-family="Archivo" font-weight="800" font-size="22" fill="#111214">5</text><path d="M230 100 L 175 60" fill="none" stroke="#111214" stroke-width="3" marker-end="url(#ar)"/><defs><marker id="ar" markerWidth="8" markerHeight="8" refX="6" refY="4" orient="auto"><path d="M0 0 L8 4 L0 8 z" fill="#111214"/></marker></defs></svg></div>
<div style="flex:1 1 360px;padding:28px;display:flex;flex-direction:column;gap:12px;justify-content:center"><span class="tag">From the games</span><b class="d" style="font-size:40px">How they closed at Utah</b>
<p style="margin:0;font-size:18px">Down three with 4:17 left on Oct 25, the Lakers closed on a 19–7 run to win 132–123, with Luka Dončić scoring 52.</p>
<a class="pill" style="align-self:flex-start" href="https://www.youtube.com/@boxandmotion" target="_blank" rel="noopener">▶ Watch on @boxandmotion</a></div></section>
<section class="sec"><div class="sec" style="gap:6px"><h2 class="h2">What he likes to run</h2><p class="dim" style="margin:0;max-width:46em">Each set gets drawn on the board and backed by a source: his own interviews or film from this season's games. Nothing goes up without one.</p></div>
<div class="grid g3"><div class="card pad empty"><span class="tag ghost">Go-to set</span><p class="dim" style="margin:10px 0 0">Being drawn</p></div><div class="card pad empty"><span class="tag ghost">After a timeout</span><p class="dim" style="margin:10px 0 0">Being drawn</p></div><div class="card pad empty"><span class="tag ghost">Defense</span><p class="dim" style="margin:10px 0 0">Being drawn</p></div></div></section>'''
page("coaches/jj-redick/index.html", "JJ Redick coach's whiteboard · Box & Motion Hoops", body, active="Deep Dives")

# ---- newsletter ----
R = "../"
body = f'''<section style="display:flex;flex-wrap:wrap;gap:32px;align-items:center"><div class="sec" style="flex:1 1 420px;gap:12px"><p class="k">Free · every Sunday</p><h1 class="h1">The Sunday Box</h1>
<p style="margin:0;font-size:20px;max-width:32em">The week in four minutes: the game of the week, the playoff odds movers, one deep dive and the games to watch.</p>
<div class="row"><a class="pill hot" href="{NEWSLETTER}" target="_blank" rel="noopener">Subscribe free</a><span class="dim">Unsubscribe anytime.</span></div></div>
<div class="card pad" style="flex:1 1 320px;display:flex;flex-direction:column;gap:10px"><p class="k">This week's issue</p><b class="d" style="font-size:30px">Two 50-point nights</b>
<ol style="margin:0;padding-left:20px;display:flex;flex-direction:column;gap:6px"><li>The week in one line</li><li>Game of the week: Spurs 112, Mavericks 111</li><li>Playoff race movers</li><li>Deep dive: Luka Dončić</li><li>Games to watch this week</li></ol></div></section>'''
page("newsletter/index.html", "The Sunday Box newsletter · Box & Motion Hoops", body, active="Newsletter")

# ---- about + 404 ----
body = f'''<div class="sec" style="gap:12px;max-width:44em"><h1 class="h1">About</h1><p style="font-size:18px;margin:0">Box &amp; Motion explains every NBA game in animation: a recap for every game, nightly playoff odds, and scouting reports and coach whiteboards every week or two.</p>
<p class="dim" style="margin:0">Box &amp; Motion is unofficial fan coverage and is not affiliated with the NBA or any team. Team names are used to identify teams. We link to official video uploads and never re-upload them. Scores and records come from a league stats feed; odds come from our own model.</p>
<p style="margin:0">Contact: <a href="mailto:boxandmotionhoops@gmail.com">boxandmotionhoops@gmail.com</a></p></div>'''
page("about/index.html", "About · Box & Motion Hoops", body)
page("404.html", "Not found · Box & Motion Hoops", '<div class="sec"><h1 class="h1">Air ball.</h1><p class="dim" style="font-size:18px;margin:0">That page doesn\'t exist. <a href="/">Back to the home page</a>.</p></div>')

n = sum(len(fs) for _, _, fs in os.walk(OUT))
print("built", n, "files")
