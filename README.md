# WebScraping
All my web scraping side-projects.

Feel free to visit https://www.ryanglynn.com for additional stuff and check out my other repos here.




# **Zillow Mortgage Rates**
This script was written for a local Splunk collector (running on my home computer) to scrape [Zillow's current mortgage rates](https://www.zillow.com/mortgage-rates/#/ "Zillow's current mortgage rates")  on a daily basis (excludes Government Loans).

It then writes the Date, Loan Type, Program, Rate, Rate Change, APR, and APR change to a CSV for Splunk ingestion. If you use this for your own splunk environment you would most likely have to modify the chrome driver location as Splunk does not like default Chrome Driver paths.


# **Goochland_Permit_Scrape**

This script will take an input of any GPIN (unique identifier for a plot of land) and scrape the ownership (assuming it's in Goochland county). This can be used to essentially monitor for when plots of change within the county change. For example, if you wanted to know if certain plots of land were sold you can have this script run once per day and it will print out if anything changes as well as writing the newest results to the CSV.

# **Stock_Scraping**

This script will pull in a list of stocks (located in lookups/stock_list) and iterate through the historical stock open/close prices since the last date recorded in stock_list. Can go back as far as 1998. This also calculates High, Low, Close, Adj Close, Volume, Up Move, Down Move, Average Up, Average DOwn, RS, RSI, MACD, smacd ShortEMA, LongEMA, MACD Histogram, and OBV values.

This was also written for Splunk ingestion so the script also includes a cleanup clause to auto delete the files once per day. You can always reload the historcal files by manually changing the date marker in the "stock_list" file. If you would like to see a sample output, check out data/stocks/AAPL_06_11_2021.csv which is a sample from running with a single Stock in the stock list set to the date of 6/1/2021.
