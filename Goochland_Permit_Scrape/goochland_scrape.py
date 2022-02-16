import numpy
import pandas as pd
from bs4 import BeautifulSoup
import urllib.parse
import re
import csv
import requests
import time
import datetime

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import re
###Create a
from __future__ import print_function
from bs4 import BeautifulSoup


df = pd.read_csv('\\Goochland_Parcels.csv')

url = 'https://gis.co.goochland.va.us/GoochlandPV/'
options = webdriver.ChromeOptions()
user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36'
headers = {"user-agent": user_agent}
options.add_argument(f'user-agent={user_agent}')

print('starting webdriver')
driver = webdriver.Chrome(options=options)
driver.set_window_size(1920, 1080)
driver.get(url)

# Bypass splash page
driver.find_element_by_xpath("//span[contains(@id, 'cbNewCheckbox')]").click()
driver.find_element_by_xpath("//input[contains(@name, 'btnEnterSite')]").click()
time.sleep(2)
# searchbar = driver.find_element_by_xpath("//input[contains(@id, 'Gpin')]")
# searchbar.send_keys('7715-69-8839')
# searchbox.send_keys(Keys.RETURN)


for i, row in df.iterrows():
    print(row['Neighborhood'] + ' - ' + row['Property Address'])
    searchbar = driver.find_element_by_xpath("//input[contains(@id, 'Gpin')]")
    searchbar.clear()
    searchbar.send_keys(row['GPIN'])
    searchbar.send_keys(Keys.RETURN)
    time.sleep(4)
    infobox = driver.find_element_by_xpath("//div[contains(@id, 'info')]")
    topbox = infobox.find_element_by_xpath(".//div")
    topleftbox = topbox.find_element_by_xpath(".//tbody")
    topleftfirstline = topleftbox.find_element_by_xpath(".//tr")
    owner_name = topleftfirstline.find_elements_by_xpath(".//td")[1]
    if owner_name.text == row['Owner']:
        #print('No change in Owner')
        pass
    elif len(owner_name.text) < 4:
        pass
    else:
        print('New Owner: ' + owner_name.text)
        #print('Replacing ' + row['Owner'])
        df.at[i, 'Owner'] = str(owner_name.text)
        bottombox = infobox.find_elements_by_xpath(".//div")[3]
        sale_date = bottombox.find_elements_by_xpath(".//td")[1]
        print('Updating sale date to: ' + sale_date.text)
        df.at[i, 'Sale Date'] = str(sale_date.text)
    #print('Checking permits.')
    permits = driver.find_element_by_partial_link_text("Permits").click()
    time.sleep(0.5)
    table_header = 0
    permit_table = driver.find_element_by_xpath("//div[contains(@id, 'Permits')]")
    permit_rows = permit_table.find_elements_by_xpath(".//tr")
    for permit in permit_rows:
        if table_header == 0:
            table_header = 1
        else: 
            permit_type = permit.find_elements_by_xpath(".//td")[6].text
            permit_status = permit.find_elements_by_xpath(".//td")[2].text
            if permit_type == 'Building':
                permit_date = permit.find_elements_by_xpath(".//td")[4].text
                cur_y = int(re.search('\d+\/\d+\/(\d+)', permit_date).group(1))
                cur_d = int(re.search('\d+\/(\d+)\/\d+', permit_date).group(1))
                cur_m = int(re.search('(\d+)\/\d+\/\d+', permit_date).group(1))
                cur_date = datetime.datetime(cur_y, cur_m, cur_d)
                if  row['Permit Date'] != "Unk":
                    prev_y = int(re.search('\d+\/\d+\/(\d+)', row['Permit Date']).group(1))
                    prev_d = int(re.search('\d+\/(\d+)\/\d+', row['Permit Date']).group(1))
                    prev_m = int(re.search('(\d+)\/\d+\/\d+', row['Permit Date']).group(1))
                    prev_date = datetime.datetime(prev_y, prev_m, prev_d)
                else:
                    prev_date = datetime.datetime(2000, 1, 1)
                if prev_date >= cur_date:
                    #print('Permit up to date.')
                    if permit_status == row['Permit Status']:
                    #print('Permit status up to date')
                        pass
                    else:
                        df.at[i, 'Permit Status'] = str(permit_status)
                        print('Updating permit status to ' + permit_status)
                else:
                    df.at[i, 'Permit Date'] = str(permit_date)
                    print('Updating permit date to ' + permit_date)
                    if permit_status == row['Permit Status']:
                    #print('Permit status up to date')
                        pass
                    else:
                        df.at[i, 'Permit Status'] = str(permit_status)
                        print('Updating permit status to ' + permit_status)
    return_to_search = driver.find_element_by_xpath('//a[@href="#searchtab"]').click()
    time.sleep(0.5)

df.to_csv('\\Goochland_Parcels.csv', index=False)
