"""Box & Motion playoff odds, v0.

Each team's strength starts from its Oct 30 projected win total and is
updated with its actual record (the prior counts as 30 games). The rest of
the 82-game season is simulated 20,000 times, with strength uncertainty in
every run. Ties are broken at random. Outputs top-6 seed odds, top-10
(play-in or better) odds and average projected wins.
"""
import json, numpy as np

PRIOR_GAMES = 30
SIMS = 20000

def run(records, teams, prior, seed=7):
    rng = np.random.default_rng(seed)
    codes = sorted(records)
    W = np.array([records[c][0] for c in codes], float)
    G = np.array([sum(records[c]) for c in codes], float)
    p0 = np.array([prior[c] / 82 for c in codes])
    p = (p0 * PRIOR_GAMES + W) / (PRIOR_GAMES + G)
    p = p - (p.mean() - 0.5)                      # league averages .500
    rem = 82 - G
    # strength uncertainty shrinks as games are played
    sd = 0.09 * np.sqrt(PRIOR_GAMES / (PRIOR_GAMES + G))
    ps = np.clip(rng.normal(p, sd, size=(SIMS, len(codes))), 0.03, 0.97)
    final = W + rng.binomial(rem.astype(int), ps)
    final = final + rng.random(final.shape) * 1e-3  # random tiebreak
    out = {}
    for conf in ("East", "West"):
        idx = [i for i, c in enumerate(codes) if teams[c]["conf"] == conf]
        sub = final[:, idx]
        rank = (-sub).argsort(axis=1).argsort(axis=1) + 1
        for j, i in enumerate(idx):
            out[codes[i]] = {
                "top6": round(float((rank[:, j] <= 6).mean() * 100)),
                "top10": round(float((rank[:, j] <= 10).mean() * 100)),
                "wins": round(float(final[:, i].mean())),
            }
    return out

if __name__ == "__main__":
    teams = json.load(open("data/teams.json"))
    s = json.load(open("data/season.json"))
    now = {k: list(v) for k, v in s["standings"].items()}
    before = {k: list(v) for k, v in now.items()}
    # "this week" = since Monday morning (US Eastern game dates) of the latest game's week
    import datetime
    last = datetime.date.fromisoformat(max(g[0] for g in s["games"]))
    week_start = (last - datetime.timedelta(days=last.weekday())).isoformat()
    for d, a, sa, h, sh, _ in s["games"]:
        if d < week_start:
            continue
        win, lose = (a, h) if sa > sh else (h, a)
        before[win][0] -= 1
        before[lose][1] -= 1
    o_now = run(now, teams, s["prior_wins_oct30"])
    o_before = run(before, teams, s["prior_wins_oct30"])
    for c in o_now:
        o_now[c]["chg"] = o_now[c]["top6"] - o_before[c]["top6"]
        o_now[c]["rec_before"] = before[c]
    json.dump(o_now, open("data/odds.json", "w"), indent=1)
    for conf in ("West", "East"):
        print(conf)
        for c in sorted([c for c in o_now if teams[c]["conf"] == conf], key=lambda c: -o_now[c]["top6"]):
            o = o_now[c]
            print(f"  {c} {now[c][0]}-{now[c][1]} (was {before[c][0]}-{before[c][1]})  top6 {o['top6']:3d}  top10 {o['top10']:3d}  wins {o['wins']}  chg {o['chg']:+d}")
