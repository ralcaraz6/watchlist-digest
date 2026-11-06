"""Market data sources: Alpha Vantage (live) and a local fixture (demo/tests)."""
from __future__ import annotations

import csv
import io
import json
import time
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path

AV_URL = "https://www.alphavantage.co/query"


class RateLimited(RuntimeError):
    """Alpha Vantage answered with a rate-limit or info message instead of data."""


@dataclass
class Snapshot:
    symbol: str
    name: str
    price: float
    change_pct: float
    high_52w: float | None
    low_52w: float | None
    pe: float | None
    analyst_target: float | None
    next_earnings: date | None = None


def _num(value) -> float | None:
    try:
        return float(str(value).strip().rstrip("%"))
    except (TypeError, ValueError):
        return None


class FixtureSource:
    """Reads made-up snapshots from a JSON file. Used by --demo and the tests."""

    def __init__(self, path: Path):
        self.rows = {r["symbol"]: r for r in json.loads(Path(path).read_text())}

    def snapshot(self, symbol: str) -> Snapshot:
        r = self.rows[symbol]
        return Snapshot(
            symbol=symbol,
            name=r.get("name", symbol),
            price=r["price"],
            change_pct=r["change_pct"],
            high_52w=r.get("high_52w"),
            low_52w=r.get("low_52w"),
            pe=r.get("pe"),
            analyst_target=r.get("analyst_target"),
            next_earnings=(
                date.today() + timedelta(days=r["earnings_in_days"])
                if r.get("earnings_in_days") is not None else None
            ),
        )


class AlphaVantage:
    """Live data with a small on-disk cache, so a 15-ticker run fits the free tier."""

    def __init__(self, api_key: str, cache_dir: Path = Path(".cache"), ttl_hours: float = 12):
        if not api_key:
            raise ValueError("ALPHAVANTAGE_API_KEY is not set (see .env.example)")
        self.api_key = api_key
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ttl = ttl_hours * 3600
        self._earnings: dict[str, date] | None = None

    def _get(self, **params) -> dict:
        key = "_".join(f"{k}-{v}" for k, v in sorted(params.items()))
        path = self.cache_dir / f"{key}.json"
        if path.exists() and time.time() - path.stat().st_mtime < self.ttl:
            return json.loads(path.read_text())
        url = AV_URL + "?" + urllib.parse.urlencode({**params, "apikey": self.api_key})
        with urllib.request.urlopen(url, timeout=30) as resp:
            data = json.loads(resp.read())
        message = data.get("Note") or data.get("Information")
        if message:
            raise RateLimited(message)
        path.write_text(json.dumps(data))
        return data

    def earnings_dates(self) -> dict[str, date]:
        """Next report date per symbol, from ONE call for the whole market (saves quota)."""
        if self._earnings is not None:
            return self._earnings
        path = self.cache_dir / "earnings_calendar_3month.csv"
        if path.exists() and time.time() - path.stat().st_mtime < self.ttl:
            text = path.read_text()
        else:
            url = AV_URL + "?" + urllib.parse.urlencode(
                {"function": "EARNINGS_CALENDAR", "horizon": "3month", "apikey": self.api_key})
            with urllib.request.urlopen(url, timeout=60) as resp:
                text = resp.read().decode("utf-8")
            if not text.startswith("symbol"):
                raise RateLimited(text[:200])
            path.write_text(text)
        out: dict[str, date] = {}
        for row in csv.DictReader(io.StringIO(text)):
            try:
                d = date.fromisoformat(row["reportDate"])
            except (KeyError, ValueError):
                continue
            sym = row.get("symbol", "")
            if sym and (sym not in out or d < out[sym]):
                out[sym] = d
        self._earnings = out
        return out

    def snapshot(self, symbol: str) -> Snapshot:
        quote = self._get(function="GLOBAL_QUOTE", symbol=symbol).get("Global Quote", {})
        overview = self._get(function="OVERVIEW", symbol=symbol)
        price = _num(quote.get("05. price"))
        if price is None:
            raise LookupError(f"No quote returned for {symbol}")
        return Snapshot(
            symbol=symbol,
            name=overview.get("Name", symbol),
            price=price,
            change_pct=_num(quote.get("10. change percent")) or 0.0,
            high_52w=_num(overview.get("52WeekHigh")),
            low_52w=_num(overview.get("52WeekLow")),
            pe=_num(overview.get("PERatio")),
            analyst_target=_num(overview.get("AnalystTargetPrice")),
            next_earnings=self._safe_earnings().get(symbol),
        )

    def _safe_earnings(self) -> dict[str, date]:
        # Earnings dates are a bonus: a failed calendar call never breaks the digest.
        try:
            return self.earnings_dates()
        except Exception:
            self._earnings = {}
            return self._earnings
