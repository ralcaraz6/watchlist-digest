"""Command line entry point: `watchlist-digest --watchlist watchlist.toml`."""
from __future__ import annotations

import argparse
import os
import sys
import tomllib
from datetime import date
from pathlib import Path

from .data import AlphaVantage, FixtureSource, RateLimited
from .render import to_markdown
from .rules import Settings, Ticker, evaluate

ROOT = Path(__file__).resolve().parents[2]


def load_env(path: Path = Path(".env")) -> None:
    """Minimal .env reader so the tool has no dependencies."""
    if path.exists():
        for line in path.read_text().splitlines():
            if "=" in line and not line.lstrip().startswith("#"):
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())


def load_watchlist(path: Path) -> tuple[Settings, list[Ticker]]:
    cfg = tomllib.loads(Path(path).read_text())
    settings = Settings(**cfg.get("settings", {}))
    tickers = [Ticker(**t) for t in cfg.get("ticker", [])]
    if not tickers:
        raise SystemExit(f"No [[ticker]] entries in {path}")
    return settings, tickers


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="watchlist-digest", description=__doc__)
    p.add_argument("--watchlist", type=Path, default=Path("watchlist.toml"))
    p.add_argument("--out", type=Path, help="write the digest here instead of printing it")
    p.add_argument("--demo", action="store_true", help="use made-up sample data, no API key needed")
    args = p.parse_args(argv)

    if args.demo:
        source = FixtureSource(ROOT / "sample" / "snapshots.json")
        watchlist = ROOT / "sample" / "watchlist.toml"
    else:
        load_env()
        source = AlphaVantage(os.environ.get("ALPHAVANTAGE_API_KEY", ""))
        watchlist = args.watchlist

    settings, tickers = load_watchlist(watchlist)
    rows, errors = [], {}
    for t in tickers:
        try:
            rows.append(evaluate(source.snapshot(t.symbol), t, settings))
        except RateLimited as e:
            errors[t.symbol] = f"rate limited ({e})"
            break
        except Exception as e:  # one bad ticker should not kill the digest
            errors[t.symbol] = str(e)

    md = to_markdown(rows, errors, date.today())
    if args.out:
        args.out.write_text(md)
        print(f"Wrote {args.out}")
    else:
        sys.stdout.write(md)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
