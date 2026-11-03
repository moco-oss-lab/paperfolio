"""Core calculations for a paper-trading portfolio.

A portfolio is cash plus a list of holdings. Each holding records how
many shares were bought, at what average cost, and what the current
price is. Nothing here fetches market data or moves real money: prices
are supplied by the caller, so the tool works offline and is safe to
use for practice portfolios.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Holding:
    symbol: str
    shares: float
    cost: float  # average cost per share, in the portfolio currency
    price: float  # current price per share

    def __post_init__(self) -> None:
        if self.shares < 0:
            raise ValueError("shares must not be negative")
        if self.cost < 0 or self.price < 0:
            raise ValueError("cost and price must not be negative")

    @property
    def cost_value(self) -> float:
        return self.shares * self.cost

    @property
    def market_value(self) -> float:
        return self.shares * self.price

    @property
    def profit(self) -> float:
        return self.market_value - self.cost_value

    @property
    def return_pct(self) -> float | None:
        """Return in percent, or None when there is no cost basis."""
        if self.cost_value == 0:
            return None
        return self.profit / self.cost_value * 100


@dataclass(frozen=True)
class Flag:
    level: str  # "review" or "defensive"
    message: str


@dataclass(frozen=True)
class PortfolioReport:
    cash: float
    holdings: tuple[Holding, ...]
    flags: tuple[Flag, ...]

    @property
    def cost_value(self) -> float:
        return sum(h.cost_value for h in self.holdings)

    @property
    def market_value(self) -> float:
        return sum(h.market_value for h in self.holdings)

    @property
    def profit(self) -> float:
        return self.market_value - self.cost_value

    @property
    def total_value(self) -> float:
        return self.cash + self.market_value

    @property
    def total_cost(self) -> float:
        return self.cash + self.cost_value

    @property
    def return_pct(self) -> float | None:
        if self.total_cost == 0:
            return None
        return self.profit / self.total_cost * 100

    def format(self) -> str:
        lines = ["Symbol  Shares  Cost  Price  Value  P/L  P/L%"]
        for h in self.holdings:
            pct = "n/a" if h.return_pct is None else f"{h.return_pct:+.1f}%"
            lines.append(
                f"{h.symbol}  {h.shares:g}  {h.cost:g}  {h.price:g}  "
                f"{h.market_value:.2f}  {h.profit:+.2f}  {pct}"
            )
        lines.append(f"Cash: {self.cash:.2f}")
        lines.append(f"Holdings value: {self.market_value:.2f}")
        lines.append(f"Total value: {self.total_value:.2f}")
        total_pct = "n/a" if self.return_pct is None else f"{self.return_pct:+.1f}%"
        lines.append(f"Total P/L: {self.profit:+.2f} ({total_pct})")
        if self.flags:
            lines.append("Flags:")
            for flag in self.flags:
                lines.append(f"- [{flag.level}] {flag.message}")
        else:
            lines.append("OK: no stop-loss flags.")
        return "\n".join(lines)


def assess_portfolio(
    cash: float,
    holdings: list[Holding],
    *,
    individual_stop_pct: float = 15.0,
    portfolio_stop_pct: float = 10.0,
) -> PortfolioReport:
    """Assess a portfolio and flag stop-loss rule breaches.

    A holding whose return is worse than ``-individual_stop_pct`` gets a
    "review" flag, and a portfolio whose overall return is worse than
    ``-portfolio_stop_pct`` gets a "defensive" flag. The flags are a
    prompt to re-check the thesis, not a recommendation to sell.
    """
    if cash < 0:
        raise ValueError("cash must not be negative")
    if individual_stop_pct < 0 or portfolio_stop_pct < 0:
        raise ValueError("stop thresholds must not be negative")
    flags: list[Flag] = []
    for holding in holdings:
        pct = holding.return_pct
        if pct is not None and pct < -individual_stop_pct:
            flags.append(
                Flag(
                    "review",
                    f"{holding.symbol} is down {pct:.1f}% from cost "
                    f"(beyond -{individual_stop_pct:g}%): re-check the thesis.",
                )
            )
    report = PortfolioReport(cash, tuple(holdings), tuple(flags))
    pct = report.return_pct
    if pct is not None and pct < -portfolio_stop_pct:
        flags.append(
            Flag(
                "defensive",
                f"Portfolio is down {pct:.1f}% overall "
                f"(beyond -{portfolio_stop_pct:g}%): consider switching to defence.",
            )
        )
        report = PortfolioReport(cash, tuple(holdings), tuple(flags))
    return report
