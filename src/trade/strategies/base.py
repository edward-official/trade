from abc import ABC, abstractmethod
import pandas as pd


class Strategy(ABC):
    @abstractmethod
    def prepare_data(self, history: pd.DataFrame) -> pd.DataFrame:
        """
        백테스트 전 데이터를 가공하거나 보조지표를 계산합니다.
        """
        pass

    @abstractmethod
    def evaluate(
        self,
        history: pd.DataFrame,
        index: int,
        is_retained: bool,
        entry_price: float,
        highest_price: float,
    ) -> str:
        """
        특정 시점(index)의 데이터를 기반으로 매매 판단을 내립니다.
        반환값: "ENTER", "EXIT", "HOLD"
        """
        pass
