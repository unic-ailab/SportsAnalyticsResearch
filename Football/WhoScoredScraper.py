import time
import pandas as pd
from pandas.io.html import read_html
from pandas import DataFrame
from selenium import webdriver
import csv

driver = webdriver.Chrome("C:\\Users\\1\\Downloads\\chromedriver_win32\\chromedriver.exe") # change this to wherever your chromedriver executable is located
driver.get('https://www.whoscored.com/Regions/252/Tournaments/2/Seasons/3853/Stages/7794/PlayerStatistics/England-Premier-League-2013-2014') # change this to the URL of the season that you want to scrape

df = DataFrame()

statistics = {  # this is a list of all the tabs on the page
    'summary': DataFrame()
}

count = 0
tabs = driver.find_element_by_xpath('//*[@id="stage-top-player-stats-options"]').find_elements_by_tag_name('li')  # this pulls all the tab elements
for tab in tabs[:-1]:  # iterate over the different tab sections
    section = tab.text.lower()
    time.sleep(3)

    driver.find_element_by_xpath('//*[@id="stage-top-player-stats-options"]').find_element_by_link_text(section.title()).click()  # clicks the actual tab by using the dictionary's key (.proper() makes the first character in the string uppercase)
    time.sleep(3)
    while True:
        while driver.find_element_by_xpath('//*[@id="statistics-table-%s"]' % section).get_attribute('class') == 'is-updating':  # string formatting on the xpath to change for each section that is iterated over
            time.sleep(1)

        table = driver.find_element_by_xpath('//*[@id="statistics-table-%s"]' % section)  # string formatting on the xpath to change for each section that is iterated over
        table_html = table.get_attribute('innerHTML')

        df = read_html(table_html)[0]

        df1 = df.Player # player dataframe
        df2 = df.Rating # ratings dataframe
        df3 = df.Mins # mins dataframe

        df4 = pd.concat([df1,df2,df3], axis=1) # combine based on ID
        print(df4)

        df4.to_csv("13-14-WhoScored.csv", mode='a', header=False)

        next_link = driver.find_elements_by_xpath('//*[@id="next"]')[count]  # makes sure it's selecting the correct index of 'next' items
        if 'disabled' in next_link.get_attribute('class'):
            break
        time.sleep(1)
        next_link.click()
    count += 1


for df in statistics.values():  # iterates over the DataFrame() elements
    print(df)

driver.quit()
