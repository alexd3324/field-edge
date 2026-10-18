# FIELD/EDGE — Free NFL personal prediction dashboard

**Price: $0. No API key required.** The website is mobile-responsive and designed to run from GitHub Pages. Its forecasts are unvalidated historical baselines, **not established profitable betting predictions**.

## Publish it

1. Create a GitHub repository. GitHub Pages on the free plan makes the website **publicly accessible**; your local saved scenarios are stored in your own browser, but the site itself is not password-protected.
2. Upload the **contents** of this folder into the repository root, including `.github/workflows/update-data.yml`, `scripts/`, `data/`, `.nojekyll`, and `index.html`.
3. In GitHub → **Actions** → **Refresh NFL data**, select **Run workflow**. Ensure Actions has repository write permission (Settings → Actions → General). Inspect logs if the update fails.
4. In Settings → Pages, select **Deploy from a branch**, `main`, `/ (root)`.
5. Open your GitHub Pages URL in iPhone Safari, tap **Share → Add to Home Screen**.

The scheduled workflow runs three times daily, subject to GitHub scheduling delays. It downloads nflverse schedules and player game summaries, then attempts to collect public NFL lines.

## Free odds: what works and what doesn't

- **ESPN public scoreboard**: Best-effort retrieval of a DraftKings spread **only when ESPN explicitly labels the provider as DraftKings and provides an unambiguous team/spread pair**. Not every game or update will have a usable price. ESPN's endpoints are undocumented and can change.
- **DraftKings Network**: Best-effort collection of **selected popular anytime-touchdown prices**, not a comprehensive props feed. The page can change or restrict automated retrieval; the script will preserve an existing snapshot on failure.
- **Fanatics**: **Manual entry only**. No claim of automatic Fanatics coverage.
- **Other player props**: Model-generated projections can be compared with manually entered sportsbook lines. No full free automated player-prop feed is promised.
- The site displays snapshot timestamps; a displayed price is not a guaranteed current or available offer. Game spreads older than eight hours are withheld from automated spread comparisons.
- If collection fails, the website does **not** invent or silently replace odds. Always check your sportsbook before relying on a line.

## Model limitations

Historical nflverse game data powers a simple team margin model; prior player-game statistics power basic player props and ATTD projections. No verified injuries, QB adjustments, usage forecasting, EPA, or matchup-aware props yet. Historical walk-forward results are not proof of future profitability. No API key, server, or subscription is required, but the site must be published for automatic updates.

## Run collector locally (optional)

`python scripts/sync.py` downloads historical stats. `python scripts/free_odds.py` attempts free odds. These scripts require internet access. If you open `index.html` directly as a file, browser fetch restrictions can prevent auto-loading.
