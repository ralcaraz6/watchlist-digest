"""Alert rules: turn a snapshot plus my own levels into a short list of flags."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

from .data import Snapshot


@dataclass
class Settings:
    move_threshold_pct: float = 4.0  # flag daily moves at or beyond this size
    near_low_pct: float = 5.0        # within X% above the 52-week low
    near_high_pct: float = 2.0       # within X% below the 52-week high
    earnings_window_days: int = 7    # flag earnings reports within this many days


@dataclass
class Ticker:
    symbol: str
    buy_below: float | None = None
    sell_above: float | None = None
    note: str = ""


@dataclass
class Row:
    snap: Snapshot
    ticker: Ticker
    alerts: list[str] = field(default_factory=list)

    @property
    def upside_pct(self) -> float | None:
        t = self.snap.analyst_target
        return None if not t else (t / self.snap.price - 1) * 100


def evaluate(snap: Snapshot, ticker: Ticker, s: Settings, today: date | None = None) -> Row:
    row = Row(snap, ticker)
    today = today or date.today()
    if abs(snap.change_pct) >= s.move_threshold_pct:
        row.alerts.append(f"Big move: {snap.change_pct:+.1f}% today")
    if snap.low_52w and snap.price <= snap.low_52w * (1 + s.near_low_pct / 100):
        row.alerts.append(f"Near 52-week low ({snap.low_52w:,.2f})")
    if snap.high_52w and snap.price >= snap.high_52w * (1 - s.near_high_pct / 100):
        row.alerts.append(f"Near 52-week high ({snap.high_52w:,.2f})")
    if ticker.buy_below is not None and snap.price <= ticker.buy_below:
        row.alerts.append(f"Below my buy level ({ticker.buy_below:,.2f})")
    if ticker.sell_above is not None and snap.price >= ticker.sell_above:
        row.alerts.append(f"Above my sell level ({ticker.sell_above:,.2f})")
    if snap.next_earnings is not None:
        days = (snap.next_earnings - today).days
        if 0 <= days <= s.earnings_window_days:
            when = "today" if days == 0 else "tomorrow" if days == 1 else f"in {days} days"
            row.alerts.append(f"Earnings {when} ({snap.next_earnings.isoformat()})")
    return row
