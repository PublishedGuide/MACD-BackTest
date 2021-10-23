import pandas as pd
import matplotlib.pyplot as plt
import json
import numpy as np
import requests

def buy_sell(signal):
  Buy = []
  Sell = []
  flag = -1
  #Flag will tell us whether price continues to rise or fall after point of intersection is detected.
  #The flag will only change when those two lines  cross agian (when there is a momentum shift)

  #in range below, as each row goes, we are trying to determine when the lines cross bu investigating the datapoints
  for i in range(0, len(signal)):
    if signal['MACD'][i] > signal['Signal Line'][i]:
      Sell.append(np.nan)
      if flag != 1:
        Buy.append(signal['Close'][i])
        flag = 1
      else:
        Buy.append(np.nan)

    elif signal['MACD'][i] < signal['Signal Line'][i]:
      Buy.append(np.nan)
      if flag != 0:
        Sell.append(signal['Close'][i])
        flag = 0
      else:
        Sell.append(np.nan)
    else:
      Buy.append(np.nan)
      Sell.append(np.nan)
  return (Buy, Sell)

tickers = ['NFLX', 'VZ', 'TSLA', 'AMD', 'NVDA']

stprice = []
empsum = []
pctg = []

for i in range(0,len(tickers)):

    df = pd.read_csv(f'https://query1.finance.yahoo.com/v7/finance/download/{tickers[i]}?period1=1598918400&period2=1630454400&interval=1d&events=history&includeAdjustedClose=true')
    df = df.set_index(pd.DatetimeIndex(df['Date'].values))
    del df['Date']

    #Calculate the MACD and Signal line indicators
    #Calculate the short term emponential moving averaga (EMA)
    ShortEMA = df.Close.ewm(span=12, adjust=False).mean()
    #Calculate the long term emponential moving averaga (EMA)
    LongEMA = df.Close.ewm(span=26, adjust=False).mean()
    #Calculate the MACD line
    MACD = ShortEMA - LongEMA
    #Calculate the signal line
    signal = MACD.ewm(span=9, adjust=False).mean()

    #Create new columns for the data
    df['MACD'] = MACD
    df['Signal Line'] = signal

    #Create buy and sell column
    a = buy_sell(df)
    df['Buy_Signal_Price'] = a[0]
    df['Sell_Signal_Price'] = a[1]


    #separate the buying and selling signal prices to make it easier to calculat overall earnings or loss potential
    nsums=df.loc[:,['Buy_Signal_Price', 'Sell_Signal_Price']]
    nsums['Buy_Signal_Price'] = nsums['Buy_Signal_Price'].fillna(0)
    nsums['Sell_Signal_Price'] = nsums['Sell_Signal_Price'].fillna(0)
    nsums['Tot_Sig_P'] = nsums['Buy_Signal_Price'] - nsums['Sell_Signal_Price']

    #set an empty list to collect the values that are not 0 or Nan
    pot = []
    #seperate and assign these values to a condensed list
    for s in range(0,len(nsums)):
        if nsums['Tot_Sig_P'][s] != 0:
            pot.append(nsums['Tot_Sig_P'][s])
    #Pull the first value of this set to be used as our emperical starting principle for this test
    startprice = abs(pot[0])
    #Find the empirical result of all the profits and losses as the remaining total earned sum
    empirical_sum = sum(nsums['Tot_Sig_P'])
    #Compared to the starting value what did we end up with?
    pct_gains = (empirical_sum/startprice)*100
    #print(f"startprice = {startprice:.2f}, empirical_sum = {empirical_sum:.2f}, pct_gains = {pct_gains:.2f}%")
    stprice.append(startprice)
    empsum.append(empirical_sum)
    pctg.append(pct_gains)


macdtest = pd.DataFrame(list(zip(tickers,stprice,empsum,pctg)), columns=['Ticker','Start_Price', 'Emperical_Sum', 'Percent_Gain'])
print(macdtest)