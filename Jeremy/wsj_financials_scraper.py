import requests
import pandas as pd
import csv
import time
import random
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from sqlalchemy import create_engine
import pprint


def get_ticker_values():    
    # set the path of the file to open
    sec_data_path = 'Combined_US_Stocks.csv'
    # open the csv file with 
    with open(sec_data_path) as csvfile:
        sec_data=csv.reader(csvfile, delimiter=',')
        # create a list of lists containing each line of data in the csv file
        data_lines = list(sec_data)
        last_line = len(data_lines)
        # initialize empty ticker lists to use as input when scraping
        ticker_list = []
        # iterate through the data in the sec data file
        for line in data_lines[1:last_line]:
            ticker_list.append(line[0])
                
    return ticker_list


def create_links(url, ticker_symbol):
    url_base = url
    url_add_filter = '/financials/annual/income-statement'
    url_list = []
    # use the ticker symbols to create the links to scrape
    for ticker in ticker_symbol:
        scrape_url = (f'{url_base}{ticker}{url_add_filter}')
        url_list.append(scrape_url)
    
    return url_list


def get_driver(urls):
    try:
        chrome_driver_path = 'chromedriver.exe'
        desired_capabilities = DesiredCapabilities.CHROME.copy()
        desired_capabilities['acceptInsecureCerts'] = True    
        driver = webdriver.Chrome(chrome_driver_path, desired_capabilities=desired_capabilities)
        driver.header_overrides = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"}
    except:
        print('Error creating driver')

    return driver


