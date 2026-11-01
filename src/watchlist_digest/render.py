"""Render the digest as Markdown: alerts first, then the quiet names."""
from __future__ import annotations

from datetime import date

from .rules import Row


def _fmt(x: float | None, suffix: str = "") -> str:
    return "n/a" if x is None else f"{x:,.2f}{suffix}"


def to_markdown(rows: list[Row], errors: dict[str, str], today: date) -> str:
    flagged = [r for r in rows if r.alerts]
    quiet = [r for r in rows if not r.alerts]
    out = [f"# Watchlist digest, {today.isoformat()}", ""]
    out.append(f"{len(flagged)} of {len(rows)} names need a look." if rows else "No data.")
    out.append("")

    if flagged:
        out += ["## Needs a look", ""]
        for r in sorted(flagged, key=lambda r: -len(r.alerts)):
            out.append(f"**{r.snap.symbol}** {r.snap.name}: {_fmt(r.snap.price)} ({r.snap.change_pct:+.1f}%)")
            out += [f"- {a}" for a in r.alerts]
            if r.ticker.note:
                out.append(f"- My note: {r.ticker.note}")
            out.append("")

    if quiet:
        out += ["## Quiet", "", "| Ticker | Price | Day | P/E | Upside to analyst target |", "|---|---|---|---|---|"]
        for r in quiet:
            out.append(
                f"| {r.snap.symbol} | {_fmt(r.snap.price)} | {r.snap.change_pct:+.1f}% "
                f"| {_fmt(r.snap.pe)} | {_fmt(r.upside_pct, '%')} |"
            )
        out.append("")

    if errors:
        out += ["## Not fetched", ""] + [f"- {s}: {e}" for s, e in errors.items()] + [""]

    out.append("_Public market data. Not investment advice._")
    return "\n".join(out) + "\n"
