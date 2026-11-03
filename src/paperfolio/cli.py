"""Command-line interface for paperfolio.

Usage:
    paperfolio portfolio.json [--individual-stop 15] [--portfolio-stop 10]

The JSON file has the shape:
    {"cash": 1532, "holdings": [
        {"symbol": "NTDOY", "shares": 2, "cost": 10000, "price": 9800}
    ]}

Exits with status 1 when any stop-loss flag is raised, so it can be
used in scripts and scheduled reviews.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .core import Holding, assess_portfolio


def load_portfolio(path: Path) -> tuple[float, list[Holding]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("portfolio file must contain a JSON object")
    cash = float(data.get("cash", 0))
    holdings = [
        Holding(
            symbol=str(item["symbol"]),
            shares=float(item["shares"]),
            cost=float(item["cost"]),
            price=float(item["price"]),
        )
        for item in data.get("holdings", [])
    ]
    return cash, holdings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="paperfolio", description=__doc__)
    parser.add_argument("portfolio", type=Path, help="JSON portfolio file")
    parser.add_argument("--individual-stop", type=float, default=15.0,
                        help="per-holding stop threshold in percent (default 15)")
    parser.add_argument("--portfolio-stop", type=float, default=10.0,
                        help="whole-portfolio stop threshold in percent (default 10)")
    args = parser.parse_args(argv)
    try:
        cash, holdings = load_portfolio(args.portfolio)
        report = assess_portfolio(
            cash, holdings,
            individual_stop_pct=args.individual_stop,
            portfolio_stop_pct=args.portfolio_stop,
        )
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f"paperfolio: error: {exc}", file=sys.stderr)
        return 2
    print(report.format())
    return 1 if report.flags else 0


if __name__ == "__main__":
    raise SystemExit(main())