def scrape_page(urls, ticker_list, driver): 
    financials_dfs_list = []
    counter = 0
    for url in urls:        
        driver.get(url)
        driver.maximize_window()
        WebDriverWait(driver, 5)
        # wait a random amount of time to allow the page to load
        # value = random.randint(8,17)
        # time.sleep(value) 
        # Wait until the page loads and the revenue values are present on the page
        try:
            WebDriverWait(driver, 20).until(
                        EC.presence_of_element_located((By.XPATH, './/*[@id="cr_cashflow"]/div[2]/div/table/tbody/tr[1]/td[2]')))
        except:
            print(f'Error page did not finish loading for: {ticker_list[counter]}')  
        soup = BeautifulSoup(driver.page_source, 'lxml') 
         # get the ticker and append value to a list
         # wait a random amount of time to allow the page to load
        value = random.randint(2,4)
        time.sleep(value) 
        try:
            tickers = [] 
            ticker = ticker_list[counter]
            for i in range(5):
                tickers.append(ticker)
        except:
            print(f'Error creating ticker list for dataframe')
        # Scrape header values for each year
        header = []
        try:
            for tables in soup.find_all('table', class_= 'cr_dataTable'):
                for header_val in tables.find_all('th'):
                    header.append(header_val.text)
            header = header[:-1]            
            rpt_year = header[1:]
        except:
            print(f'Error scraping Headers for: {ticker}')        
        # get the scale value and append value to a list
        try:
            fin_scale = []
            scale = header[0]
            for i in range(5):
                fin_scale.append(scale)
        except:
            print(f'Error getting the reporting period for: {ticker}')
        # Get the exchange name
        exchange = []
        try:
            exchange_val = soup.find('span', class_='exchangeName').text
            exchange_val = exchange_val.replace("(", "").replace(")", "").replace(":", "").replace(".", "").replace("US ", "").upper()
            for i in range(2,7):                
                exchange.append(exchange_val)
        except:
            print(f'Error scraping exchange name information for: {ticker}')                         
        # Read from soup and scrape the account information for each year
        new_acct = [] 
        try:
            table = soup.find('table', class_="cr_dataTable")
            for rows in table.find_all('tbody'):
                for tr in rows.find_all('tr', class_=""):
                    for td in tr.find_all('td'):
                        new_acct.append(td.text)    
        except:
            print(f'Error creating soup object for: {ticker}')  
        # wait a random amount of time to allow the page to load
        value = random.randint(2,4)
        time.sleep(value) 
        # Create empty lists to hold account info
        revenue_list = []
        income_tax_list = []
        net_income_list = []
        diluted_shares_list = []
        # loop through the soup object and extract the annual acct info
        try:
            for item in new_acct:
                if item in ['Sales/Revenue', 'Interest Income']:
                    item_index = new_acct.index(item)
                    for i in range(5):
                        revenue_list.append(new_acct[item_index + 1 + i].replace(",",""))
                elif item in ['Net Income', 'Net Interest Income']:
                    item_index = new_acct.index(item)
                    for i in range(5):
                        net_income_list.append(new_acct[item_index + 1 + i].replace(",",""))
                elif item in ['Income Tax', 'Income Taxes']:
                    item_index = new_acct.index(item)
                    for i in range(5):
                        income_tax_list.append(new_acct[item_index + 1 + i].replace(",",""))
                elif item =='Diluted Shares Outstanding':
                    item_index = new_acct.index(item)
                    for i in range(5):
                        diluted_shares_list.append(new_acct[item_index + 1 + i].replace(",",""))
        except:
            print(f'Error looping through soup object to find accout info for: {ticker}') 

        # If there is a Sales/Revenue and an interest income account adjust the list to grab
        # only the net Sales/Revenue amount. Assumption is that Sales/Revenue before after Interest Income
        try:
            if len(revenue_list) > 5:
                revenue_list = revenue_list[0:5]
        except:
            print(f'Error adjusting Sales Revenue list for: {ticker}')
        # If there is a net income and a net interest income account adjust the list to grab
        # only the net income amount. Assumption is that NI comes after NI Income
        try:
            if len(net_income_list) > 5:
                net_income_list = net_income_list[5:10]
        except:
            print(f'Error adjusting net income list for: {ticker}')
        # If there is revenue but no outstanding share amout populate a list of zeros
        # to include in the dataframe
        try:
            if len(revenue_list) == 5 and len(diluted_shares_list) == 0:
                for i in range(5):
                    diluted_shares_list.append('0')
        except:
            print(f'Error appending 0 to diluted shares list for: {ticker}')
        # If there is revenue but no income tax amout populate a list of zero
        # to include in the dataframe
        try:
            if len(revenue_list) == 5 and len(income_tax_list) == 0:
                for i in range(5):
                    income_tax_list.append('0')
        except:
            print(f'Error appending 0 to income tax list for: {ticker}')           
        # Create a dictionary to hold the list values that have been scraped
        try:
            if len(tickers) > 0 and len(exchange) > 0 and len(fin_scale) > 0 and len(rpt_year) > 0 \
               and len(revenue_list) > 0 and len(net_income_list) > 0 and len(income_tax_list) > 0 and len(diluted_shares_list) > 0:
                # Create a dictionary for the financials
                financials_dict = {
                    'ticker': tickers,
                    'exchange':exchange,
                    'rpt_scale': fin_scale,
                    'rpt_year': rpt_year,
                    'revenue': revenue_list,
                    'income_tax': income_tax_list,
                    'net_income': net_income_list,
                    'diluted_shares_outstanding': diluted_shares_list,
                }
                financials_dfs_list.append(financials_dict)             
        except:
            print(f'\nError creating the financials_dict for: {ticker}\n') 
            print(f'Year: {rpt_year}')
            print(f'Ticker: {tickers}')
            print(f'Exchange: {exchange}')
            print(f'fin scale: {fin_scale}')
            print(f'revenue: {revenue_list}')            
            print(f'income tax: {income_tax_list}')
            print(f'net income: {net_income_list}')
            print(f'outstanding diluted shares: {diluted_shares_list}\n')
        # increment the counter to pull in the correct ticker from the ticker list  
        counter +=1
    try:
        financial_stats_df = pd.DataFrame()
        for d in financials_dfs_list:
            data = pd.DataFrame(d)
            financial_stats_df = financial_stats_df.append(data, ignore_index=True, sort=False)           
    except:
        print(f'Error creating dataframe for d: {d}')
    driver.quit()
    return financial_stats_df
    

def write_df_to_sql(financial_stats_df):    
    try:
        rds_connection_string = "postgres:password@localhost:5432/project2"
        engine = create_engine(f'postgresql://{rds_connection_string}')
        # Export the DataFrame to SQL
        financial_stats_df.to_sql(name='fin_stats', con=engine, if_exists='append', index=False) 
    except:
        print('Error writing data to SQL database')
    try:   
        # Verify that the data can be read into a DataFrame from SQL
        sql_stats_results = pd.read_sql_query('select * from fin_stats', con=engine).tail()
    except:
        print(f'Error reading data from postgres SQL database')
    
    return sql_stats_results


def main():
    tickers = get_ticker_values()
    base_url = 'https://www.wsj.com/market-data/quotes/'  
    url_list = create_links(base_url, tickers)
    driver = get_driver(url_list)
    df = scrape_page(url_list, tickers, driver)
    sql_results = write_df_to_sql(df)
    print(sql_results.tail())    

if __name__ == "__main__":
    main()
