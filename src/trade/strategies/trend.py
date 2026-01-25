import pandas as pd
from trade.strategies.base import Strategy


class TrendStrategy(Strategy):
    """
    강화된 추세 추종 전략 (BUY&HOLD 대비 초과 수익을 노림).
    """

    def prepare_data(self, history: pd.DataFrame) -> pd.DataFrame:
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

    def evaluate(
        self,
        history: pd.DataFrame,
        index: int,
        is_retained: bool,
        entry_price: float,
        highest_price: float,
    ) -> str:
        """
        - 필터: 종가가 sma150·sma200 위에 있고, 두 이동평균이 상승 중일 때만 매수/보유
        - 진입: 최근 20일 고가 돌파 시 진입
        - 청산: 150/200일선 이탈 시 즉시 청산, 또는 최고가 대비 20% 이상 하락 시 청산
        """
        trailing_stop = 0.20
        breakout_lookback = 20
        price_close = history["Close"].iloc[index]
        sma150 = history["sma150"].iloc[index]
        sma200 = history["sma200"].iloc[index]

        if pd.isna(sma150) or pd.isna(sma200):
            return "HOLD"

        prev_sma150 = history["sma150"].iloc[index - 1] if index > 0 else sma150
        prev_sma200 = history["sma200"].iloc[index - 1] if index > 0 else sma200
        slope_ok = sma150 > prev_sma150 and sma200 >= prev_sma200

        # 장기 추세 이탈 시 즉시 청산, 이탈 구간에서는 매수하지 않음
        if price_close <= sma150 or price_close <= sma200:
            return "EXIT" if is_retained else "HOLD"

        recent_high = (
            history["Close"].rolling(window=breakout_lookback).max().iloc[index]
        )
        if pd.isna(recent_high):
            return "HOLD"

        # 진입: 장기 추세 상방 & 상승 기울기 + 20일 고가 돌파
        if not is_retained:
            return "ENTER" if (price_close >= recent_high and slope_ok) else "HOLD"

        # 보유 중이면 최고가 대비 20% 이상 밀릴 때 청산
        if highest_price and price_close <= highest_price * (1 - trailing_stop):
            return "EXIT"

        return "HOLD"
