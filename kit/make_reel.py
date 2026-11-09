"""Box & Motion Hoops: build the drawn ~66s game-recap reel from a game config.
Usage: python3 make_reel.py configs/<game>.json out/<name>-reel.html
The config holds the D data block, the play-of-the-game settings, the text substitutions, aria label, notes and
(optionally) a palette. See configs/ for two complete, checked examples (Sixers and Lakers, Nov 2, 2026)."""
import sys, json, os, re
HERE = os.path.dirname(os.path.abspath(__file__))
FIGURE_REAL = open(os.path.join(HERE, 'figure-real.js')).read()
sys.path.insert(0, HERE)
from looks import look_for, kit_for, kit_css, LOOK_KEYS
TEAMS_JSON = os.path.join(HERE, '..', 'data', 'teams.json')

def _rgb(h): h = h.lstrip('#'); return [int(h[i:i + 2], 16) for i in (0, 2, 4)]
def _hex(c): return '#' + ''.join(f'{max(0, min(255, round(v))):02x}' for v in c)
def _mix(a, b, t): A, B = _rgb(a), _rgb(b); return _hex([x + (y - x) * t for x, y in zip(A, B)])
def _lum(h): r, g, b = [v / 255 for v in _rgb(h)]; return 0.2126 * r + 0.7152 * g + 0.0722 * b

def team_palette(code):
    """A reel palette in a team's colors (from the site's data/teams.json). No logos, colors only."""
    t = json.load(open(TEAMS_JSON))[code]
    c1, c2, dark = t['c1'], t['c2'], t['dark']
    navy = _mix(dark, '#000000', 0.35)
    lift = c1 if _lum(c1) < 0.25 else _mix(navy, c1, 0.28)
    mid = _mix(navy, lift, 0.45)
    blue = next((c for c in (c1, c2) if _lum(c) > 0.3), _mix(c1, '#ffffff', 0.45))
    bt = _mix(blue, '#ffffff', 0.3)
    muted = _mix('#b0b3b9', blue, 0.15)
    silver = _mix(muted, '#ffffff', 0.25)
    r, g, b = _rgb(blue)
    return (f"  --navy:{navy};--navy-mid:{mid};--navy-lift:{lift};\n"
            f"  --ink:#f7f8f9;--muted:{muted};--blue:{blue};--blue-text:{bt};--red:#ff5a1f;--red-text:#ff8a5c;--silver:{silver};\n"
            f"  --hairline:rgba({r},{g},{b},.24);--track:rgba({r},{g},{b},.16);")

EMBED_CSS = """html.embed body{background:transparent}
html.embed .wrap{padding:0;gap:.5rem;max-width:none}
html.embed .page-title,html.embed .chips,html.embed .own,html.embed .still-note,html.embed .notes{display:none}
html.embed .stage{border-radius:0;border:0}
html.embed .transport{padding:0 10px 8px}
/* embedded on a game page: fill the frame exactly, never scroll inside it */
html.embed,html.embed body{height:100%;margin:0;overflow:hidden;overscroll-behavior:none}
html.embed .wrap{height:100%;box-sizing:border-box}
html.embed .stage,html.embed .stage.tall{flex:1 1 0;min-height:0;aspect-ratio:auto;width:100%}
html.embed .transport{flex:none}
"""
EMBED_JS = '<script>if (/[?&]embed=1/.test(location.search)) document.documentElement.classList.add("embed");</script>\n'

SRC = open(os.path.join(HERE, 'base-reel.html')).read()
DAME = open(os.path.join(HERE, 'play-base.js')).read()

