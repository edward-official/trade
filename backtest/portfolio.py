from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional

import pandas as pd

from .data import get_history
from .strategy import add_moving_averages, is_on_up_trend

# Core risk controls
MAX_ALLOC_PER_TICKER = 0.20    # 20% cap per ticker
TRANCHE_FRACTION = 0.05        # each buy/sell tranche = 5% of portfolio
TRAILING_STOP_PCT = 0.15       # lock profits if price drops 15% from highest
RISK_CUTOFF = 0.01             # cut a ticker if loss hits 1% of total equity


@dataclass
class Position:
  shares: float = 0.0
  avg_cost: float = 0.0
  highest_price: float = 0.0
  trailing_stop: float = 0.0
  last_price: Optional[float] = None

  def value(self, price: Optional[float]) -> float:
    return 0.0 if price is None else self.shares * price

  def reset(self) -> None:
    self.shares = 0.0
    self.avg_cost = 0.0
    self.highest_price = 0.0
    self.trailing_stop = 0.0


def _prepare_history(ticker: str, warmup: int, use_cache: bool) -> pd.DataFrame:
  history = get_history(ticker, period="max", use_cache=use_cache)
  history = add_moving_averages(history)
  uptrend_flags = [False] * len(history)
  for i in range(len(history)):
    if i < warmup:
      continue
    uptrend_flags[i] = is_on_up_trend(history, i)
  history = history.copy()
  history["uptrend"] = uptrend_flags
  return history


def _union_dates(histories: Dict[str, pd.DataFrame]) -> List[pd.Timestamp]:
  all_dates = set()
  for df in histories.values():
    all_dates.update(df.index)
  return sorted(all_dates)


