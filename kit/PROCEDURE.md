# Box & Motion Hoops: nightly recap reels (every game)

What gets made (Elan's split, Nov 8, 2026):
- **Website, every game:** the drawn ~66-second recap reel (it leads the game's page) plus the text recap.
  Scenes: title, final, drawn play of the game, game flow, star, top scorers, how they won, up next, end card.
- **YouTube, the best games only:** each run posts at most ONE Short: a ~27-second, play-first cut of its most notable
  verified game (biggest star line, close finish, or a big play). Three runs = 2-3 Shorts a night. The full reel is never
  posted to YouTube. Titles lead with the player ("Steph's and-one to win it in OT | Warriors 126, Magic 119").

## Rules (non-negotiable)
- Every number and claim is verified against the box score or a named written source. Cite sources in the reel's notes.
- The play of the game names the player who made it on screen: in the subline before the shot ("Luka in the lane, 28 seconds left")
  and in the caption after it ("Luka had the dagger. Lakers by 6."). Never just "a jumper" or "a free throw".
- The player who made the play is drawn to his build (`figure` in the config): listed height and weight, arms scaled to a reported
  wingspan. Face stays featureless. Measurements from a named source that is not espn.com or nba.com (Basketball-Reference,
  RealGM, Wikipedia, team media guides via news coverage). Add a note saying what the figure is based on.
- Figure style for every player (Elan, Nov 8: every recap should look and feel like the Luka step-back and Steph's Splash, not
  stick figures): the star is drawn in his team's kit (home = white with team-colour numbers, Lakers gold at home; away = team
  colour) with his look from `kit/looks.json` (skin tone, hair, beard, gear) and the glowing outline. The face always stays blank;
  never traced, never cartoony. Set `"player"` (his name as in looks.json) and `"home"` (true/false) and the build/kit/look are
  applied automatically. If he isn't in looks.json yet, he is drawn as a team-colour silhouette in the kit: do NOT invent a look;
  list him in the report under "needs a look" so Elan can approve one. Every make gets the signature-piece finish (glowing arc in
  the team accent, sparks, backspin, the net snapping, rings off the rim); stars with a signature finish get it too (Steph: SPLASH).
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

## Steps per game (work in kit/; tell the story from the WINNING team's side, plus the losing team's short block)
1. **Box score.** `fetch_sports_data` game_stats with the game id; standings for records and conference rank; scores for each team's next game.
   **The losing side:** from the same box score, take the losing team's top two scorers (three if a third line is notable,
   e.g. a triple-double) with one short note each, and put them in the config as `"loser_top": [["Full Name", pts, "8 of 15 from three"], ...]`.
   `make_writeup.py` carries them to the game page's "From the <team>' side" block, which also says where the game got away
   (worked out from the line score) and the loser's next game. Numbers only from the box score; skip a note rather than guess.
2. **Written recaps.** WebSearch + WebFetch 2-3 game stories. Collect halftime score, runs, biggest lead, and ONE play of the game
   with clock time and score before/after. If the move isn't described, draw the template's plain pull-up and say so in the notes.
   **Board watch:** while reading the stories, look for a coaching whiteboard play: a play out of a timeout, an inbounds play or a
   late-game set that a coach drew up. It's a candidate only if at least two sources describe the actions (who screened, cut, passed,
   where the shot came from) and the clock and score are known (the Basketball-Reference play-by-play is a good check). Don't build
   it: write `kit/boards/candidates/<key>.md` (one file per game, so the three runs never edit the same file) with the coach,
   clock, score, the actions and the source links, and mention it in the report.
3. **Config.** Copy the closest example in configs/: `2026-11-06-POR-at-LAL.json` (late jumper, pull-up), `2026-11-04-DAL-at-SAS.json`
   (free throw at the line), `2026-11-02-CHI-at-PHI.json`, `2026-11-02-MIA-at-LAL.json`. Rewrite `D`, `play`, `aria`, `notes`,
   `figure`, and only the RIGHT-hand side of each `subs` pair (never a left-hand side). Set `"team"` to the winner's code and DELETE
   any `"palette"` key, so the reel is drawn in the winner's colors. Edges/gaps: only "more is better" stats; set the `max` values above
   the largest number. The footer line must be another verified fact (streak, last meeting with the next opponent).
   `figure`: `{"player": "<name as in kit/looks.json>", "home": true|false, "tall": height_in/78, "ape": wingspan_in/height_in (1.0 if no wingspan is reported), "mass": sqrt((lb/height_in)/(215/78)), "label": "..."}`.
   His look and kit come from `player`/`home` (see the figure style rule at the top).
4. **Build.** `python3 make_reel.py configs/<key>.json out/<key>-reel.html`. Leftovers may only list words that really belong to this game.
5. **Check once.** `python3 hooks.py out/<key>-reel.html out/<key>-copy.html` then
   `node shots.js $PWD/out/<key>-copy.html out/<key>-p 1 2 7 12 14.5 21.5 29 36 42 50 58 64`. Look at the frames: nothing clipped or
   overlapping, names and numbers right, the shooter's figure reads as a player. Fix and rebuild once if needed.
6. **Publish to the site** (from the repo root): `python3 kit/publish_reel.py kit/out/<key>-reel.html <key>`.
   Then write the game page's text recap from the same config:
   `python3 kit/make_writeup.py kit/configs/<date>-<AWAY>-at-<HOME>.json "<Headline>"`.
   - The headline is the only new text: short, factual, about who won and how (e.g. "Brunson and Towns take Cleveland",
     "Curry's 41 wins it in overtime"). No hype beyond the facts, and nothing that isn't in the config.
   - Everything else comes from the config's verified numbers and captions: the dek, the three things that decided it,
     where it was won, top performers and the quarter line score, with an OT column when needed.
