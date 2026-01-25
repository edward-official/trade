from dataclasses import dataclass
from typing import Optional

@dataclass
class Position:
    shares: float = 0.0
    avg_cost: float = 0.0
    highest_price: float = 0.0
    trailing_stop: float = 0.0  # e.g., highest_price * (1 - TRAILING_STOP_PCT)
    last_price: Optional[float] = None

    def value(self, price: Optional[float]) -> float:
        return 0.0 if price is None else self.shares * price

    def reset(self) -> None:
        self.shares = 0.0
        self.avg_cost = 0.0
        self.highest_price = 0.0
        self.trailing_stop = 0.0
        self.last_price = None
