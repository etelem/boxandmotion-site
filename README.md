# Box & Motion Hoops site

Static site for boxandmotion.com. Every page is generated from the data files.

## Layout
- `data/teams.json`: names, colors, divisions
- `data/season.json`: standings, results, upcoming games, featured recaps
- `model.py`: playoff odds model (writes `data/odds.json`)
- `build.py`: builds the site into `dist/`
- `src/`: shared CSS and JS (favorites, filters, tabs)

## Update after a night of games
1. Add results to `data/season.json` and update `standings`, `seeds`, `upcoming` and `updated`.
2. `python3 model.py && python3 build.py`
3. Commit and push. Cloudflare Pages redeploys automatically.

## Deploy (Cloudflare Pages)
- Framework preset: None
- Build command: (leave empty)
- Build output directory: `dist`
