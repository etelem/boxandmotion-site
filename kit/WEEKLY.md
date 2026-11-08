# Box & Motion Hoops: the weekly deep dives and The Sunday Box

Every Saturday morning this run makes the week's two deep dives and drafts Sunday's newsletter. **Nothing goes public until
Elan approves.** The run builds everything, sends him previews and waits in the same session for his reply.

The house rules in PROCEDURE.md still apply: every number checked against a box score or a named written source; no logos and
no traced footage; never espn.com or nba.com as a source; never Elan's personal name anywhere; skip rather than guess. Figures
follow the figure style rule at the top of PROCEDURE.md: the recap silhouette drawn to the player's build, plus ONE motion that
shows his signature trait.

## The week
The games from last Saturday through Friday night: every game in `data/season.json` dated in that window. Pull before
starting; the nightly update keeps that file current.

## 1. Scouting report: the week's hottest player
1. **Pick him.** Use fetch_sports_data (game_stats for the week's games) to rank players by the week: points per game (2+ games),
   plus 50-point nights, triple-doubles and game-winners. Skip anyone with a report in the last 4 weeks (`data/players/`, and Luka
   Dončić's hand-built page). If two are close, take the team that hasn't had a deep dive yet.
2. **His week, verified.** For each game: date, opponent, result, pts, reb, ast, FG, 3PT. Use the feed's box score and check
   the points against at least one written recap. Bio line: listed height and weight, position, season number (Basketball-Reference
   or RealGM). Build: tall = height_in/78, ape = wingspan/height (1.0 if none reported), mass = sqrt((lb/height_in)/(215/78)).
3. **Signature move.** Find his signature move described in writing (scouting pieces, team beat coverage, The Ringer, Yahoo, SI).
   Two sources should agree. Write three short steps for it.
   - Step-back three: copy `kit/moves/luka-stepback.json` to `kit/moves/<slug>-<move>.json`, edit it, then run
     `python3 kit/make_stepback.py kit/moves/<file>.json`.
   - Any other move: write `kit/make_<move>.py` modeled on make_stepback.py. Keep its features: the same figure and palette,
     `?embed=1` and `?short=1` modes, `window.__A = {render, build, total}`, the height postMessage, controls, reduced motion,
     a "not traced from footage, not to scale" note and an aria label. Add his trait motion (speed = afterimage trail).
   Check frames at 1100 px and 400 px wide and in `?short=1`; fix any overlap.
4. **Write `data/players/<slug>.json`** (example fields):
   ```json
   {"slug": "jalen-brunson", "name": "Jalen Brunson", "team": "NYK", "published": "2026-11-14", "week": "Week of Nov 8",
    "lede": "One sentence on why he's the hottest player in the league this week.",
    "bio": "No. 11 · Knicks · 6-2 · 8th NBA season", "card": "38.5 points a game this week",
    "stats": [["38.5", "points per game"], ["4", "games"], ["47", "week high"], ["7–2", "Knicks record"]],
    "move": {"title": "The step-back three", "text": "Two sentences on how it works.", "anim": "jalen-brunson-stepback.html",
             "steps": [["The jab", "..."], ["The hop back", "..."], ["The rise", "..."]]},
    "log": [["Nov 8", "vs. Celtics", "W 120–112", 41, 5, 8, "15–27", "5–11"]],
    "sources": [["Label", "https://..."]]}
   ```
   Log rows are newest first. Use `null` for a stat the feed doesn't have (it shows as a dash).

## 2. Coach's board: the week's best drawn-up play (only if one qualifies)
1. **Find it.** Search the week's game stories for after-timeout plays and sets with a written description: "out of a
   timeout", "drew up", "inbounds play", "play call", game-winners. It qualifies only if at least two sources describe the
   actions (who screened, who cut, who passed, where the shot came from), with the clock and the score. If nothing qualifies,
   skip the board this week and say so. Never invent an action.
2. **Draw it.** Copy `kit/boards/2026-11-04-MIA-at-LAC.json` to `kit/boards/<date>-<AWAY>-at-<HOME>.json` and edit it.
   - Offense: numbered circles; name only players the sources name.
   - Defense: X's.
   - Actions: move (`key: true` for the main cutter), screen, pass, shot. Coordinates are in feet: x from -25 (offense's left)
     to 25, y from the baseline (0) to half court (47).
   - Keep the note saying the spots are illustrative.
   - The clock freezes until the catch, then runs to the release.
   Run `python3 kit/make_board.py kit/boards/<file>.json src/anim/<slug>.html`, then check the frames in all three layouts.
3. **Add it to `data/deepdives.json`** under `boards` (newest first): config, anim, published, coach_slug, since (the year he
   became head coach), dek.

## 3. Shorts and the newsletter draft
1. For each animation: `bash kit/short_mp4.sh src/anim/<file>.html kit/out/<file>-short.mp4` (normal speed, then slow motion).
   Copy it to `src/anim/<file>.mp4` for the YouTube step below.
2. **Draft the issue in beehiiv** (publication "Box & Motion", The Sunday Box). Duplicate the newest Sunday Box post and keep
   its design. Title: "The Sunday Box: <hook>". Sections:
   - The week in one line.
   - Game of the week, with its recap Short link.
   - Playoff race movers, from `data/odds.json`.
   - Deep dives: the scouting report and the board, each with a link to its page on boxandmotion.com.
   - Games to watch this week.
   Every number comes from the site data or the sources above. Send a test email to boxandmotionhoops@gmail.com. Do not
   schedule it yet.
3. **Build on a branch:** create `weekly-<date>`, run `python3 build.py`, commit and push the branch (not main). Main is
   unchanged, so nothing is public yet.

## 4. Ask Elan, then publish
Send with SendUserFile: both Shorts MP4s. Then a SendUserMessage with:
- the hot player and why, his week's line, and the move;
- the board: play, clock, score and the sources;
- the newsletter's title and subject line, and that a test email went to the brand inbox;
- "Reply **approve** to publish everything, or tell me what to change."

Then wait for his reply in this session. Change whatever he asks and send new previews.
**On approve:**
1. Merge the branch into main, then `python3 build.py`, commit, and push. Use the same retry loop as kit/push_site.sh.
2. Wait 3 minutes, then post each Short through Buffer (the same settings as PROCEDURE.md step 2), with
   `assets.video.url = https://boxandmotion.com/anim/<file>.mp4`.
   - Titles: "<Player>'s <move>, explained | Box & Motion scouting report" and "<Coach>'s <play>, on the board | <Team> vs <Opp>".
   - When the video ids come back, add them to the deep-dive data (`youtube` field), `git rm src/anim/*.mp4`, rebuild and push.
3. Add the Short links to the newsletter draft. Schedule it for Sunday 8:00 AM ET (or the time Elan gave), then report the
   scheduled time.
Before ending your turn, use send_later to remind yourself in this session at Sunday 7:30 AM ET. If he still hasn't
replied by then, publish nothing and send him one reminder.
