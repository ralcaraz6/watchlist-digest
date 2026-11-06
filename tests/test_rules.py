import sys
import unittest
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from watchlist_digest.data import FixtureSource  # noqa: E402
from watchlist_digest.render import to_markdown  # noqa: E402
from watchlist_digest.rules import Settings, Ticker, evaluate  # noqa: E402

SRC = FixtureSource(ROOT / "sample" / "snapshots.json")


class RuleTests(unittest.TestCase):
    def test_big_drop_near_low_and_buy_level(self):
        row = evaluate(SRC.snapshot("ACME"), Ticker("ACME", buy_below=45), Settings())
        self.assertEqual(len(row.alerts), 3)
        self.assertTrue(row.alerts[0].startswith("Big move"))

    def test_near_high_and_sell_level(self):
        row = evaluate(SRC.snapshot("NIMB"), Ticker("NIMB", sell_above=210), Settings())
        self.assertIn("Above my sell level (210.00)", row.alerts)
        self.assertTrue(any("52-week high" in a for a in row.alerts))

    def test_quiet_name_has_no_alerts(self):
        row = evaluate(SRC.snapshot("TERR"), Ticker("TERR"), Settings())
        self.assertEqual(row.alerts, [])
        self.assertAlmostEqual(row.upside_pct, 7.95, places=2)

    def test_earnings_inside_window(self):
        row = evaluate(SRC.snapshot("VOLT"), Ticker("VOLT"), Settings())
        self.assertTrue(any(a.startswith("Earnings in 3 days") for a in row.alerts))

    def test_earnings_outside_window_is_quiet(self):
        snap = SRC.snapshot("NIMB")
        row = evaluate(snap, Ticker("NIMB"), Settings())
        self.assertFalse(any(a.startswith("Earnings") for a in row.alerts))
        snap.next_earnings = date.today() + timedelta(days=1)
        row = evaluate(snap, Ticker("NIMB"), Settings())
        self.assertIn("Earnings tomorrow", row.alerts[-1])

    def test_markdown_puts_alerts_first(self):
        rows = [evaluate(SRC.snapshot(s), Ticker(s), Settings()) for s in ["TERR", "ACME"]]
        md = to_markdown(rows, {}, date(2026, 11, 1))
        self.assertLess(md.index("ACME"), md.index("TERR"))
        self.assertIn("1 of 2 names need a look.", md)


if __name__ == "__main__":
    unittest.main()
