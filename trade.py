import yfinance as yf
qqq = yf.Ticker("QQQ")
history = qqq.history(period="800d")

balance = 100
buyingPrice = 0
tradingRecords = []
recentIndex = 0

def evaluateTrend(index):
  date = history.index[index].date()
  priceOpen = history['Open'].iloc[index]
  priceClose = history['Close'].iloc[index]
  priceHigh = history['High'].iloc[index]
  priceLow = history['Low'].iloc[index]
  sma50 = history['Close'].rolling(window=50).mean().iloc[index]
  sma150 = history['Close'].rolling(window=150).mean().iloc[index]
  sma200 = history['Close'].rolling(window=200).mean().iloc[index]

  if priceClose > sma50 > sma150 > sma200:
    return "UP"
  elif priceClose < sma50 < sma150 < sma200:
    return "DOWN"
  else:
    return "SIDEWAY"

def movement(index):
  global buyingPrice, balance
  date = history.index[index].date()
  priceOpen = history['Open'].iloc[index]
  priceClose = history['Close'].iloc[index]
  priceHigh = history['High'].iloc[index]
  priceLow = history['Low'].iloc[index]
  sma50 = history['Close'].rolling(window=50).mean().iloc[index]
  sma150 = history['Close'].rolling(window=150).mean().iloc[index]
  sma200 = history['Close'].rolling(window=200).mean().iloc[index]

  if evaluateTrend(index-1)!="UP" and evaluateTrend(index)=="UP":
    print(f"✅ [{date}]  CLOSE: {priceClose:<8.2f} 50: {sma50:<8.2f} 150: {sma150:<8.2f} 200: {sma200:<8.2f}")
    buyingPrice = priceClose
    return
  elif evaluateTrend(index-1)=="UP" and evaluateTrend(index)!="UP":
    if buyingPrice==0:
      return
    print(f"❌ [{date}]  CLOSE: {priceClose:<8.2f} 50: {sma50:<8.2f} 150: {sma150:<8.2f} 200: {sma200:<8.2f}")
    balance = (priceClose / buyingPrice) * balance
    profitRatio = (priceClose / buyingPrice) * 100 - 100
    print(f"💻 balance: {balance:.2f} , profit: {profitRatio:.2f}%")
    print()
    tradingRecords.append(float(profitRatio))
    return

for index in range(600):
  movement(index+200)
print()

print(f"opening date: {history.index[0].date()}")
print(f"closing date: {history.index[-1].date()}")
print(f"total balance: {balance:.2f}")
print()

print(f"🔎 record of trade profit ratio in ascending order")
for ratio in sorted(tradingRecords):
  print(f"{ratio:>6.2f}%")