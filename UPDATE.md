# Nightly update (runs every morning)

Refreshes scores, standings, "last night", upcoming games and playoff odds on boxandmotion.com.
Cloudflare redeploys the site automatically whenever `main` changes on GitHub.

## Two checks a morning (about 6:40 and 7:15 AM ET)
The same procedure runs twice (cut from five on Nov 12, 2026 to save usage). Standings pages refresh at different times each
morning (FOX or CBS current by 6:12-6:49 on Nov 8-11), so the scores are verified once and the second check only waits for
current standings if the first found them stale. The first check also handles quiet nights.

0. **Already done?** If `data/season.json` already has last night's games (its `updated_short` is last night's date, e.g.
   "Mon, Nov 9"), or there were no games and nothing changed, stop: one line in the report, no commit, no alert.
1. **Saved scores?** If `data/pending/<last night's date>.json` exists, an earlier check already verified the scores
   (same format as `data/incoming.json`). Use its `games` and `upcoming` as they are and only fetch fresh standings
   (step 1 below, standings part). Otherwise do the full steps.
2. **Standings not current yet** (update.py says the records don't match, and the differences are exactly last night's
   results): save the verified `games` and `upcoming` to `data/pending/<date>.json`, add a line to the standings log,
   commit `Standings check <time> ET: waiting for standings (<date>)` and push. No alert unless this is the 7:15 check (the last one).
3. **Standings log:** every check that fetches standings appends one line to `data/standings-log.csv`:
   `<games date>,<check time ET>,<source>,<current|stale>` (e.g. `2026-11-09,06:30,FOX,stale`). It shows when standings
   usually appear, so checks that never matter can be dropped later.
4. **On success:** also delete `data/pending/<date>.json` in the same commit.

## Steps

1. Get the data from the sports feed (the `fetch_sports_data` tool, league `nba`):
   - `scores` → every game with `status: "closed"` is final. Others are in progress or upcoming.
   - `standings` → wins, losses and `rank.conference` for all 30 teams.
   Do not scrape ESPN.com or NBA.com.
   If the `fetch_sports_data` tool isn't available in this session (it isn't listed and ToolSearch doesn't find it), or it
   errors twice, use the **fallback sources** below instead. Never stop just because the feed is missing.

   **National TV for upcoming games (added Nov 13, 2026):** for each upcoming game, look up its national network on
   Sports Media Watch's NBA TV schedule (sportsmediawatch.com/nba-tv-schedule/) and confirm it on the network's own
   schedule or a second outlet (NBC Sports, Prime Video/Amazon, ESPN Press Room, Awful Announcing). Only national outlets:
   ABC, ESPN, NBC, Peacock, Prime Video, NBA TV (write e.g. "Prime Video", "NBC/Peacock", "ESPN"). If the two don't agree, or
   only one source lists it, leave it off. Regional/local channels and League Pass are never listed. Add it as an optional
   5th item on that game's `upcoming` row; the site shows it as a small tag on tonight's schedule and team pages' next game.

2. Write `data/incoming.json`:
   ```json
   {
     "games":     [["2026-11-07", "DEN", 121, "IND", 104]],
     "standings": [["Oklahoma City Thunder", 8, 2, 3]],
     "upcoming":  [["Sun, Nov 8", "3:30 PM", "PHI", "CHI", "NBC/Peacock"], ["Sun, Nov 8", "6:00 PM", "LAL", "SAS"]]
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
   If `update.py` reports records that don't match and the differences are exactly last night's results, the standings
   source hasn't refreshed yet: try the backup standings source (see Fallback sources), and if that is stale too, save the
   scores as in "Two checks a morning" step 2 and leave it to the next check. If the differences are anything else (a game
   missing or not final), re-check the games once. Never edit standings by hand, and never push season.json changes that
   update.py refused.

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

4. Delete `data/incoming.json` (and `data/pending/<date>.json` if there is one), then commit and push to `main`:
   `Nightly update: games through <date>`.

5. Check the live site a couple of minutes later shows the new date. Add a throwaway query so WebFetch doesn't return a
   cached copy: `https://boxandmotion.com/last-night/?r=<HHMM>`. A stale result is still not a failure: say so in the
   report, and send no alert for it. Only a failed push is a deploy problem worth a PushNotification.

## Fallback sources (when the feed is unavailable)
Same `data/incoming.json`, same checks; only the sources change. Never ESPN.com or NBA.com.
- **Which games:** the season schedule on Plain Text Sports (`https://plaintextsports.com/nba/<season>/schedule`, e.g.
  `2026-2027`) lists last night's games, ET tip times and each game's page link. Take every game dated last night.
- **Final scores:** each score must match in **two** sources: the Covers.com box score (WebSearch with
  `allowed_domains: ["covers.com"]`, e.g. "covers.com Nuggets vs Pacers Game Overview Match Player Stats November 07, 2026")
  and one of: the Plain Text Sports game page, the AP or Field Level Media game story, or the CBS Sports gametracker.
  If a game's Covers matchup page doesn't come up in search or won't open, the result on the winning team's Covers schedule
  page (covers.com/sport/basketball/nba/teams/main/<team>, e.g. minnesota-timberwolves) counts as the Covers source.
  Plain Text Sports pages can come back as an old snapshot (check the "loaded at" time on the page); if one is from before the
  game, use the AP / Field Level Media story or the CBS Sports scoreboard as the second source instead.
  Add `"OT"` only if a source says overtime. Check the Covers line score adds up to the final. If a game isn't final yet
  or two sources don't agree, don't save that night's scores: the next check verifies them again (the 7:15 check reports
  what's still unconfirmed and alerts).
- **Standings:** FOX Sports conference standings (`https://www.foxsports.com/nba/standings`): rank, wins and losses for
  all 30 teams. If FOX can't be opened or update.py shows FOX is stale (differences are exactly last night's results), use
  CBS Sports (`https://www.cbssports.com/nba/standings/`) the same way. If both are stale, the next check tries again
  (see "Two checks a morning"); don't wait inside the run. ESPN.com and NBA.com stay off-limits (ESPN's standings also came
  back stale through WebFetch hours after the games when tested on Nov 10).
- **Upcoming:** the next two days from the Plain Text Sports schedule (times are ET).
- Commit message: `Nightly update: games through <date> (fallback sources)`, and say in the report that the fallback was used.
- update.py's record check is the safety net: if it still refuses after the retry, change nothing and do not push.

## If the update fails, alert the owner
Only the **7:15 check** (the last one) alerts for missing data: if it ends without last night's games in season.json
(standings still stale on FOX and CBS, scores still unconfirmed, or update.py refused), send a **PushNotification** right
away, not just a SendUserMessage, with the summary in `<routine_summary>` tags: first sentence "Site update failed: <reason
in a few words>.", then what didn't match and that the recap runs will hold their reels until it's fixed. Earlier checks
that save scores and wait send no alert. A failed push alerts from any check. A successful fallback run needs no push; the
normal report says the fallback was used.

## Adding a recap video to a game page

Add the YouTube Shorts id to `videos` in `data/season.json`, keyed by game key `YYYY-MM-DD-AWAY-HOME`:
`"videos": {"2026-11-07-SAS-POR": "nypysMVAPZQ"}`. The video then leads that game's page.
