import sys
from pathlib import Path

# Ensure src is in python path
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root / "src"))

import pandas as pd  # noqa: E402, I001
from trade.data import get_history  # noqa: E402
from trade.strategies.trend import add_moving_averages, evaluate_trend  # noqa: E402


def main():
    tickers = ["QQQ", "SPY", "AAPL", "TSLA", "NVDA", "MSFT", "AMZN", "GOOGL"]

    print(f"🔍 Daily Signal Scan ({pd.Timestamp.now().date()})")
    print("-" * 65)
    header = (
        f"{'Ticker':<8} {'Price':<10} {'Trend':<10} "
        f"{'Action (No Pos)':<18} {'Action (Holding)':<18}"
    )
    print(header)
    print("-" * 65)

    for ticker in tickers:
        try:
            # Fetch latest data without cache to get today's data
            history = get_history(ticker, period="2y", use_cache=False)
            if history.empty:
                print(f"{ticker:<8} {'N/A':<10} {'No Data'}")
                continue

            history = add_moving_averages(history)

            # Use the last available candle
            idx = len(history) - 1
            last_close = history["Close"].iloc[idx]

            # 1. Check Entry Signal (Assuming we don't hold it)
            entry_signal = evaluate_trend(
                history=history,
                index=idx,
                is_retained=False,
                entry_price=0.0,
                highest_price=0.0,
            )

            # 2. Check Exit Signal (Assuming we hold it)
            # Evaluate trend usually checks Trailing Stop or MA violation.
            # We assume a hypothetical 'highest_price' equal to current price to focus
            # on MA violation, unless the price is already below MA.
            exit_signal = evaluate_trend(
                history=history,
                index=idx,
                is_retained=True,
                entry_price=last_close,
                highest_price=last_close,
            )

            # Determine Trend Status
            sma150 = history["sma150"].iloc[idx]
            sma200 = history["sma200"].iloc[idx]

            trend_str = "Unknown"
            if not pd.isna(sma150) and not pd.isna(sma200):
                if last_close > sma150 and last_close > sma200:
                    trend_str = "UP 🟢"
                elif last_close < sma150 or last_close < sma200:
                    trend_str = "DOWN 🔴"
                else:
                    trend_str = "MIXED 🟡"

            # Formulate Action Strings
            entry_act = "BUY 🚀" if entry_signal == "ENTER" else "WAIT"
            exit_act = "SELL ⚠️" if exit_signal == "EXIT" else "HOLD"

            row = (
                f"{ticker:<8} {last_close:<10.2f} {trend_str:<10} "
                f"{entry_act:<18} {exit_act:<18}"
            )
            print(row)

        except Exception as e:
            print(f"{ticker:<8} Error: {e}")

    print("-" * 65)


if __name__ == "__main__":
    main()
