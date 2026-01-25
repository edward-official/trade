import argparse
import sys
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


def main() -> None:
    parser = argparse.ArgumentParser(description="Trade execution CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Single backtest command
    single_parser = subparsers.add_parser("single", help="Run single ticker backtest")
    single_parser.add_argument(
        "--ticker", nargs="+", help="Tickers to backtest (default: QQQ)"
    )
    single_parser.set_defaults(func=run_single)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
