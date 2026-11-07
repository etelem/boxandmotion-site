# Box & Motion Hoops: nightly recap reels (every game)

Output per game: one drawn ~66-second recap reel, published on boxandmotion.com (it leads the game's page),
posted to YouTube Shorts through Buffer (the Short then replaces the reel at the top of the page), and the MP4 sent to Elan. This is the ONLY recap format.
Scenes: title, final, drawn play of the game, game flow, star, top scorers, how they won, up next, end card.

## Rules (non-negotiable)
- Every number and claim is verified against the box score or a named written source. Cite sources in the reel's notes.
- The play of the game names the player who made it on screen: in the subline before the shot ("Luka in the lane, 28 seconds left")
  and in the caption after it ("Luka had the dagger. Lakers by 6."). Never just "a jumper" or "a free throw".
- The player who made the play is drawn to his build (`figure` in the config): listed height and weight, arms scaled to a reported
  wingspan. Face stays featureless. Measurements from a named source that is not espn.com or nba.com (Basketball-Reference,
  RealGM, Wikipedia, team media guides via news coverage). Add a note saying what the figure is based on.
- Check that the box score's player points add up to the team total; fill missing points from a full box score (StatMuse, FantasyData)
  or written recaps and say so in the notes.
- No team or league logos, no traced footage, original music only, keep the unofficial-fan disclaimer (already in the template).
- Don't scrape ESPN.com or NBA.com. Use AP/Reuters syndications, local papers, Yahoo, team beat sites, StatMuse, FantasyData.
- Never show Elan's personal name. Brand is "Box & Motion Hoops".
- If a game can't be verified (no written recap with a clock-and-score play yet, numbers don't add up), skip it and report why.
  Never publish a guess.

## Which games
All games that finished last night (US Eastern date). From `fetch_sports_data` scores (league nba), take every `closed` game whose
`local_start` is yesterday's date, sorted by `start_time`, then by home team code. When the work is split across runs, run N of M
takes games number N, N+M, N+2M, ... (counting from 1).

Game key = `YYYY-MM-DD-AWAY-HOME`, e.g. `2026-11-06-POR-LAL` (team codes from data/teams.json).

## Steps per game (work in kit/; tell the story from the WINNING team's side)
1. **Box score.** `fetch_sports_data` game_stats with the game id; standings for records and conference rank; scores for each team's next game.
2. **Written recaps.** WebSearch + WebFetch 2-3 game stories. Collect halftime score, runs, biggest lead, and ONE play of the game
   with clock time and score before/after. If the move isn't described, draw the template's plain pull-up and say so in the notes.
3. **Config.** Copy the closest example in configs/: `2026-11-06-POR-at-LAL.json` (late jumper, pull-up), `2026-11-04-DAL-at-SAS.json`
   (free throw at the line), `2026-11-02-CHI-at-PHI.json`, `2026-11-02-MIA-at-LAL.json`. Rewrite `D`, `play`, `aria`, `notes`,
   `figure`, and only the RIGHT-hand side of each `subs` pair (never a left-hand side). Set `"team"` to the winner's code and DELETE
   any `"palette"` key, so the reel is drawn in the winner's colors. Edges/gaps: only "more is better" stats; set the `max` values above
   the largest number. The footer line must be another verified fact (streak, last meeting with the next opponent).
   `figure`: `{"tall": height_in/78, "ape": wingspan_in/height_in (1.0 if no wingspan is reported), "mass": sqrt((lb/height_in)/(215/78)), "label": "..."}`.
4. **Build.** `python3 make_reel.py configs/<key>.json out/<key>-reel.html`. Leftovers may only list words that really belong to this game.
5. **Check once.** `python3 hooks.py out/<key>-reel.html out/<key>-copy.html` then
   `node shots.js $PWD/out/<key>-copy.html out/<key>-p 1 2 7 12 14.5 21.5 29 36 42 50 58 64`. Look at the frames: nothing clipped or
   overlapping, names and numbers right, the shooter's figure reads as a player. Fix and rebuild once if needed.
6. **Publish to the site** (from the repo root): `python3 kit/publish_reel.py kit/out/<key>-reel.html <key>`.
7. **MP4.** `bash kit/mp4.sh kit/out/<key>-reel.html kit/out/<key>-recap.mp4`, then SendUserFile the MP4.
   For YouTube, also make a smaller copy next to the reel: `ffmpeg -y -loglevel error -i kit/out/<key>-recap.mp4 -c:v libx264 -preset veryfast -crf 28 -c:a aac -b:a 128k -movflags +faststart reels/<key>/recap.mp4`.

## After all games in this run
1. `bash kit/push_site.sh "Recap reels: <date> (<keys>)"` from the repo root. It rebuilds the site on top of the latest main and pushes,
   retrying if another run pushed first. Cloudflare redeploys in a minute or two. Then wait 3 minutes so the MP4s are live at
   `https://boxandmotion.com/reels/<key>/recap.mp4`.
2. **YouTube Shorts through Buffer** (Buffer connector). Organization "My organization" (`get_account`), YouTube channel "Box & Motion"
   (`list_channels`, service youtube). For each game in this run, up to `YOUTUBE_MAX_PER_RUN = 5` games (the channel is phone-verified as of Nov 7, 2026;
   three runs x 5 covers a full 15-game night), most notable game first. If Buffer or YouTube returns a daily-limit error, stop
   posting for this run, send the remaining MP4s to Elan, and say the limit was hit:
   `create_post` with `channelId`, `schedulingType: "automatic"`, `mode: "shareNow"`,
   `assets: [{"video": {"url": "https://boxandmotion.com/reels/<key>/recap.mp4"}}]`, `text` = the description,
   `metadata.youtube = {"title": <title, max 100 chars>, "categoryId": "17", "privacy": "public", "madeForKids": false, "isAiGenerated": true}`.
   Title names the star and the result, e.g. "Wembanyama's 52 and the winning free throw | Spurs 112, Mavericks 111".
   Description: one or two sentences, then "Box & Motion Hoops: animated NBA recaps. Unofficial fan content, not affiliated with the NBA
   or any team." then "#NBA #Shorts" and the two team names as hashtags. Never mention Elan's personal name.
   Then `get_post` until it shows `externalLink` (wait up to 2 minutes) or an `error`.
   - Success: write the video id (the `v=` value of externalLink) to `reels/<key>/youtube.txt`. The game page then embeds the YouTube Short.
   - Error: leave the reel as is and report the error.
   Games over the cap: send the MP4 to Elan to post by hand and say so.
3. Delete every `reels/<key>/recap.mp4` from this run (`git rm`), then `bash kit/push_site.sh "YouTube links: <date>"` again
   (it commits everything under reels/).

## Report (SendUserMessage)
Per game: result, star line, play of the game (who, clock, score), and a YouTube title + one-line description to paste.
Then anything skipped or filled in from written recaps, and a Sources list. Remind Elan that a YouTube link pasted back can be
added to the game page.
