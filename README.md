# paperfolio

Check a paper-trading portfolio offline, before a bad week turns into
a bad habit.

`paperfolio` takes a JSON portfolio — cash plus holdings with average
cost and current price — and reports value, profit/loss, and stop-loss
flags:

- A holding down more than 15% from cost gets a **review** flag:
  re-check the thesis before doing anything.
- A portfolio down more than 10% overall gets a **defensive** flag:
  consider switching to defence.

Both thresholds are configurable. The flags are a prompt to re-check,
not a recommendation to buy or sell.

> This is a practice-portfolio tool. It fetches no market data and
> moves no real money. It is not investment advice.

## Install

```bash
pip install .
```

Requires Python 3.10+. No dependencies.

## Usage

Create a portfolio file:

```json
{
  "cash": 1532,
  "holdings": [
    {"symbol": "NTDOY", "shares": 2, "cost": 10000, "price": 9800},
    {"symbol": "TM", "shares": 5, "cost": 2000, "price": 2100}
  ]
}
```

Then run:

```bash
paperfolio portfolio.json
# Symbol  Shares  Cost  Price  Value  P/L  P/L%
# NTDOY  2  10000  9800  19600.00  -400.00  -2.0%
# ...
# Total value: ...
# OK: no stop-loss flags.
```

Custom thresholds:

```bash
paperfolio portfolio.json --individual-stop 20 --portfolio-stop 12
```

The command exits with status 1 when any flag is raised, and status 2
on an unreadable or invalid portfolio file, so it can be used in
scripts and scheduled reviews.

## Library use

```python
from paperfolio import Holding, assess_portfolio

report = assess_portfolio(1532, [
    Holding("NTDOY", 2, 10000, 9800),
])
print(report.format())
```

## Tests

```bash
PYTHONPATH=src python -m unittest discover -s tests
```

## License

MIT
