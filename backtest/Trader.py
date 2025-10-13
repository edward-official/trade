import yfinance as yf
target = yf.Ticker("QQQ")
history = target.history(period="max")
daysInHistory = len(history)

isRetained = False
balance = 100
entryPrice = 0
currentPrice = 0
highest = 0
tradingRecords = []
recentIndex = 0

def evaluateTrend(index):
  global entryPrice, isRetained, highest
  date = history.index[index].date()
  priceOpen = history['Open'].iloc[index]
  priceClose = history['Close'].iloc[index]
  priceHigh = history['High'].iloc[index]
  priceLow = history['Low'].iloc[index]
  sma50 = history['Close'].rolling(window=50).mean().iloc[index]
  sma150 = history['Close'].rolling(window=150).mean().iloc[index]
  sma200 = history['Close'].rolling(window=200).mean().iloc[index]

  tradingPrice = (priceOpen+priceClose)/2
  if priceOpen<=sma50<=priceClose or priceOpen>=sma50>=priceClose:
    tradingPrice = sma50
  
  if isRetained and entryPrice != 0:
    if tradingPrice < (entryPrice*0.98):
      print(f"🔥 exit: bleeding {entryPrice} > {tradingPrice}: {tradingPrice/entryPrice*100-100}%")
      return "EXIT"
  if isRetained and tradingPrice < highest * 0.8:
    print(f"🔥🔥🔥🔥🔥🔥🔥🔥 exit: drop from high")
    return "EXIT"
  if isRetained and tradingPrice < sma50:
    print(f"🔥 exit: below the 50-day average")
    return "EXIT"
  if tradingPrice > sma50 > sma150 > sma200:
    return "UP"
  

def movement(index):
  global isRetained, entryPrice, currentPrice, balance, highest, tradingRecords
  date = history.index[index].date()
  priceOpen = history['Open'].iloc[index]
  priceClose = history['Close'].iloc[index]
  priceHigh = history['High'].iloc[index]
  priceLow = history['Low'].iloc[index]
  sma50 = history['Close'].rolling(window=50).mean().iloc[index]
  sma150 = history['Close'].rolling(window=150).mean().iloc[index]
  sma200 = history['Close'].rolling(window=200).mean().iloc[index]

  tradingPrice = (priceOpen+priceClose)/2
  if priceOpen<sma50<priceClose or priceOpen>sma50>priceClose:
    tradingPrice = sma50
  currentPrice = tradingPrice
  profitRatio = (tradingPrice / entryPrice) * 100 - 100
  if entryPrice==0:
    profitRatio=0
  if isRetained and highest < tradingPrice:
    print(f"🚨 new highest: {tradingPrice}")
    highest = tradingPrice

  trend = evaluateTrend(index)
  if trend=="UP" and not isRetained:
    isRetained = True
    entryPrice = tradingPrice
    print()
    print(f"✅ [{date}]  PRICE: {tradingPrice:<8.2f}({profitRatio:>5.2f}%) 50: {sma50:<8.2f} 150: {sma150:<8.2f} 200: {sma200:<8.2f}")
    return
  elif trend=="EXIT" and isRetained:
    isRetained = False
    if entryPrice==0:
      return
    print(f"❌ [{date}]  PRICE: {tradingPrice:<8.2f}({profitRatio:>5.2f}%) 50: {sma50:<8.2f} 150: {sma150:<8.2f} 200: {sma200:<8.2f}")
    balance = (tradingPrice / entryPrice) * balance
    profitRatio = (tradingPrice / entryPrice) * 100 - 100
    print(f"💻 balance: {balance:.2f} , profit: {profitRatio:.2f}%")
    # print()
    tradingRecords.append(float(profitRatio))
    entryPrice = 0
    highest = 0
    print(f"🚨 reset highest: {highest}")
    return
  # elif isRetained:
    # print(f"👀 [{date}]  PRICE: {tradingPrice:<8.2f}({profitRatio:>5.2f}%) 50: {sma50:<8.2f} 150: {sma150:<8.2f} 200: {sma200:<8.2f}")


def backtest(daysInHistory):
  global balance
  for index in range(daysInHistory-200):
    movement(index+200)
  print()

  if isRetained:
    tradingRecords.append(currentPrice/entryPrice*100)
    balance = (currentPrice/entryPrice)*balance

  print(f"🔎 record of trade profit ratio in ascending order")
  for ratio in sorted(tradingRecords):
    print(f"{ratio:>6.2f}%")
  print()

  veryFirstPrice = history['Open'].iloc[0]
  veryRecentPrice = history['Open'].iloc[-1]
  natureProfit = 100 * (veryRecentPrice/veryFirstPrice)

  print(f"opening date: {history.index[0].date()}")
  print(f"closing date: {history.index[-1].date()}")
  print(f"total balance: {balance:.2f}")
  print(f"nature profit: {natureProfit:.2f}")
  if balance > natureProfit:
    print("🎉 WIN 🎉")
  else:
    print("❌ LOSE ❌")

backtest(daysInHistory)
