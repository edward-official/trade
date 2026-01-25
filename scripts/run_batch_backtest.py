import sys
from pathlib import Path

# Ensure src is in python path
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root / "src"))

from trade.backtest.single import run_single_backtest  # noqa: E402
from trade.strategies.trend import TrendStrategy  # noqa: E402


def run_all():
    """
    나스닥 상위 종목 + QQQ, QTUM에 대해 일괄 백테스트를 수행합니다.
    """
    tickers = [
        "AAPL",
        "MSFT",
        "NVDA",
        "AMZN",
        "GOOGL",
        "META",
        "TSLA",
        "AVGO",
        "COST",
        "NFLX",
        "AMD",
        "QCOM",
        "INTC",
        "PEP",
        "CSCO",
        "QQQ",
        "QTUM",
    ]

    print(f"총 {len(tickers)}개 종목에 대해 백테스트를 시작합니다...\n")

    # scripts/에서 실행되므로, 로그 디렉토리를 프로젝트 루트 기준으로 설정
    log_dir = project_root / "outputs" / "single"

    for ticker in tickers:
        print(f"[{ticker}] 백테스트 진행 중...")
        try:
            strategy = TrendStrategy()
            run_single_backtest(
                ticker=ticker,
                strategy=strategy,
                initial_balance=100.0,
                warmup=200,
                show_trades=False,
                print_to_console=False,
                log_dir=str(log_dir),
            )
        except Exception as e:
            print(f"[{ticker}] 오류 발생: {e}")

    print("\n모든 백테스트가 완료되었습니다. 결과는 'backtests/single/' 디렉토리에서 확인하세요.")


if __name__ == "__main__":
    run_all()
