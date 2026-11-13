"""Merge a nightly feed snapshot into data/season.json.

Input: data/incoming.json, written each morning from the sports feed:
{
  "games":     [["2026-11-07", "DEN", 121, "IND", 104], ...],    # FINAL games only; date = US Eastern game date; away first
  "standings": [["Oklahoma City Thunder", 8, 2, 3], ...],          # all 30 teams: name or code, wins, losses, conference rank
  "upcoming":  [["Sun, Nov 8", "3:30 PM", "PHI", "CHI", "NBC/Peacock"], ...]  # next ~2 days: day, ET time, away, home, national TV (optional)
}
An "OT" flag can be added as a 6th item on a game row.

Checks before writing anything (exits non-zero and changes nothing if one fails):
- every team code / name is known, scores are whole numbers and nobody ties
- all 30 teams are in the standings, conference ranks 1-15 appear once per conference
- the new results line up with the change in each team's record since the last update
"""
import json, sys, datetime

T = json.load(open("data/teams.json"))
S = json.load(open("data/season.json"))
inc = json.load(open("data/incoming.json"))

ALIASES = {f"{t['city']} {t['name']}".lower(): c for c, t in T.items()}
ALIASES.update({t["name"].lower(): c for c, t in T.items()})
ALIASES.update({"la clippers": "LAC", "la lakers": "LAL", "los angeles clippers": "LAC", "los angeles lakers": "LAL",
                "philadelphia 76ers": "PHI", "76ers": "PHI", "sixers": "PHI"})
errors = []

def code(x):
    if x in T: return x
    c = ALIASES.get(str(x).strip().lower())
    if not c: errors.append(f"unknown team: {x!r}")
    return c

# ---- new games ----
have = {(d, a, h) for d, a, _, h, _, _ in S["games"]}
new = []
for row in inc.get("games", []):
    d, a, sa, h, sh = row[:5]
    ot = row[5] if len(row) > 5 else ""
    a, h = code(a), code(h)
    try: datetime.date.fromisoformat(d)
    except Exception: errors.append(f"bad date {d!r}")
    if not (isinstance(sa, int) and isinstance(sh, int)) or sa == sh: errors.append(f"bad score {row}")
    if (d, a, h) not in have:
        new.append([d, a, sa, h, sh, "OT" if ot else ""]); have.add((d, a, h))
new.sort()

# ---- standings ----
st, ranks = {}, {}
for row in inc.get("standings", []):
    c = code(row[0])
    if c: st[c] = [int(row[1]), int(row[2])]; ranks[c] = int(row[3])
missing = sorted(set(T) - set(st))
if missing: errors.append(f"standings missing {missing}")
for conf in ("East", "West"):
    rs = sorted(ranks[c] for c in st if T[c]["conf"] == conf)
    if rs and rs != list(range(1, 16)): errors.append(f"{conf} ranks are not 1-15: {rs}")

# ---- consistency: old record + new results == new record ----
if not errors:
    exp = {c: list(v) for c, v in S["standings"].items()}
    for d, a, sa, h, sh, _ in new:
        w, l = (a, h) if sa > sh else (h, a)
        exp[w][0] += 1; exp[l][1] += 1
    off = [f"{c}: feed {st[c][0]}-{st[c][1]}, expected {exp[c][0]}-{exp[c][1]}" for c in T if exp[c] != st[c]]
    if off:
        errors.append("records don't match the results (a game is missing from 'games', or one isn't final yet):\n    " + "\n    ".join(off))

upcoming = []
for day, tm, a, h, *tv in inc.get("upcoming", []):
    upcoming.append([day, tm, code(a), code(h)] + ([tv[0]] if tv and tv[0] else []))

if errors:
    print("NOT UPDATED. Fix these and run again:")
    for e in errors: print(" -", e)
    sys.exit(1)

S["games"] += new
S["games"].sort(key=lambda g: (g[0], g[1]))
S["standings"] = st
S["seeds"] = ranks
if upcoming: S["upcoming"] = upcoming
last = max(g[0] for g in S["games"])
day = datetime.date.fromisoformat(last).strftime("%a, %b %-d")
S["updated"], S["updated_short"] = f"after {day} games", day
json.dump(S, open("data/season.json", "w"), indent=1, ensure_ascii=False)
print(f"Added {len(new)} game(s); latest game date {last}; {len(upcoming)} upcoming.")
for g in new: print("  ", *g)
