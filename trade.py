import yfinance as yf

qqq = yf.Ticker("QQQ")
price = qqq.info['regularMarketPrice']
history = qqq.history(period="60d")

print(f"QQQ 현재 주가: ${price}")
print(history['Close'])
