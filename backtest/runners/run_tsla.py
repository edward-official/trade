from ..backtester import run_backtest
from ..data import get_history
from ..strategy import evaluate_trend


def main() -> None:
  history = get_history("TSLA", period="max", use_cache=True)
  run_backtest(
    history,
    evaluate_trend,
    initial_balance=100.0,
    warmup=200,
    name="TSLA MA trend with stop",
  )


if __name__ == "__main__":
  main()

