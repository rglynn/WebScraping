import urllib.parse
import pandas as pd 
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
import time
import re
import glob
import os
import numpy as np
from datetime import datetime

directory="lookups\\zillow_date"
date_check = test = pd.read_csv(directory)
options = webdriver.ChromeOptions()
user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36'
options.add_argument(f'user-agent={user_agent}')
#options.add_argument("--user-data-dir=chrome-data")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
# options.add_argument("--headless")
# options.add_argument("--auto-open-devtools-for-tabs")

then = datetime.now()
cur_pull = then.strftime('%m/%d/%Y')
cur_pull_d = str(then.strftime('%m_%d_%Y'))
hp =  re.compile("[^\s]+\s([0-9]+)")
hour = int(hp.match(str(then)).group(1))
now = then.strftime('%m/%d/%Y')
yp = re.compile("[^\/]+\/[^\/]+\/([0-9]{4})$")
yp_s = yp.match(str(cur_pull)).group(1)
year_p = int(yp.match(str(cur_pull)).group(1))
dp = re.compile("[^\/]+\/([^\/]+)\/[0-9]{4}$")
dp_s = dp.match(str(cur_pull)).group(1)
day_p = int(dp.match(str(cur_pull)).group(1))
mp = re.compile("([^\/]+)\/[^\/]+\/[0-9]{4}$")
mp_s = mp.match(str(cur_pull)).group(1)
month_p = int(mp.match(str(cur_pull)).group(1))
print(mp_s+" "+dp_s+" "+yp_s)

if hour <15:
    fileList = glob.glob('zillow\\**.csv', recursive=False)
    # Iterate over the list of filepaths & remove each file.
    for filePath in fileList:
        try:
            os.remove(filePath)
        except OSError:
            print("Error while deleting file")


lp = str(date_check['Last_Pulled'][0])
print(f'last pulled: {lp}')
year = int(yp.match(str(lp)).group(1))
day = int(dp.match(str(lp)).group(1))
month = int(mp.match(str(lp)).group(1))
if year_p==year and day_p==day and month_p==month:
    print("Up to date.")
    exit()


print('starting webdriver')
driver = webdriver.Chrome(options=options)
driver.set_window_size(1920, 1080)

# driver.maximize_window()
delay = 3
# driver.set_window_size(1024, 768)
url_param = 'https://www.zillow.com/mortgage-rates/#/'
# search_div = 'js-gbi-sayt gbi-sayt w-100'

print('visiting zillow')
driver.get(url_param)

print('finding rates')
allRates = driver.find_element_by_xpath("//div[contains(@name, 'allRates')]")

loan_types = allRates.find_elements_by_xpath(".//div[contains(@class, 'zgmi__ubp5bz-0 gmFqhz')]")
df = pd.DataFrame(columns = ['Date', 'Loan_Type', 'Program', 'Rate', 'Rate_Change', 'APR', 'APR_Change']) 
#(driver.page_source).encode('utf-8')

for header in loan_types:
    print('looping')
    loan_type=header.find_element_by_tag_name('h3')
    body=header.find_element_by_tag_name('tbody')
    programs=body.find_elements_by_tag_name('tr')
    if loan_type.text == 'Government Loans':
        continue
    loan_type_name = loan_type.text
    print('Loan Type: '+loan_type.text)
    for program in programs:
        if program.find_elements_by_xpath(".//a[contains(@class, 'Anchor-c11n-8-37-0__hn4bge-0 ieIKGR')]"):
            program_name = program.find_element_by_xpath(".//a[contains(@class, 'Anchor-c11n-8-37-0__hn4bge-0 ieIKGR')]")
        else:
            program_name = program.find_element_by_xpath(".//td[contains(@class, 'AverageRatesTable-program')]")
        rate = program.find_element_by_xpath(".//div[contains(@class, 'zgmi__sc-1gaok4s-0 hZgvrA')]") 
        rate_txt = re.search('^([0-9]+\.[0-9]+)',rate.text)
        rate_change = program.find_elements_by_xpath(".//td[contains(@class, 'StyledTableCell-c11n-8-37-0__sc-1mvjdio-0 eOtaFs')]")[0] 
        if rate_change.find_elements_by_xpath(".//svg[contains(@class, 'Icon-c11n-8-37-0__sc-13llmml-0 kyDcCO IconArrowUpCircle-c11n-8-37-0__sc-1h3m26u-0 zgmi__iz4i4h-2 lcSIIz QMGIo')]"):
            rate_change = '-'+rate_change.text
        else:
            rate_change = rate_change.text
        rate_change_txt = re.search('^(-?[0-9]+\.[0-9]+)', rate_change)
        apr = program.find_element_by_xpath(".//div[contains(@class, 'zgmi__sc-1gaok4s-0 hZgvrA')]")
        apr_txt = re.search('^([0-9]+\.[0-9]+)',apr.text)
        apr_change = program.find_elements_by_xpath(".//td[contains(@class, 'StyledTableCell-c11n-8-37-0__sc-1mvjdio-0 eOtaFs')]")[2] 
        apr_change_txt = re.search('^([0-9]+\.[0-9]+)',apr_change.text)
        df = df.append({'Date' : cur_pull, 'Loan_Type' : loan_type_name, 
                        'Program' : program_name.text, 'Rate' : str(rate_txt.group(0)), 
                        'Rate_Change' : str(rate_change_txt.group(0)), 'APR' : str(apr_txt.group(0)), 
                        'APR_Change' : str(apr_change_txt.group(0))},  
                ignore_index = True) 

df.to_csv(f"data\\zillow\\zillow_{cur_pull_d}.csv",index=False)

date_check['Last_Pulled'][0] = cur_pull
date_check.to_csv(directory,index=False)

driver.close()