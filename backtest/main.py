import yfinance as yf
target = yf.Ticker("TSLA")
history = target.history(period="max")
numberOfDays = len(history)


def isOnUpTrend(history, index):
  priceLow = history['Low'].iloc[index]
  sma50 = history['Close'].rolling(window=50).mean().iloc[index]
  sma150 = history['Close'].rolling(window=150).mean().iloc[index]
  sma200 = history['Close'].rolling(window=200).mean().iloc[index]

  if sma200 < sma150 < sma50 < priceLow:
    return True
  else:
    return False


def manager(history, index, highestPrice):
  date = history.index[index].date()
  priceOpen = history['Open'].iloc[index]
  priceClose = history['Close'].iloc[index]
  priceHigh = history['High'].iloc[index]
  priceLow = history['Low'].iloc[index]
  sma50 = history['Close'].rolling(window=50).mean().iloc[index]
  sma150 = history['Close'].rolling(window=150).mean().iloc[index]
  sma200 = history['Close'].rolling(window=200).mean().iloc[index]

  if not isOnUpTrend(history, index-1) and isOnUpTrend(history, index):
    return "ENTER"
  elif not isOnUpTrend(history, index):
    return "EXIT"
  # elif priceOpen < highestPrice * 0.9:
  #   return "EXIT"


def backtest(history):
  enteredPrice = 0
  highestPrice = 0
  balance = 100
  recordsOfRate = []

  for index in range(numberOfDays-200):
    date = history.index[index].date()
    priceOpen = history['Open'].iloc[index]
    priceClose = history['Close'].iloc[index]
    priceHigh = history['High'].iloc[index]
    priceLow = history['Low'].iloc[index]
    sma50 = history['Close'].rolling(window=50).mean().iloc[index]
    sma150 = history['Close'].rolling(window=150).mean().iloc[index]
    sma200 = history['Close'].rolling(window=200).mean().iloc[index]
    
    action = manager(history, index, highestPrice)
    if enteredPrice == 0 and action == "ENTER":
      print(f"✅ [{date}]: open: {priceOpen:5.2f}, close: {priceClose:5.2f}, 50: {sma50:5.2f}, 150: {sma150:5.2f}, 200: {sma200:5.2f}")
      enteredPrice = history["Open"].iloc[index]
      highestPrice = history["High"].iloc[index]
    elif enteredPrice != 0 and action == "EXIT":
      exitingPrice = history["Open"].iloc[index]
      interestRate = (exitingPrice / enteredPrice) * 100 - 100
      recordsOfRate.append(interestRate)
      print(f"❌ [{date}]: open: {priceOpen:5.2f}, close: {priceClose:5.2f}, 50: {sma50:5.2f}, 150: {sma150:5.2f}, 200: {sma200:5.2f}")
      print(f"🔎 entered price: {enteredPrice:7.2f}, interest rate: {interestRate:6.2f}%")
      print()
      balance = balance * (exitingPrice / enteredPrice)
      enteredPrice = 0
      highestPrice = 0
    elif highestPrice < priceHigh:
      highestPrice = priceHigh

  for rate in sorted(recordsOfRate):
    print(f"{rate:5.2f}%")
  opponent = 100 * (history["Close"].iloc[-1] / history["Open"].iloc[0])
  print(f"💻 balance : {balance}")
  print(f"💻 opponent: {opponent}")
  return


backtest(history)
