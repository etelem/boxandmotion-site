# X's and O's in 20 seconds
A learn-the-game series: each piece explains one basketball term (pin-down, Spain pick-and-roll, Horns...) on the whiteboard.

- Evergreen: no games, players, teams, dates or "this week" references, so a piece never goes out of date.
- Build: `python3 kit/make_board.py kit/xo/<term>.json src/anim/xo-<term>.html` (no `team`, `clock` or `score` in the config,
  so it draws in Box & Motion orange with no game clock), then `bash kit/short_mp4.sh $PWD/src/anim/xo-<term>.html kit/out/xo-<term>.mp4 1`.
- Music: Film Room (`python3 kit/music.py film-room <out.mp3>` on the music-options branch), faded out over the last 1.5 seconds.
- Spots on the floor are illustrative; the note on the board says so.
