# watchlist-digest

A daily digest of my personal stock watchlist. Instead of opening ten charts every morning, I get one short page: which names moved hard, which are near their 52-week low or high, and which crossed the buy or sell levels I set myself. Everything else goes into a quiet table.

**Who it's for:** me, an individual investor with a watchlist of 10–20 names. It works for anyone with the same habit.
**Built with:** Python 3.11+ (standard library only) and the [Alpha Vantage](https://www.alphavantage.co/) API for public market data.

## What it does

```
2 of 4 names need a look.

ACME Acme Robotics (fictional): 41.20 (-6.3%)
- Big move: -6.3% today
- Near 52-week low (40.10)
- Below my buy level (45.00)
- My note: Thesis: margins recover in 2027. Re-check after earnings.
```

- Alerts on big daily moves, proximity to the 52-week low/high, and my own buy/sell levels
- Shows P/E and upside to the analyst target for the quiet names
- Caches API responses so a full run fits the Alpha Vantage free tier
- No holdings, no account data: only public prices and the levels I write in my watchlist

## Run it

Try it with made-up data (no API key needed):

```bash
git clone https://github.com/ralcaraz6/watchlist-digest.git
cd watchlist-digest
PYTHONPATH=src python3 -m watchlist_digest --demo
```

With live data:

```bash
cp .env.example .env                  # add your free Alpha Vantage key
cp watchlist.example.toml watchlist.toml   # add your tickers and levels
PYTHONPATH=src python3 -m watchlist_digest --out digest.md
```

Or install it: `pip install -e .` and then `watchlist-digest --demo`.

## Tests

```bash
python3 -m unittest discover -s tests
```

## Plans

See [ROADMAP.md](ROADMAP.md): email and Telegram delivery, a daily GitHub Actions run, earnings dates, history in SQLite, headlines.

## License

MIT. Public market data only; nothing here is investment advice.
