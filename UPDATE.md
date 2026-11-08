# Nightly update (runs every morning)

Refreshes scores, standings, "last night", upcoming games and playoff odds on boxandmotion.com.
Cloudflare redeploys the site automatically whenever `main` changes on GitHub.

## Steps

1. Get the data from the sports feed (the `fetch_sports_data` tool, league `nba`):
   - `scores` → every game with `status: "closed"` is final. Others are in progress or upcoming.
   - `standings` → wins, losses and `rank.conference` for all 30 teams.
   Do not scrape ESPN.com or NBA.com.
   If the `fetch_sports_data` tool isn't available in this session (it isn't listed and ToolSearch doesn't find it), or it
   errors twice, use the **fallback sources** below instead. Never stop just because the feed is missing.

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

3b. **Official video links** (`data/links.json`, keyed `<date>-<AWAY>-<HOME>`, e.g. `2026-11-06-POR-LAL`). For each game added
   tonight, plus any game from the last 7 days that has no `highlights` yet (at most 15 games a run), use WebSearch with
   `allowed_domains: ["youtube.com"]`:
   - `highlights`: query `<Away name> at <Home name> full game highlights <Month D YYYY>`. Accept ONLY the NBA channel's upload.
     The title reads `AWAY at HOME | FULL GAME HIGHLIGHTS | <Month D, YYYY>` (it may start with `EXTENDED:` or add a cup tag),
     and the description starts "The <winner> defeated the <loser>, <score> tonight". Reject re-uploads ("X vs Y - FULL GAME
     HIGHLIGHTS | ... NBA Season"), reaction videos and other channels. Store the video id only.
   - `postgame` (optional): query `<team> postgame <opponent> <Month D YYYY>`. Store it only when the result is clearly the
     team's own channel or its TV broadcaster, and set `postgame_label` (e.g. "Lakers postgame interviews"). If unsure, leave
     it out: the page then links a YouTube search for that game's postgame interviews.
   Never guess an id. Then run `python3 build.py` again.

4. Delete `data/incoming.json`, then commit and push to `main`:
   `Nightly update: games through <date>`.

5. Check the live site a couple of minutes later (https://boxandmotion.com/last-night/) shows the new date.

## Fallback sources (when the feed is unavailable)
Same `data/incoming.json`, same checks; only the sources change. Never ESPN.com or NBA.com.
- **Which games:** the season schedule on Plain Text Sports (`https://plaintextsports.com/nba/<season>/schedule`, e.g.
  `2026-2027`) lists last night's games, ET tip times and each game's page link. Take every game dated last night.
- **Final scores:** each score must match in **two** sources: the Covers.com box score (WebSearch with
  `allowed_domains: ["covers.com"]`, e.g. "covers.com Nuggets vs Pacers Game Overview Match Player Stats November 07, 2026")
  and one of: the Plain Text Sports game page, the AP or Field Level Media game story, or the CBS Sports gametracker.
  Add `"OT"` only if a source says overtime. Check the Covers line score adds up to the final. If a game isn't final yet
  or two sources don't agree, wait 15 minutes and try once more; if it's still unconfirmed, stop and report it.
- **Standings:** FOX Sports conference standings (`https://www.foxsports.com/nba/standings`): rank, wins and losses for
  all 30 teams. If update.py says records don't match and the differences are exactly last night's results, FOX hasn't
  refreshed yet: wait 15 minutes, fetch again and retry once.
- **Upcoming:** the next two days from the Plain Text Sports schedule (times are ET).
- Commit message: `Nightly update: games through <date> (fallback sources)`, and say in the report that the fallback was used.
- update.py's record check is the safety net: if it still refuses after the retry, change nothing and do not push.

## If the update fails, alert Elan
If the run ends without pushing last night's games (feed and fallback both failed, update.py refused, or the push
failed), send a **PushNotification** right away, not just a SendUserMessage, with the summary in `<routine_summary>`
tags: first sentence "Site update failed: <reason in a few words>.", then what didn't match and that the recap runs will
hold their reels until it's fixed. A successful fallback run needs no push; the normal report says the fallback was used.

## Adding a recap video to a game page

Add the YouTube Shorts id to `videos` in `data/season.json`, keyed by game key `YYYY-MM-DD-AWAY-HOME`:
`"videos": {"2026-11-07-SAS-POR": "nypysMVAPZQ"}`. The video then leads that game's page.
