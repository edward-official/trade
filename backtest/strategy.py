import pandas as pd


def add_moving_averages(history: pd.DataFrame) -> pd.DataFrame:
  """
  history DataFrame에 50/150/200일 이동평균선을 미리 계산해서 컬럼으로 추가한다.

  컬럼 이름:
    - sma50
    - sma150
    - sma200
  """
  close = history["Close"]
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
  QQQ 장기 백테스트용 200일 이동평균 기반 리스크 관리 전략.

  - 진입:
      * 종가가 200일선 위로 1% 이상 돌파
  - 청산:
      * 종가가 200일선 아래로 내려갈 때
      * 또는 최고가 대비 15% 이상 하락 (트레일링 스탑)

  반환값:
    - "ENTER"
    - "EXIT"
    - "HOLD"
  """
  price_close = history["Close"].iloc[index]
  sma200 = history["sma200"].iloc[index]

  if not is_retained:
    if price_close > sma200 * 1.01:
      return "ENTER"
    return "HOLD"

  if is_retained and entry_price:
    if price_close < sma200:
      return "EXIT"
    if highest_price and price_close < highest_price * 0.85:
      return "EXIT"

  return "HOLD"
