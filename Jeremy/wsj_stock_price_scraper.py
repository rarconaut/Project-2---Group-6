import requests
import pandas as pd
import datetime
import os
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
    # sec_data_path = 'Missing_tickers.csv'
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
    url_add_filter = '/historical-prices'
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
        # Update chromedriver options to temporarily change the download directory
        options = webdriver.ChromeOptions()
        prefs = {
            "download.default_directory":r"C:\Gitlab\project2\downloads",
            "download.prompt_for_download": False,
            "download.directory_upgrade": True
        }
        options.add_experimental_option('prefs', prefs)
        driver = webdriver.Chrome(chrome_options=options)
        driver.header_overrides = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"}
    except:
        print('Error creating driver')

    return driver


def rename_files(ticker, counter):
    try:
        ticker = ticker              
        old_file_name = 'HistoricalPrices.csv'
        new_file_name = 'HistoricalPrices_' + ticker +'.csv'
        source = './downloads/' + old_file_name
        destination = './downloads/' + new_file_name
        duplicate_name = './downloads/Duplicate_HistoricalPrices_' + ticker + '.csv'
        name = os.rename(source, destination) 
    except:
        print(f'Error renaming file for {ticker}')  
        duplicate_name = os.rename(source, duplicate_name)
        # delete the duplicate file
        os.remove(duplicate_name)    

    return name


def add_csv_ticker_column(path):
    files = os.listdir(path)
    # add a ticker column to each downloaded file
    for file in files:
        start = file.index("_")
        end = file.index(".")
        ticker = file[start+1:end]
        file_to_update = path + file
        df = pd.read_csv(file_to_update)        
        df['ticker'] = ticker
        df.to_csv(file_to_update, index=False)
        updated_file_df = pd.read_csv(file_to_update)

    return updated_file_df


def combine_csv_files(source_folder_path):
    # create a list of files to merge
    files_list = os.listdir(source_folder_path)    
    dfList = []
    colnames = ['date', 'open', 'high', 'low', 'close', 'volume', 'ticker']
    # loop through the files and concatenate them together into one dataframe
    for file in files_list:
        file = source_folder_path + file   
        # remove the header row and then skip the first row as the header moves to row 1    
        df = pd.read_csv(file, header=None, skiprows=1)
        dfList.append(df)
    comb_hist_df = pd.concat(dfList, axis=0, ignore_index=True)
    comb_hist_df.columns=colnames
    comb_hist_df.to_csv('combined_historical_prices.csv', index=None)

    return comb_hist_df


def get_end_of_year_price(df):
    eoy_df = df
    # add a column for the year
    eoy_df["year"] = pd.DatetimeIndex(eoy_df["date"]).year
    #convert the date to a datetimeindex 
    eoy_df["date"] = pd.to_datetime(eoy_df["date"])
    eoy_df.sort_values(by=["ticker", "date", "year"], ascending=[True, False, False], inplace=True)
    # create a groupby object using year
    ticker = eoy_df.groupby(['ticker', 'year'], as_index=False)
    # bring in the closing price which occurs on the last date in each year
    close_price_df = ticker[["date", "open", "high", "low", "close", "volume"]].first()
    # rename date field
    close_price_df = close_price_df.rename(columns={'date': 'date_val', 
                                                    'year': 'year_val',
                                                    'open': 'open_val',
                                                    'high': 'high_val',
                                                    'low': 'low_val',
                                                    'close': 'close_val'})
    close_price_df = close_price_df[['ticker', 'date_val', 'year_val', 'open_val', 'high_val', 'low_val', 'close_val', 'volume']]
    
    return close_price_df


def scrape_page(urls, tickers, driver):
    counter = 0
    for url in urls:        
        driver.get(url)
        driver.maximize_window()
        # get ticker
        ticker = tickers[counter]
        print(f'ticker: {ticker}')
        # wait a random amount of time to allow the page to load
        value = random.randint(4,7)
        time.sleep(value)
        # Clear the from date and enter the new beginning date filter
        driver.find_element_by_xpath('.//*[@id="selectDateFrom"]').clear()
        driver.find_element_by_xpath('.//*[@id="selectDateFrom"]').send_keys("12/25/2015")
        # click on go
        new_date = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, './/*[@id="datPickerButton"]')))
        new_date.click()
        # click on download spreadsheet
        download = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, './/*[@id="dl_spreadsheet"]')))
        download.click()
        # wait a random amount of time to allow the page to load
        value = random.randint(4,7)
        time.sleep(value)
        # call function to rename downloaded file
        rename_files(ticker, counter)   
        counter+=1
    driver.quit()
    print(f'Done downloading files')
    return 


def write_df_to_sql(close_price_df):    
    try:
        rds_connection_string = "postgres:password@localhost:5432/project2"
        engine = create_engine(f'postgresql://{rds_connection_string}')
        # Export the DataFrame to SQL
        close_price_df.to_sql(name='close_price', con=engine, if_exists='append', index=False) 
    except:
        print('Error writing data to SQL database')
    try:   
        # Verify that the data can be read into a DataFrame from SQL
        sql_stats_results = pd.read_sql_query('select * from close_price', con=engine).tail()
    except:
        print(f'Error reading data from postgres SQL database')
    
    return sql_stats_results

    
def main():
    tickers = get_ticker_values()
    base_url = 'https://www.wsj.com/market-data/quotes/'  
    url_list = create_links(base_url, tickers)
    driver = get_driver(url_list)
    scrape_page(url_list, tickers, driver)
    # specify a download path for the function to look for when 
    # adding a ticker column to each file
    download_path = './downloads/'
    df = add_csv_ticker_column(download_path)
    
    df = combine_csv_files(download_path)
    close_price_df = get_end_of_year_price(df)
    
    sql_results = write_df_to_sql(close_price_df)
    print(sql_results.tail())

    driver.quit()    

if __name__== "__main__":
    main()