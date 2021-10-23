# MACD-BackTest

In the attempt to understand how effective using the MACD indicator as a part of my trading strategy
for intraday algorithmic trading, I decided to back test the strategy by applying it to multiple securities
over the same period of time. For consistency I used September 1st 2020 to September 1st 2021.

    #Calculate the MACD and Signal line indicators
    #Calculate the short term emponential moving averaga (EMA)
    ShortEMA = df.Close.ewm(span=12, adjust=False).mean()
    #Calculate the long term emponential moving averaga (EMA)
    LongEMA = df.Close.ewm(span=26, adjust=False).mean()
    #Calculate the MACD line
    MACD = ShortEMA - LongEMA
    #Calculate the signal line
    signal = MACD.ewm(span=9, adjust=False).mean()
    
As september is usally when we see the most Bear change and the fall of 2020 and the year of 2021 causing
very irregular activity in the market, I understand that I would have to test this same method over multiple 
periods of time as well. This is the reason I decided to codify this test rather than use an excel spread sheet,
because with this code I can now enter as many ticker symbols I want to test in the 'tickers list' and import datasets
from which ever period of time I pull a history data URL from.

    tickers = ['NFLX', 'VZ', 'TSLA', 'AMD', 'NVDA']
      df = pd.read_csv(f'https://query1.finance.yahoo.com/v7/finance/download/{tickers[i]}?period1=1598918400&period2=1630454400&interval=1d&events=history&includeAdjustedClose=true')
      df = df.set_index(pd.DatetimeIndex(df['Date'].values))
      del df['Date']
    
Because I want to get a general sense of how these results would compare over many trials I decided to use these 
trials over time to generate a dataset that I can store to later analyze. The most important column of information for
me would be the percentage gain or loss of income over the passage of alloted time (1 year in this test case). For this
reason i set up a few blank lists at the outset of the code run that will be populated at the run of each loop.

    stprice = []
    empsum = []
    pctg = []
    ...
        stprice.append(startprice)
        empsum.append(empirical_sum)
        pctg.append(pct_gains)


    macdtest = pd.DataFrame(list(zip(tickers,stprice,empsum,pctg)), columns=['Ticker','Start_Price', 'Emperical_Sum', 'Percent_Gain'])
    print(macdtest)

Each of these variable were calculated after the manipulation of the original dataset derived from yahoo finance. 
From which, as described above, both the MACD and Signal lines were generated so that we can use the code chunk below
to identify some buying and selling signals.


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

  #Create buy and sell column
  a = buy_sell(df)
  df['Buy_Signal_Price'] = a[0]
  df['Sell_Signal_Price'] = a[1]
    
Above, when data point 'a' is greater than point 'b', all is good. When datapoint becomes greater than 'a' in the same 
row of data, I am notified once, and mark value in a list of values for when the value 'a' becomes less than 'b'. 
(append close price as sell price to sell list)

From there, we continue to monitor whether there is ever an instance when value of 'a' ever becomes greater than value 
'b' within the same row again. I am notified of that instance, and record that instance, in the appropriate list. 
(append close price as buy price to buy list)

Having set up these new rows of data indicating when values are set for buying at selling at close price, we can 
quantify the wins and losses using this strategy by using more dataframe manipulation, as shown below:

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
    
 ..and that is how we get our values to fill the new dataframe that I can use for analysis of this stategy.

