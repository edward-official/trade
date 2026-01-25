from pathlib import Path
from typing import List, Optional

from trade.data import get_history
from trade.strategies import add_moving_averages, evaluate_trend


def run_single_backtest(
    ticker: str,
    *,
    initial_balance: float = 100.0,
    warmup: int = 200,
    show_trades: bool = True,
    use_cache: bool = True,
    log_limit: int = 80,
    log_dir: Optional[str] = "backtests/single",
    print_to_console: bool = True,
) -> None:
  """
  Run a single-ticker breakout/trailing-stop backtest.

  - 엔트리: 최근 고가 돌파 시 자본 100% 매수
  - 청산: 최고가 대비 20% 이상 하락 시 전량 청산
  - 결과는 log_dir/{ticker}_backtest.log 에 기록한다.
  """
  history = get_history(ticker, period="max", use_cache=use_cache)
  history = add_moving_averages(history)

  cash = initial_balance
  shares = 0.0
  avg_cost = 0.0
  highest_price = 0.0
  last_price: Optional[float] = None
  buy_hold_entry: Optional[float] = None
  buy_hold_final: Optional[float] = None

  trade_log: List[str] = []
  full_trade_log: List[str] = []
  log_output: List[str] = []
  skipped_logs = 0

  def out(msg: str = "") -> None:
    if print_to_console:
      print(msg)
    log_output.append(msg)

  def log_trade(
      date_obj,
      action: str,
      price: float,
      *,
      shares_after: float,
      avg_cost_after: float,
      profit_amt: Optional[float] = None,
      profit_pct: Optional[float] = None,
  ) -> None:
    nonlocal skipped_logs
    if not show_trades or log_limit <= 0:
      return
    action_label = {"BUY": "매수", "EXIT": "청산"}.get(action, action)
    hold_value = price * shares_after
    parts = [
      f"{date_obj.date()}",
      f"{action_label:4s}",
      f"{ticker:5s}",
      f"가격 {price:8.2f}",
      f"보유금액 {hold_value:9.2f}",
      f"평단 {avg_cost_after:8.4f}",
    ]
    if profit_amt is not None:
      pct = 0.0 if profit_pct is None else profit_pct
      parts.extend([
        f"수익률 {pct:6.2f}%",
        f"수익금 {profit_amt:8.2f}",
      ])
    entry = " | ".join(parts)
    if len(trade_log) >= log_limit:
      trade_log.pop(0)
      skipped_logs += 1
    trade_log.append(entry)
    full_trade_log.append(entry)

  for idx, current_date in enumerate(history.index):
    if idx < warmup:
      if idx == warmup - 1 and len(history) > warmup:
        buy_hold_entry = float(history["Close"].iloc[idx + 1])
      continue

    price_close = float(history["Close"].iloc[idx])
    last_price = price_close

    if shares > 0 and price_close > highest_price:
      highest_price = price_close

    decision = evaluate_trend(
      history=history,
      index=idx,
      is_retained=shares > 0,
      entry_price=avg_cost,
      highest_price=highest_price,
    )

    if decision == "ENTER" and shares <= 0 and cash > 0:
      buy_value = cash
      shares = buy_value / price_close
      avg_cost = price_close
      highest_price = price_close
      cash -= buy_value
      log_trade(
        current_date,
        "BUY",
        price_close,
        shares_after=shares,
        avg_cost_after=avg_cost,
      )
      continue

    if decision == "EXIT" and shares > 0:
      position_value = shares * price_close
      profit_amt = position_value - (avg_cost * shares)
      profit_pct = (
        (profit_amt / (avg_cost * shares)) * 100
        if shares > 0 and avg_cost > 0 else 0.0
      )
      cash += position_value
      shares = 0.0
      avg_cost = 0.0
      highest_price = 0.0
      log_trade(
        current_date,
        "EXIT",
        price_close,
      shares_after=shares,
      avg_cost_after=avg_cost,
      profit_amt=profit_amt,
      profit_pct=profit_pct,
    )

  position_value = shares * last_price if last_price is not None else 0.0
  final_equity = cash + position_value
  if buy_hold_entry and last_price:
    buy_hold_final = initial_balance * (last_price / buy_hold_entry)

  out()
  out(f"전략 이름   : 단일 종목 추세 추종 ({ticker})")
  out(f"종료 일자   : {history.index[-1].date() if len(history) else 'n/a'}")
  out(f"최종 자산   : {final_equity:,.2f}")
  out(f"현금 잔고   : {cash:,.2f}")
  if buy_hold_final:
    diff = final_equity - buy_hold_final
    diff_pct = (diff / buy_hold_final * 100) if buy_hold_final else 0.0
    verdict = "전략 우세" if diff > 0 else "BUY&HOLD 우세" if diff < 0 else "동률"
    out(
        f"비교(BUY&HOLD) 최종 자산: {buy_hold_final:,.2f} "
        f"({verdict}, 격차 {diff:,.2f}, {diff_pct:.2f}%)"
    )
  if shares > 0:
    out(f"- 보유 {ticker}: 평가액 {position_value:,.2f} (평단 {avg_cost:,.2f})")

  if show_trades and log_limit > 0 and trade_log:
    out()
    out(f"🔎 최근 거래 기록 (최대 {log_limit}건, 이전 {skipped_logs}건 생략)")
    for entry in trade_log:
      out(entry)

  if log_dir:
    dir_path = Path(log_dir)
    dir_path.mkdir(parents=True, exist_ok=True)
    file_path = dir_path / f"{ticker}_backtest.log"
    log_lines = ["✅ 백테스트 완료"]
    log_lines.extend(log_output)
    if full_trade_log:
      log_lines.append("")
      log_lines.append("🔎 전체 거래 기록")
      log_lines.extend(full_trade_log)
    file_path.write_text("\n".join(log_lines) + "\n", encoding="utf-8")
