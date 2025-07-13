import yfinance as yf
target = yf.Ticker("QQQ")
history = target.history(period="5y")
daysInHistory = len(history)

veryFirstPrice = history['Open'].iloc[0]
veryRecentPrice = history['Open'].iloc[-1]
natureProfit = 100 * (veryRecentPrice/veryFirstPrice)

isRetained = False
balance = 100
entryPrice = 0
tradingRecords = []
recentIndex = 0

def evaluateTrend(index):
  global entryPrice, isRetained
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

  if tradingPrice > sma50 > sma200 or tradingPrice > sma50 > sma150:
    return "UP"
  elif entryPrice == 0 and isRetained:
    print("🚨 ERROR 🚨")
    return "ERROR"
  elif entryPrice == 0:
    return "UNDEFINED"
  elif tradingPrice < sma150 or tradingPrice < sma200:
    return "EXIT"
  elif tradingPrice < (entryPrice*95/100):
    print(f"🔥🔥🔥🔥🔥🔥🔥🔥🔥 {entryPrice} > {tradingPrice}: {tradingPrice/entryPrice*100-100}%")
    return "EXIT"

def movement(index):
  global isRetained, entryPrice, balance
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

  if evaluateTrend(index)=="UP" and not isRetained:
    isRetained = True
    print(f"✅ [{date}]  PRICE: {tradingPrice:<8.2f} 50: {sma50:<8.2f} 150: {sma150:<8.2f} 200: {sma200:<8.2f}")
    entryPrice = tradingPrice
    return
  elif evaluateTrend(index)=="EXIT" and isRetained:
    isRetained = False
    if entryPrice==0:
      return
    print(f"❌ [{date}]  PRICE: {tradingPrice:<8.2f} 50: {sma50:<8.2f} 150: {sma150:<8.2f} 200: {sma200:<8.2f}")
    balance = (tradingPrice / entryPrice) * balance
    profitRatio = (tradingPrice / entryPrice) * 100 - 100
    print(f"💻 balance: {balance:.2f} , profit: {profitRatio:.2f}%")
    print()
    tradingRecords.append(float(profitRatio))
    entryPrice = 0
    return


for index in range(daysInHistory-200):
  movement(index+200)
print()

print(f"🔎 record of trade profit ratio in ascending order")
for ratio in sorted(tradingRecords):
  print(f"{ratio:>6.2f}%")
print()

print(f"opening date: {history.index[0].date()}")
print(f"closing date: {history.index[-1].date()}")
print(f"total balance: {balance:.2f}")
print(f"nature profit: {natureProfit:.2f}")
if balance > natureProfit:
  print("🎉 WIN 🎉")
else:
  print("❌ LOSE ❌")
