buyingPrice = 100

def isBleeding(tradingPrice):
  global buyingPrice
  if buyingPrice != 0 and tradingPrice < (buyingPrice * 95 / 100):
    return True
  else:
    return False

print(isBleeding(100))
print(isBleeding(90))