import pandas as pd


def add_moving_averages(history: pd.DataFrame) -> pd.DataFrame:
  close = history["Close"]
  if "sma10" not in history.columns:
    history["sma10"] = close.rolling(window=10).mean()
  if "sma20" not in history.columns:
    history["sma20"] = close.rolling(window=20).mean()
  if "sma50" not in history.columns:
    history["sma50"] = close.rolling(window=50).mean()
  if "sma150" not in history.columns:
    history["sma150"] = close.rolling(window=150).mean()
  if "sma200" not in history.columns:
    history["sma200"] = close.rolling(window=200).mean()
  return history


def is_on_up_trend(history: pd.DataFrame, index: int) -> bool:
  """
  조건: sma200 < sma150 < sma50 < 당일 저가
  """
  price_low = history["Low"].iloc[index]
  sma50 = history["sma50"].iloc[index]
  sma150 = history["sma150"].iloc[index]
  sma200 = history["sma200"].iloc[index]

  return sma200 < sma150 < sma50 < price_low



def evaluate_trend(
    history: pd.DataFrame,
    index: int,
    is_retained: bool,
    entry_price: float,
    highest_price: float,
) -> str:
  """
  5일 고가 돌파 + 트레일링 스탑 기반 추세 추종 전략.

  - 진입: 종가가 최근 5일 고가 이상일 때
  - 청산: 최고가 대비 38% 이상 밀릴 때 (트레일링 스탑)

  반환값:
    - "ENTER"
    - "EXIT"
    - "HOLD"
  """
  trailing_stop = 0.38
  breakout_lookback = 2
  price_close = history["Close"].iloc[index]

  recent_high = history["Close"].rolling(window=breakout_lookback).max().iloc[index]
  if pd.isna(recent_high):
    return "HOLD"

  # 진입: 최근 5일 고가 이상을 돌파했을 때만 진입한다.
  if not is_retained:
    return "ENTER" if price_close >= recent_high else "HOLD"

  # 보유 중이면 최고가 대비 38% 이상 밀릴 때 청산한다.
  if highest_price and price_close <= highest_price * (1 - trailing_stop):
    return "EXIT"

  return "HOLD"
