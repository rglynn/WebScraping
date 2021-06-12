# WebScraping
All my web scraping side-projects.

Feel free to visit https://www.ryanglynn.com for additional stuff and check out my other repos here.




# **Zillow Mortgage Rates**
This script was written for a local Splunk collector (running on my home computer) to scrape [Zillow's current mortgage rates](https://www.zillow.com/mortgage-rates/#/ "Zillow's current mortgage rates")  on a daily basis (excludes Government Loans).

It then writes the Date, Loan Type, Program, Rate, Rate Change, APR, and APR change to a CSV for Splunk ingestion. If you use this for your own splunk environment you would most likely have to modify the chrome driver location as Splunk does not like default Chrome Driver paths.
