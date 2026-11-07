# Nightly update (runs every morning)

Refreshes scores, standings, "last night", upcoming games and playoff odds on boxandmotion.com.
Cloudflare redeploys the site automatically whenever `main` changes on GitHub.

## Steps

1. Get the data from the sports feed (the `fetch_sports_data` tool, league `nba`):
   - `scores` → every game with `status: "closed"` is final. Others are in progress or upcoming.
   - `standings` → wins, losses and `rank.conference` for all 30 teams.
   Do not scrape ESPN.com or NBA.com.

2. Write `data/incoming.json`:
   ```json
   {
     "games":     [["2026-11-07", "DEN", 121, "IND", 104]],
     "standings": [["Oklahoma City Thunder", 8, 2, 3]],
     "upcoming":  [["Sun, Nov 8", "3:30 PM", "PHI", "CHI"]]
   }
   ```
   - `games`: every **closed** game from the feed (already-known games are skipped automatically).
     Date = the US Eastern date in `local_start` (a 10:30 PM ET tip on Nov 7 is `2026-11-07`).
     Order is **away, away score, home, home score**. Add `"OT"` as a 6th item only if a source says it went to overtime.
   - `standings`: all 30 teams as `[team name, wins, losses, conference rank]`, copied from the feed.
   - `upcoming`: scheduled games for the next two days: `[day as "Sun, Nov 8", ET time as "3:30 PM", away code, home code]`.
   Team codes are the keys in `data/teams.json`.

3. Run, in order:
   ```
   python3 update.py     # stops with a list of problems and changes nothing if the data doesn't add up
   python3 model.py      # playoff odds (20,000 simulations)
   python3 build.py      # rebuilds dist/
   ```
   If `update.py` reports records that don't match, a final game is missing or the feed hasn't updated.
   Re-fetch once. If it still doesn't match, stop: do not edit standings by hand and do not push.

4. Delete `data/incoming.json`, then commit and push to `main`:
   `Nightly update: games through <date>`.

5. Check the live site a couple of minutes later (https://boxandmotion.com/last-night/) shows the new date.

## Adding a recap video to a game page

Add the YouTube Shorts id to `videos` in `data/season.json`, keyed by game key `YYYY-MM-DD-AWAY-HOME`:
`"videos": {"2026-11-07-SAS-POR": "nypysMVAPZQ"}`. The video then leads that game's page.
