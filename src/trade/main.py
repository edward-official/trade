import sys
import argparse
from pathlib import Path

# Disable bytecode generation
sys.dont_write_bytecode = True


def get_outputs_dir() -> Path:
    # src/trade/main.py -> src/trade -> src -> project_root
    project_root = Path(__file__).resolve().parent.parent.parent
    return project_root / "outputs"


def run_single(args: argparse.Namespace) -> None:
    from trade.backtest.single import run_single_backtest

    outputs_dir = get_outputs_dir()
    tickers = args.ticker if args.ticker else ["QQQ"]

    print(f"Running single backtest for: {tickers}")
    for ticker in tickers:
        run_single_backtest(
            ticker,
            initial_balance=1000.0,
            warmup=200,
            show_trades=True,
            use_cache=False,
            log_limit=80,
            log_dir=str(outputs_dir / "single"),
            print_to_console=False,
        )
    print("Done.")


def run_portfolio(args: argparse.Namespace) -> None:
    from trade.backtest.portfolio import run_portfolio_backtest

    outputs_dir = get_outputs_dir()
    tickers = args.ticker if args.ticker else ["QQQ", "QTUM", "IONQ", "TSLA", "GOOGL"]

    print(f"Running portfolio backtest for: {tickers}")
    run_portfolio_backtest(
        tickers,
        initial_balance=1000.0,
        warmup=200,
        show_trades=True,
        use_cache=False,
        log_limit=60,
        log_path=str(outputs_dir / "portfolio_backtest.log"),
        per_ticker_log_dir=str(outputs_dir / "portfolio_by_ticker"),
        print_to_console=False,
    )
    print("Done.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Trade execution CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Single backtest command
    single_parser = subparsers.add_parser("single", help="Run single ticker backtest")
    single_parser.add_argument("--ticker", nargs="+", help="Tickers to backtest (default: QQQ)")
    single_parser.set_defaults(func=run_single)

    # Portfolio backtest command
    portfolio_parser = subparsers.add_parser("portfolio", help="Run portfolio backtest")
    portfolio_parser.add_argument("--ticker", nargs="+", help="Tickers for portfolio (default: predefined set)")
    portfolio_parser.set_defaults(func=run_portfolio)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