7. **The YouTube Short (this run's ONE most notable game only).** Pick the game; its play must be a drive (layup or floater,
   with or without an and-one) or a jump shot (two or three). If its play is another kind (free throw, dunk, block, lob), use
   this run's next most notable game whose play fits; if none fits, post no Short and say so.
   - Copy the closest example in `kit/shorts/`: `2026-11-07-ORL-at-GSW.json` (drive + and-one, with the free-throw beat) or
     `2026-11-06-POR-at-LAL.json` (`"play_type": "jumper"`, `"three": true|false`). Set `out` (`short-<date>-<AWAY>-<HOME>.html`),
     `team` (the winner), `home`, `player`, `number`, `build` (tall/ape/mass from the reel config), `kicker`, `hook` (player-first,
     two short lines), `clock`, `stamp` (AND-ONE, DAGGER, GAME-WINNER, THREE... only what the play was), the beat lines
     (`ft_line` for an and-one, otherwise `beat`), `final`, `star`, `story`, `aria`.
   - Score on the board: `score_before` / `score_make` (/ `score_ft`) only if every number is verified; otherwise use
     `"margins": ["Lakers +4", "Lakers +6"]` from the written recap. Every line on every card is from the box score or a named source.
   - Build and check: `python3 kit/make_playshort.py kit/shorts/<key>.json`, then look at frames (`?short=1`, `window.__A.render(t)`)
     around the release, the make, the beat, the final card and the end card: nothing clipped or overlapping. The end card
     (from `make_playshort.py`, don't edit it per game) shows boxandmotion.com large and points to the newsletter link on the channel.
   - MP4: `bash kit/short_mp4.sh $PWD/src/anim/<out> kit/out/<key>-short.mp4 1`, copy it to `reels/<key>/short.mp4`,
     and SendUserFile it.

## After all games in this run
1. `bash kit/push_site.sh "Recap reels: <date> (<keys>)"` from the repo root. It rebuilds the site on top of the latest main and pushes,
   retrying if another run pushed first. Cloudflare redeploys in a minute or two. Then wait 3 minutes so the MP4s are live at
   `https://boxandmotion.com/reels/<key>/short.mp4`.
2. **YouTube Shorts through Buffer** (Buffer connector). Organization "My organization" (`get_account`), YouTube channel "Box & Motion"
   (`list_channels`, service youtube). Post this run's one Short (step 7). If Buffer or YouTube returns a daily-limit error, send the MP4 to Elan and say so:
   `create_post` with `channelId`, `schedulingType: "automatic"`, `mode: "shareNow"`,
   `assets: [{"video": {"url": "https://boxandmotion.com/reels/<key>/short.mp4", "metadata": {"thumbnailOffset": <ms>}}}]`, where <ms>
   is the "thumbnail offset" make_playshort.py printed (the frame with the hook, the stamp and the star; never a chart or the end card),
   `text` = the description. If create_post rejects `thumbnailOffset`, post again without it and say so in the report,
   `metadata.youtube = {"title": <title, max 100 chars>, "categoryId": "17", "privacy": "public", "madeForKids": false, "isAiGenerated": true}`.
   Title leads with the player and the play, then the result, e.g. "Steph's and-one to win it in OT | Warriors 126, Magic 119".
   Description: one or two sentences, then "Every game: boxandmotion.com · Free Sunday newsletter: boxandmotion.beehiiv.com/subscribe"
   (Shorts links aren't clickable, so these are for people to read and copy), then "Box & Motion Hoops: every NBA game, in motion.
   Unofficial fan content, not affiliated with the NBA or any team." then "#NBA #Shorts" and the two team names as hashtags.
   Never mention Elan's personal name.
   Then `get_post` until it shows `externalLink` (wait up to 2 minutes) or an `error`.
   **TikTok and Instagram too:** `list_channels` also shows any TikTok and Instagram channels connected to Buffer. Post the same
   MP4 to each with `create_post` (`schedulingType: "automatic"`, `mode: "shareNow"`, same `assets`). Caption: the one-or-two
   sentence description, then "Every NBA game, in motion: boxandmotion.com · Free Sunday newsletter: link in bio", then at most 5
   hashtags (#NBA plus the two teams and the player). Instagram: `metadata.instagram = {"type": "reel", "shouldShareToFeed": true,
   "isAiGenerated": true}`. TikTok: `metadata.tiktok = {"isAiGenerated": true}`. If one of them errors (limits, a lapsed login),
   report it and carry on; YouTube is the one whose link goes on the site.
   - Success: write the video id (the `v=` value of externalLink) to `reels/<key>/youtube.txt`. The game page keeps the reel and adds the
     "Watch on YouTube" button.
   - Error: leave the reel as is and report the error.
3. Delete `reels/<key>/short.mp4` (`git rm`), then `bash kit/push_site.sh "YouTube links: <date>"` again
   (it commits everything under reels/).

## If something blocks the morning, alert Elan
Send a **PushNotification** (summary in `<routine_summary>` tags, the first sentence says what broke) when any of these
happen, not just a note in the report:
- last night's games still aren't in `data/season.json` after the last re-pull, so reels were held back;
- `kit/push_site.sh` printed `PUSH FAILED`;
- every YouTube post in this run failed (a daily-limit error on some posts is normal; say so in the report only).

## Report (SendUserMessage)
Per game: result, star line, play of the game (who, clock, score), and a YouTube title + one-line description to paste.
Then any board candidate you logged (one line each: game, coach, clock and score, what the play was), anything skipped or filled
in from written recaps, and a Sources list. Remind Elan that a YouTube link pasted back can be
added to the game page.
