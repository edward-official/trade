import sys

sys.dont_write_bytecode = True

from ..portfolio import run_portfolio_backtest


def main() -> None:
  tickers = ["QQQ", "QTUM", "IONQ", "TSLA", "GOOGL"]
  run_portfolio_backtest(
    tickers,
    initial_balance=1000.0,
    warmup=200,
    show_trades=True,
    use_cache=False,
    log_limit=60,
    log_path="portfolio_backtest.log",
    per_ticker_log_dir="portfolio_backtest_by_ticker",
    print_to_console=False,
  )


if __name__ == "__main__":
  main()
