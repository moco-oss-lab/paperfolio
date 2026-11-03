import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from paperfolio import Holding, assess_portfolio


class TestHolding(unittest.TestCase):
    def test_values_and_profit(self):
        h = Holding("AAA", 5, 100, 120)
        self.assertEqual(h.cost_value, 500)
        self.assertEqual(h.market_value, 600)
        self.assertEqual(h.profit, 100)
        self.assertAlmostEqual(h.return_pct, 20.0)

    def test_zero_cost_basis_has_no_return(self):
        h = Holding("FREE", 5, 0, 10)
        self.assertIsNone(h.return_pct)

    def test_negative_inputs_rejected(self):
        with self.assertRaises(ValueError):
            Holding("AAA", -1, 100, 100)
        with self.assertRaises(ValueError):
            Holding("AAA", 1, -100, 100)
        with self.assertRaises(ValueError):
            Holding("AAA", 1, 100, -1)


class TestAssessPortfolio(unittest.TestCase):
    def test_no_flags_when_healthy(self):
        report = assess_portfolio(1000, [Holding("AAA", 2, 100, 110)])
        self.assertEqual(report.flags, ())
        self.assertAlmostEqual(report.total_value, 1220)
        self.assertAlmostEqual(report.profit, 20)

    def test_individual_stop_flag(self):
        # Cash cushions the overall return, so only the review flag fires.
        report = assess_portfolio(900, [Holding("AAA", 1, 100, 80)])
        self.assertEqual(len(report.flags), 1)
        self.assertEqual(report.flags[0].level, "review")
        self.assertIn("AAA", report.flags[0].message)

    def test_exactly_at_threshold_is_not_flagged(self):
        # Exactly -15% for the holding, and cash keeps the overall
        # return above -10%, so no flag fires.
        report = assess_portfolio(900, [Holding("AAA", 1, 100, 85)])
        self.assertEqual(report.flags, ())

    def test_portfolio_stop_flag(self):
        # -20% on holdings, but cash cushions the total to exactly -10%:
        # use a case clearly beyond: holdings -20%, no cash.
        report = assess_portfolio(0, [Holding("AAA", 1, 100, 80)])
        levels = [f.level for f in report.flags]
        self.assertIn("review", levels)
        self.assertIn("defensive", levels)

    def test_cash_cushions_portfolio_flag(self):
        # Holdings down 20%, but large cash keeps overall above -10%.
        report = assess_portfolio(900, [Holding("AAA", 1, 100, 80)])
        levels = [f.level for f in report.flags]
        self.assertIn("review", levels)
        self.assertNotIn("defensive", levels)

    def test_custom_thresholds(self):
        report = assess_portfolio(
            0, [Holding("AAA", 1, 100, 90)],
            individual_stop_pct=5, portfolio_stop_pct=5,
        )
        self.assertEqual(len(report.flags), 2)

    def test_empty_portfolio(self):
        report = assess_portfolio(500, [])
        self.assertEqual(report.total_value, 500)
        self.assertEqual(report.profit, 0)
        self.assertEqual(report.flags, ())

    def test_negative_cash_rejected(self):
        with self.assertRaises(ValueError):
            assess_portfolio(-1, [])

    def test_format_lists_flags(self):
        report = assess_portfolio(0, [Holding("AAA", 1, 100, 80)])
        text = report.format()
        self.assertIn("AAA", text)
        self.assertIn("review", text)


if __name__ == "__main__":
    unittest.main()
