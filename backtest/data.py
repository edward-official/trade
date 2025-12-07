from pathlib import Path
from typing import Optional

import pandas as pd
import yfinance as yf


def get_history(
    ticker: str,
    period: str = "max",
    use_cache: bool = True,
    data_dir: str = "data",
) -> pd.DataFrame:
  """
  Download price history for a ticker via yfinance.

  If use_cache is True, store/load from CSV under `data_dir/{ticker}.csv`
  so that repeated 백테스트가 항상 같은 데이터를 사용하도록 한다.
  """
  csv_path = None
  if use_cache:
    data_path = Path(data_dir)
    data_path.mkdir(parents=True, exist_ok=True)
    csv_path = data_path / f"{ticker}.csv"

    if csv_path.exists():
      history = pd.read_csv(csv_path, index_col=0, parse_dates=True)
      return history

  target = yf.Ticker(ticker)
  history = target.history(period=period)

  if history.empty:
    raise ValueError(f"No history returned for ticker '{ticker}'")

  if use_cache and csv_path is not None:
    history.to_csv(csv_path)

  return history