def run_portfolio_backtest(
    tickers: Iterable[str],
    *,
    initial_balance: float = 100.0,
    warmup: int = 200,
    show_trades: bool = True,
    use_cache: bool = True,
    log_limit: int = 80,
    log_path: Optional[str] = None,
    per_ticker_log_dir: Optional[str] = None,
    print_to_console: bool = True,
) -> None:
  tickers = list(tickers)
  histories = {
    ticker: _prepare_history(ticker, warmup, use_cache) for ticker in tickers
  }
  all_dates = _union_dates(histories)

  positions: Dict[str, Position] = {ticker: Position() for ticker in tickers}
  cash = initial_balance

  def equity(prices: Dict[str, Optional[float]]) -> float:
    return cash + sum(positions[t].value(prices.get(t)) for t in tickers)

  trade_log: List[str] = []
  skipped_logs = 0
  trade_counts: Dict[str, Dict[str, int]] = {
    ticker: {"BUY": 0, "SELL": 0, "EXIT": 0} for ticker in tickers
  }
  full_trade_log: List[str] = []
  ticker_trade_logs: Dict[str, List[str]] = {ticker: [] for ticker in tickers}
  log_output: List[str] = []

  def out(msg: str = "") -> None:
    if print_to_console:
      print(msg)
    log_output.append(msg)

  def log_trade(
      action: str,
      ticker: str,
      price: float,
      _reason: str,
      *,
      shares_after: float,
      avg_cost_after: float,
      profit_amt: Optional[float] = None,
      portfolio_equity: Optional[float] = None,
  ) -> None:
    nonlocal skipped_logs
    if action in trade_counts[ticker]:
      trade_counts[ticker][action] += 1
    if not show_trades or log_limit <= 0:
      return
    action_label = {"BUY": "매수", "SELL": "매도", "EXIT": "청산"}.get(action, action)
    hold_value = price * shares_after
    parts = [
      f"{current_date.date()}",
      f"{action_label:4s}",
      f"{ticker:5s}",
      f"가격 {price:8.2f}",
      f"보유금액 {hold_value:9.2f}",
      f"평단 {avg_cost_after:8.4f}",
    ]
    profit_pct_to_log: Optional[float] = None
    if profit_amt is not None:
      if portfolio_equity:
        profit_pct_to_log = profit_amt / portfolio_equity * 100
      else:
        profit_pct_to_log = 0.0
    if profit_pct_to_log is not None and profit_amt is not None:
      parts.extend([
        f"수익률 {profit_pct_to_log:6.2f}%",
        f"수익금 {profit_amt:8.2f}",
      ])
    entry = " | ".join(parts)
    if len(trade_log) >= log_limit:
      trade_log.pop(0)  # keep the most recent trades
      skipped_logs += 1
    trade_log.append(entry)
    full_trade_log.append(entry)
    ticker_trade_logs[ticker].append(entry)

  def sell_all(ticker: str, price: float, reason: str) -> None:
    nonlocal cash
    pos = positions[ticker]
    if pos.shares <= 0:
      return
    avg_before = pos.avg_cost
    shares_before = pos.shares
    portfolio_equity = equity(price_book)
    proceeds = shares_before * price
    cash += proceeds
    profit_amt = (price - avg_before) * shares_before
    log_trade(
      "EXIT",
      ticker,
      price,
      reason,
      shares_after=0.0,
      avg_cost_after=0.0,
      profit_amt=profit_amt,
      portfolio_equity=portfolio_equity,
    )
    pos.reset()

  def sell_tranche(ticker: str, price: float, tranche_value: float, reason: str) -> None:
    nonlocal cash
    pos = positions[ticker]
    if pos.shares <= 0:
      return
    avg_before = pos.avg_cost
    portfolio_equity = equity(price_book)
    sell_value = min(tranche_value, pos.value(price))
    if sell_value <= 0:
      return
    shares_to_sell = sell_value / price
    pos.shares -= shares_to_sell
    cash += sell_value
    profit_amt = (price - avg_before) * shares_to_sell
    if pos.shares <= 1e-9:
      pos.reset()
    log_trade(
      "SELL",
      ticker,
      price,
      reason,
      shares_after=pos.shares,
      avg_cost_after=pos.avg_cost,
      profit_amt=profit_amt,
      portfolio_equity=portfolio_equity,
    )

  def buy_tranche(ticker: str, price: float, tranche_value: float, reason: str) -> None:
    nonlocal cash
    if tranche_value <= 0 or cash <= 0:
      return
    buy_value = min(tranche_value, cash)
    shares = buy_value / price
    pos = positions[ticker]
    new_total_shares = pos.shares + shares
    pos.avg_cost = (
        (pos.avg_cost * pos.shares + buy_value) / new_total_shares
        if new_total_shares > 0 else 0.0
    )
    pos.shares = new_total_shares
    pos.highest_price = max(pos.highest_price, price)
    pos.trailing_stop = pos.highest_price * (1 - TRAILING_STOP_PCT)
    cash -= buy_value
    log_trade(
      "BUY",
      ticker,
      price,
      reason,
      shares_after=pos.shares,
      avg_cost_after=pos.avg_cost,
    )

  price_book: Dict[str, Optional[float]] = {ticker: None for ticker in tickers}

  for current_date in all_dates:
    # Refresh prices for the day.
    for ticker, df in histories.items():
      if current_date in df.index:
        todays_row = df.loc[current_date]
        # If duplicate index entries exist, take the last one.
        if isinstance(todays_row, pd.DataFrame):
          todays_row = todays_row.iloc[-1]
        price_book[ticker] = float(todays_row["Close"])
      # otherwise keep previous price_book value (carry value for equity calc)

    total_equity = equity(price_book)

    for ticker, df in histories.items():
      pos = positions[ticker]
      if current_date not in df.index:
        continue

      idx = df.index.get_loc(current_date)
      if isinstance(idx, slice):
        idx = idx.stop - 1  # use last occurrence if duplicates

      price = price_book[ticker]
      if price is None:
        continue

      prev_price = pos.last_price
      pos.last_price = price

      if pos.shares > 0 and price > pos.highest_price:
        pos.highest_price = price
        pos.trailing_stop = pos.highest_price * (1 - TRAILING_STOP_PCT)

      unrealized_loss = max(0.0, pos.avg_cost * pos.shares - pos.value(price))
      if pos.shares > 0 and unrealized_loss >= total_equity * RISK_CUTOFF:
        sell_all(ticker, price, "loss >= 1% portfolio")
        total_equity = equity(price_book)
        continue

      if pos.shares > 0 and pos.trailing_stop and price <= pos.trailing_stop:
        sell_all(ticker, price, "trailing stop")
        total_equity = equity(price_book)
        continue

      price_increasing = prev_price is None or price > prev_price
      price_decreasing = prev_price is not None and price < prev_price

      if price_decreasing and pos.shares > 0:
        tranche_value = total_equity * TRANCHE_FRACTION
        sell_tranche(ticker, price, tranche_value, "price down")
        total_equity = equity(price_book)

      uptrend = bool(df["uptrend"].iloc[idx])
      if price_increasing and uptrend:
        tranche_value = total_equity * TRANCHE_FRACTION
        max_value = total_equity * MAX_ALLOC_PER_TICKER
        current_value = positions[ticker].value(price)
        allowable_value = max_value - current_value
        buy_value = min(tranche_value, allowable_value)
        if buy_value > 0:
          buy_tranche(ticker, price, buy_value, "uptrend & price up")
          total_equity = equity(price_book)

  final_equity = equity(price_book)
  out()
  out(f"전략 이름   : 멀티에셋 포트폴리오 ({', '.join(tickers)})")
  out(f"종료 일자   : {all_dates[-1].date() if all_dates else 'n/a'}")
  out(f"최종 자산   : {final_equity:,.2f}")
  out(f"현금 잔고   : {cash:,.2f}")
  for ticker in tickers:
    price = price_book[ticker]
    value = positions[ticker].value(price)
    if value > 0:
      alloc = value / final_equity * 100 if final_equity else 0
      out(f"- 보유 {ticker}: 평가액 {value:,.2f} ({alloc:.2f}%)")
  if show_trades and log_limit > 0 and trade_log:
    out()
    out(f"🔎 최근 거래 기록 (최대 {log_limit}건, 이전 {skipped_logs}건 생략)")
    for entry in trade_log:
      out(entry)

  if log_path:
    header_line = "✅ 백테스트 완료"
    path = Path(log_path)
    if path.parent:
      path.parent.mkdir(parents=True, exist_ok=True)
    log_lines = [header_line]
    log_lines.extend(log_output)
    if full_trade_log:
      log_lines.append("")
      log_lines.append("🔎 전체 거래 기록")
      log_lines.extend(full_trade_log)
    path.write_text("\n".join(log_lines) + ("\n" if log_lines else ""), encoding="utf-8")

  if per_ticker_log_dir:
    dir_path = Path(per_ticker_log_dir)
    dir_path.mkdir(parents=True, exist_ok=True)
    for ticker, entries in ticker_trade_logs.items():
      lines = [f"🔎 {ticker} 거래 기록"]
      if entries:
        lines.extend(entries)
      else:
        lines.append("거래 없음")
      file_path = dir_path / f"{ticker}_backtest.log"
      file_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
