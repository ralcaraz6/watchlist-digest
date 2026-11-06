# Roadmap

What I plan to build next, roughly in order. Estimates are honest guesses.

## Done (v0.1)
- [x] Watchlist in a TOML file with my own buy/sell levels and notes
- [x] Alpha Vantage quotes + company overview, cached on disk to fit the free tier
- [x] Alerts: big daily move, near 52-week low/high, buy/sell level crossed
- [x] Markdown digest, alerts first, quiet names in a table
- [x] `--demo` mode with made-up data, unit tests for the rules

## Done (v0.2): get it to me every morning
- [x] Run on GitHub Actions every weekday after the US close, API key and watchlist as secrets
- [x] Post each digest as a comment on a "Daily digest" issue, so GitHub emails it to me
- [x] Manual run with a `demo` switch to test the pipeline without a key

## Next: better delivery (~6 h)
- [ ] Proper HTML email (SMTP) with a cleaner layout than an issue comment — 3 h
- [ ] Send a short version to Telegram — 2 h
- [ ] Skip US market holidays — 1 h

## Then: more signal, less noise (~12 h)
- [x] Upcoming earnings within 7 days (EARNINGS_CALENDAR, one call per run)
- [ ] Store daily snapshots in SQLite; show 1-week and 1-month change — 4 h
- [ ] Headlines per flagged ticker (NEWS_SENTIMENT), max 3 each — 3 h
- [ ] Thesis review dates: remind me when a note is older than N days — 2 h
- [ ] Per-ticker alert thresholds that override the global ones — 1 h

## Later: quality of life (~10 h)
- [ ] Optional one-paragraph "what changed this week" summary via an LLM API — 3 h
- [ ] Weekly summary mode (`--weekly`) — 2 h
- [ ] Rate-limit budgeting across runs (spread a long watchlist over the day) — 2 h
- [ ] `add` / `remove` CLI commands for the watchlist — 1 h
- [ ] Recorded-response tests for the Alpha Vantage parser — 2 h

Out of scope on purpose: holdings, portfolio values or any account data. This tool only looks at public prices and my own levels.