def mkplay(c):
    p = DAME
    def r(a, b):
        nonlocal p
        assert p.count(a) == 1, (p.count(a), a[:80]); p = p.replace(a, b)
    r("  // Play of the game: Damian Lillard's sidestep three with 43 seconds left that put Portland up six.", "  // Play of the game: " + c['comment'])
    r("'Dame Time'", repr(c['head']))
    r("P ? 'The dagger, 43 seconds left' : 'The dagger, with 43 seconds left'", f"P ? {c['subP']!r} : {c['subL']!r}")
    r("'Blazers +3', 'b w', 26)", f"{c['m0']!r}, 'b w', 26)")
    r("sUs.textContent = made ? 'Blazers +6' : 'Blazers +3';", f"sUs.textContent = made ? {c['m1']!r} : {c['m0']!r};")
    r("T(board, bx + 306, by + 76, '48.0', 'd', 46, 'end');", "T(board, bx + 306, by + 76, '', 'd', 46, 'end');")
    r("'48.0', 'd', P ? 230 : 300, 'middle');", "'', 'd', P ? 230 : 300, 'middle');")
    r("const ghost = figure(g, 'opp', k, '0');", f"const ghost = figure(g, 'phi', k, {c['num']!r});")
    r("const defender = figure(g, 'phi', k);", "const defender = figure(g, 'opp', k);")
    r("const shooter = figure(g, 'opp', k, '0');", f"const shooter = figure(g, 'phi', k, {c['num']!r});")
    r("T(caption, M, capY, 'Blazers by 6, 43 seconds left.', 'b w', fs.b);", f"T(caption, M, capY, {c['cap1']!r}, 'b w', fs.b);")
    r("T(caption, M, capY + fs.s * 1.5, 'The Lakers couldn’t recover.', 'b m', fs.s);", f"T(caption, M, capY + fs.s * 1.5, {c['cap2']!r}, 'b m', fs.s);")
    r("T(caption, M, capY + fs.s * 1.6, 'Blazers by 6 with 43 seconds left. The Lakers couldn’t recover.', 'b w', fs.b);", f"T(caption, M, capY + fs.s * 1.6, {(c['cap1'][:-1] + '. ' + c['cap2'])!r}, 'b w', fs.b);")
    # pull-up instead of a step-back: dribble into the shot, defender sags then closes out
    r("""      if (lt < T_STEP) return startX + 30 * k * prog(lt, T_JAB, 0.4);
      return lerp(startX + 30 * k, shotX, prog(lt, T_STEP, 0.45));""",
      """      return lerp(startX, shotX, prog(lt, T_JAB, 1.2));""")
    r("const shotX = hoopX - (P ? 500 : 600) * k, startX = shotX + 90 * k;", "const shotX = hoopX - (P ? 500 : 600) * k, startX = shotX - 90 * k;")
    r("const defX = (lt) => lerp(startX + 150 * k, startX + 120 * k, prog(lt, T_JAB, 0.4)) + (lt > T_STEP + 0.3 ? -70 * k * prog(lt, T_STEP + 0.3, 0.9) : 0);",
      "const defX = (lt) => lerp(shotX + 200 * k, shotX + 145 * k, prog(lt, T_JAB, 1.4));")
    r("ghost.g.style.opacity = lt > T_STEP && lt < T_MAKE ? (0.28 * (1 - prog(lt, T_STEP + 1.2, 1.5))).toFixed(2) : 0;", "ghost.g.style.opacity = 0;")
    r("space.style.opacity = showSpace ? Math.min(prog(lt, T_STEP + 0.2, 0.3), 1 - prog(lt, T_REL + 0.2, 0.4)) : 0;", "space.style.opacity = 0;")
    C0, C1 = c['clock']
    r("const clk = lt < T_REL ? 48 - (lt / T_REL) * 4.6 : lt < T_MAKE ? 43.4 - 0.6 * clamp((lt - T_REL) / (T_MAKE - T_REL)) : 42.8;",
      f"const clk = lt < T_REL ? {C0} - (lt / T_REL) * {C0 - C1 - 1} : lt < T_MAKE ? {C1 + 1} - clamp((lt - T_REL) / (T_MAKE - T_REL)) : {C1};")
    r("qClock.textContent = clk.toFixed(1);", "const cs = Math.ceil(clk - 1e-6); qClock.textContent = `${Math.floor(cs / 60)}:${String(cs % 60).padStart(2, '0')}`;")
    r("bigClock.textContent = clk.toFixed(1);", "")
    r("bigClock.style.opacity = (0.13 * prog(lt, 1, 0.8) + (made ? 0.25 * Math.exp(-(lt - T_MAKE) * 1.5) : 0)) * (1 - prog(lt, 13.6, 0.8));", "bigClock.style.opacity = 0;")
    # signature-piece feel: the ball's arc glows in the team accent colour
    r("class: 's-silver', 'stroke-width': 4, 'stroke-dasharray': '0 1', pathLength: 1, opacity: 0.85", "fill: 'none', stroke: 'var(--blue)', 'stroke-width': 5, 'stroke-linecap': 'round', 'stroke-dasharray': '0 1', pathLength: 1, opacity: 0.9")
    r("    // Lillard's trait: Dame Time. A giant game clock counts down behind him and freezes on the make.\n", "")
    return p

