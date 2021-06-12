import datetime as dt
import pandas as pd
from datetime import datetime, timedelta
import pandas_datareader.data as web
import re
import glob
import os
import numpy as np

#######################PANDAS READING FILES / LOADING FILES / REGULAR EXPRESSIONS
directory="lookups\\stock_list"
init_df = pd.read_csv(directory)
then = datetime.now()
cur_pull = then.strftime('%m/%d/%Y')
cur_pull_d = str(then.strftime('%m_%d_%Y'))
hp =  re.compile("[^\s]+\s([0-9]+)")
hour = int(hp.match(str(then)).group(1))
now = then.strftime('%m/%d/%Y')
yp = re.compile("[^\/]+\/[^\/]+\/([0-9]{4})$")
yp_s = yp.match(str(cur_pull)).group(1)
year_p = int(yp.match(str(cur_pull)).group(1))

# get a recursive list of file paths that matches pattern including sub directories
if hour <15:
    fileList = glob.glob('data\\stocks\\**.csv', recursive=False)
    # Iterate over the list of filepaths & remove each file.
    for filePath in fileList:
        try:
            os.remove(filePath)
        except OSError:
            print("Error while deleting file")

dp = re.compile("[^\/]+\/([^\/]+)\/[0-9]{4}$")
dp_s = dp.match(str(cur_pull)).group(1)
day_p = int(dp.match(str(cur_pull)).group(1))
mp = re.compile("([^\/]+)\/[^\/]+\/[0-9]{4}$")
mp_s = mp.match(str(cur_pull)).group(1)
month_p = int(mp.match(str(cur_pull)).group(1))
print(mp_s+" "+dp_s+" "+yp_s)

for enum,ticker in enumerate(init_df['Ticker']):
    lp = str(init_df['Last_Pulled'][enum])
    print(lp+" - "+ticker)
    year = int(yp.match(str(lp)).group(1))
    day = int(dp.match(str(lp)).group(1))
    month = int(mp.match(str(lp)).group(1))
    if year_p==year and day_p==day and month_p==month:
        print("Up to date.")
        continue
    else:
        if hour >= 17:
            end = datetime.now()
        else:
            if year_p==year and day_p-1==day and month_p==month:
                continue
            else:
                end = datetime.now() - timedelta(days=1)
    filter_st = str(year)+'-'+str(month)+"-"+str(day)
    start = dt.datetime(1980, 1, 1)
    df = web.DataReader(ticker, 'yahoo', start, end)
    if len(df) < 14:
        continue
    df['Ticker'] = ticker
    df['Date_col'] = df.index
    df = df[['Date_col','Ticker', 'Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']]
    df['Date_col'] = df['Date_col'].dt.strftime('%m/%d/%Y')
    df['Up Move'] = np.nan
    df['Down Move'] = np.nan
    df['Average Up'] = np.nan
    df['Average Down'] = np.nan
    df['OBV'] = np.nan
    # Relative Strength
    df['RS'] = np.nan
    # Relative Strength Index
    df['RSI'] = np.nan
    df['ShortEMA'] = np.nan
    df['LongEMA'] = np.nan
    df['MACD'] = np.nan
    df['OBV'][0] = 0
    for x in range(1, len(df)):
        df['Up Move'][x] = 0
        df['Down Move'][x] = 0
        if df['Adj Close'][x] > df['Adj Close'][x-1]:
            df['Up Move'][x] = df['Adj Close'][x] - df['Adj Close'][x-1]
        if df['Close'][x] > df['Close'][x-1]:
            df['OBV'][x] = df['OBV'][x-1] + df['Volume'][x]
        if df['Adj Close'][x] < df['Adj Close'][x-1]:
            df['Down Move'][x] = abs(df['Adj Close'][x] - df['Adj Close'][x-1])  
        if df['Close'][x] < df['Close'][x-1]:
            df['OBV'][x] = df['OBV'][x-1] - df['Volume'][x]
        if df['Close'][x] == df['Close'][x-1]:
            df['OBV'][x] = df['OBV'][x-1] 
    ## Calculate initial Average Up & Down, RS and RSI
    df['Average Up'][14] = df['Up Move'][1:15].mean()
    df['Average Down'][14] = df['Down Move'][1:15].mean()
    df['RS'][14] = df['Average Up'][14] / df['Average Down'][14]
    df['RSI'][14] = 100 - (100/(1+df['RS'][14]))
    ## Calculate rest of Average Up, Average Down, RS, RSI
    for x in range(15, len(df)):
        df['Average Up'][x] = (df['Average Up'][x-1]*13+df['Up Move'][x])/14
        df['Average Down'][x] = (df['Average Down'][x-1]*13+df['Down Move'][x])/14
        df['RS'][x] = df['Average Up'][x] / df['Average Down'][x]
        df['RSI'][x] = 100 - (100/(1+df['RS'][x]))
    df['ShortEMA'] = df.Close.ewm(span=12, adjust=False).mean() 
    df['LongEMA'] = df.Close.ewm(span=26, adjust=False).mean() 
    df['MACD'] = df['ShortEMA'] - df['LongEMA'] 
    df['smacd'] = df.MACD.ewm(span=9, adjust=False).mean()
    df['macdh'] = df['MACD'] - df['smacd']
    filtered_df = df.loc[( pd.to_datetime(df['Date_col'], format='%m/%d/%Y') > str(filter_st))]   
    if len(filtered_df)>0:
        filtered_df.to_csv(f"data\\stocks\\{ticker}_{cur_pull_d}.csv",index=False)
    init_df['Last_Pulled'][enum] = cur_pull
    
init_df.to_csv(directory,index=False)