def build(c, out):
    t = SRC
    def r(a, b, n=1):
        nonlocal t
        assert t.count(a) == n, (t.count(a), a[:90]); t = t.replace(a, b)
    a = t.index("  const D = {"); b = t.index("  const SCENES = [")
    t = t[:a] + c['D'] + t[b:]
    a = t.index("  // Play of the game: Damian Lillard"); b = t.index("  function sceneFlow(L, g) {")
    t = t[:a] + mkplay(c['play']) + "\n" + t[b:]
    for x, y in c['subs']: r(x, y)
    a = t.index('aria-label="Animated recap'); b = t.index('">', a)
    t = t[:a] + 'aria-label="' + c['aria'] + t[b:]
    a = t.index("  <section class=\"notes\">"); b = t.index("  </section>", a)
    t = t[:a] + '  <section class="notes">\n    <h2>About these numbers</h2>\n' + ''.join(f'    <p>{p}</p>\n' for p in c['notes']) + t[b:]
    if not c.get('palette') and c.get('team'):
        c['palette'] = team_palette(c['team'])
    if c.get('palette'):
        r("""  --navy:#14072a;--navy-mid:#2a0f52;--navy-lift:#552583;
  --ink:#fbf8ff;--muted:#b9a8d6;--blue:#fdb927;--blue-text:#fdc94f;--red:#b48ae8;--red-text:#fdb927;--silver:#d9cfe8;
  --hairline:rgba(217,207,232,.24);--track:rgba(217,207,232,.16);""", c['palette'])
    # the play-of-the-game player drawn to his listed build: "figure": {"tall": in/78, "ape": wingspan/height, "mass": ..., "label": "..."}
    fig = c.get('figure')
    if fig:
        num = c['play']['num']
        # his look (skin, hair, beard, gear) from kit/looks.json and the team's home/away kit, as in the Luka and Steph pieces
        look = {}
        if fig.get('player'):
            look, _status, _sig = look_for(fig['player'])
        sb = dict(look); sb.update({k: fig[k] for k in ('tall', 'ape', 'mass') + LOOK_KEYS if k in fig})
        r("  function scenePlay(L, g, defs) {", FIGURE_REAL + f"  const STAR_BUILD = {json.dumps(sb)};\n  function scenePlay(L, g, defs) {{")
        r(f"const shooter = figure(g, 'phi', k, {num!r});", f"const shooter = figureReal(g, 'phi', k, {num!r}, STAR_BUILD);")
        lift = re.search(r"lift = lt < 6\.3 \? (\d+) \* up", t).group(1)
        r("const rel = [shotX + 30 * k, floor + (-306 - 54) * k];",
          f"const relAt = shooter.draw(POSES.rise, shotX, floor - {lift} * k, k, 1), rel = [(relAt('lh')[0] + relAt('rh')[0]) / 2 + 4 * k, (relAt('lh')[1] + relAt('rh')[1]) / 2 - 16 * k];")
        r(".fig-num{font-family:var(--font-display);fill:var(--navy-lift)}", ".fig-num{font-family:var(--font-display);fill:var(--navy-lift)}\n.fig-hair{stroke:var(--navy-mid);fill:var(--navy-mid)}\n.fig-band{stroke:var(--navy-lift);fill:none}")
    if fig and c.get('team'):
        t = t.replace("</style>", kit_css(kit_for(c['team'], fig.get('home', True))) + "\n</style>", 1)
    t = t.replace("</style>", EMBED_CSS + "</style>", 1)
    t = t.replace('<div class="wrap">', EMBED_JS + '<div class="wrap">', 1)
    open(out, 'w').write(t)
    left = [w for w in ['Blazers', 'Portland', 'Lillard', 'Dame', 'Clippers', 'Oct 27'] if w in t]
    print(out, 'leftovers:', left)


if __name__ == '__main__':
    c = json.load(open(sys.argv[1]))
    c['subs'] = [tuple(x) for x in c['subs']]
    c['play']['clock'] = tuple(c['play']['clock'])
    build(c, sys.argv[2])
