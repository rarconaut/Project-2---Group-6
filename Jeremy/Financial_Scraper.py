from config import user_id
from config import password
import pandas as pd
import requests
import csv
import time
import random
from bs4 import BeautifulSoup
import os
from sqlalchemy import create_engine
from pprint import pprint


from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


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
    url_list = []
    # use the ticker symbols to create the links to scrape
    for ticker in ticker_symbol:
        url_filter = (f'quote/{ticker}/key-statistics?p={ticker}')
        scrape_url = url_base + url_filter
        url_list.append(scrape_url)
    
    return url_list


def sign_in(link, user, pswd):
    proxy_path = 'proxy.csv'
    with open(proxy_path) as csv_proxyfile:
        proxy_data=csv.reader(csv_proxyfile, delimiter=',')
        # create a list of lists containing each line of data in the csv file
        proxy_data_lines = list(proxy_data)
        last_line = len(proxy_data_lines)
        # initialize empty ticker lists to use as input when scraping
        proxy_list = []
        # iterate through the data in the sec data file
        for line in proxy_data_lines[1:last_line]:
            proxy_list.append(line[0])
    print(proxy_list)
    PROXY = random.choice(proxy_list)
    print(PROXY)
    # Define driver and specify path for chromedriver.exe
    chrome_driver_path = 'chromedriver.exe'
    # add desired capabilities to reduce the ssl errors
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--proxy-server=https://%s' % '75.51.241.29')
    
    desired_capabilities = DesiredCapabilities.CHROME.copy()
    desired_capabilities['acceptInsecureCerts'] = True
    driver = webdriver.Chrome(chrome_driver_path, desired_capabilities=desired_capabilities)
    # open the webpage to scrape
    print("Opening the webpage to sign in")
    driver.get(link)
    driver.maximize_window()
    WebDriverWait(driver, 5)

    # Use Beautifulsoup to grab the pages HTML and pass to a soup variable
    soup = BeautifulSoup(driver.page_source, 'lxml')
    for sign_in in soup.find_all('a', id='header-signin-link'):
        sign_in_link = sign_in.get('href')    
    # open the webpage to enter user name
    driver.get(sign_in_link)
    # wait a random amount of time to allow the page to load
    value = random.randint(4,7)
    time.sleep(value) 

    # enter user name
    driver.find_element_by_xpath('//*[@id="login-username"]').send_keys(user)    
    # click on next
    next_page = WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="login-signin"]')))    
    next_page.click()

    # wait a random amount of time to allow the page to load
    value = random.randint(4,7)
    time.sleep(value)

    # enter password
    driver.find_element_by_xpath('//*[@id="login-passwd"]').send_keys(pswd)    
    # click on next
    next_page = WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="login-signin"]')))    
    next_page.click()    
    # wait a random amount of time to allow the page to load
    value = random.randint(4,7)
    time.sleep(value)
    print("You are now logged in!")

    return driver


def convert_market_cap(market_cap_values):
    new_val_list = []
    temp_val_list = []
    try:
        for cap in market_cap_values:
            dec = cap.find('.')       
            base_val = cap[:-1].replace('.', '')
            try:
                if cap[-1] == 'T':
                    conversion_num = 13
                elif cap[-1] == 'B':
                    conversion_num = 10
                elif cap[-1] == 'M':
                    conversion_num = 7
                else:
                    conversion_num = 6
            except: 
                print(f'Error creating conversion number')
           
            zeros_to_add = conversion_num - dec
            temp_val_list.append(base_val) 
            # Append the correct number of zeros to the base number to get the 
            # reported value                           
            for i in range(zeros_to_add):
                temp_val_list.append('0')
                i+=1
            temp_val_list.append(',')

            market_cap_value = ' '.join([str(elem) for elem in temp_val_list]).replace(' ', '')

        # format the new_val_list so it may be added to the dataframe
        new_val_list.append(market_cap_value)
        new_val_list = new_val_list[0].split(',')
        # drop the last value in the list as it is a blank value
        new_val_list = new_val_list[:-1]
    except:
        print(f'Error creating new market cap values')

    return new_val_list


def scrape_web_page(weblinks, driver, tickers):
    counter = 0
    # create a list to hold dataframe objects
    fin_stats_dataframes = []
    fin_accts_dataframes = []

    for link in weblinks:        
        # open the webpage to scrape
        driver.get(link)
        driver.maximize_window()
        # set a counter to keep track of the ticker
        ticker = tickers[counter]
        # wait a random amount of time to allow the page to load
        value = random.randint(4,7)
        time.sleep(value)
        # click to select the annual valuation data on the statistics page
        web_x_path = '//*[@id="Col1-0-KeyStatistics-Proxy"]/section/div[2]/div[1]/div[1]/button[1]'
        element = WebDriverWait(driver, 10).until(
                  EC.presence_of_element_located((By.XPATH, web_x_path)))
        element.click()
        # wait a random amount of time to allow the page to load
        value = random.randint(5,7)
        time.sleep(value)

        #START SCRAPING STATISTICS HERE
        stats_date_list = []
        stats_mc_list = []
        ticker_list = []
        reporting_years_list = []
        
        soup = BeautifulSoup(driver.page_source, 'lxml')       
        try:
            for stats_hdata in soup.find_all('tr', class_='Bdtw(0px) C($primaryColor)'):
                for stats_label in stats_hdata.find_all('span'):           
                    stats_date_list.append(stats_label.text)

            # extract the label that will become the first item in the list
            first_date_label = stats_date_list[1][-10:]
            # remove the first 3 items from the list
            stats_date_list = stats_date_list[3:]
            # insert the first label back into the list
            stats_date_list.insert(0,first_date_label)

            for i in range(len(stats_date_list)):
                ticker_list.append(ticker)

            for i in range(len(stats_date_list)):
                reporting_years_list.append(len(ticker_list))
        except:
            print(f'Error getting the statistics label')

        # Scrape Market Cap data
        try:
            class_value = 'Bxz(bb) H(36px) BdY Bdc($seperatorColor) fi-row Bgc($hoverBgColor):h'
            for stats_mcdata in soup.find_all('tr', class_=class_value):
                for stats_mc in stats_mcdata.find_all('td'):           
                    stats_mc_list.append(stats_mc.text)
            # remove the "Market Cap (intraday)" label from the list
            stats_mc_list = stats_mc_list[1:]
        except:
            print(f'Error getting Market Cap data')   

        # Create a dictionary to hold market cap data
        try:
            fin_stats_df = {'ticker':ticker_list, 'reporting_date':stats_date_list, 'market_cap':stats_mc_list, \
                            'total_years_reporting':reporting_years_list}
            # append the fin stats dictionary to a dataframe list
            fin_stats_dataframes.append(fin_stats_df)
        except:
            print(f'Error creating fin stats dictionary')

        # Switch to the financials view of the page
        value = random.randint(3,7)
        time.sleep(value)      
        try:
            # select the Financials link 
            fin_x_path = '//*[@id="quote-nav"]/ul/li[8]/a/span'
            element = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, fin_x_path)))
            element.click()
        except:
            print(f'Unable to switch to financials view')

        try:
            # select the annual link on the Financials page
            fin_annual_x_path = '//*[@id="quote-nav"]/ul/li[8]/a'
            element = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, fin_annual_x_path)))
            element.click()
        except:
            print(f'Unable to click the annual link on the financials section')

        value = random.randint(3,8)
        time.sleep(value) 

        # Scrape Financial data
        financials_ticker_list = []
        financials_date_list = []
        financials_rev_list = []
        financials_gp_list = []
        # financials_tp_list = []
        fin_reporting_years_list = []

        soup = BeautifulSoup(driver.page_source, 'lxml')
        # scrape Financials date header values 
        try:
            for fin_hdata in soup.find_all('div', class_='D(tbhg)'):
                for fin_headers in fin_hdata.find_all('span'):           
                    financials_date_list.append(fin_headers.text)
            # remove the Breakdown" label from the list
            financials_date_list = financials_date_list[1:]
        except:
            print(f'Error getting Financials headers') 
        
        # scrape Financials Total Revenue values 
        try:
            for fin_revdata in soup.find(class_='D(tbr) fi-row Bgc($hoverBgColor):h'):
                for fin_rev_value in fin_revdata.find_all('span'):
                    value = fin_rev_value.text
                    num_value = value.replace(",", "")   
                    financials_rev_list.append(num_value)
            # Remove the 'Total Revenue' item from the list
            financials_rev_list = financials_rev_list[1:]
            # get the total number of years reporting for each company
            num_financial_yrs_reported = len(financials_rev_list)
            for i in range(num_financial_yrs_reported):
                fin_reporting_years_list.append(num_financial_yrs_reported)
            # create a list with the company ticker 
            for i in range(num_financial_yrs_reported):
                financials_ticker_list.append(ticker)

        except:
            print(f'Error getting Financials Revenue Data')

        # scrape Financials Gross Profit values 
        try:
            gp_list = []
            gp_xpath = '//*[@id="Col1-1-Financials-Proxy"]/section/div[3]/div[1]/div/div[2]/div[3]'
            fin_data_values = driver.find_elements_by_xpath(gp_xpath)
            for gp_value in fin_data_values:
                num_value = gp_value.text
                value = num_value.replace(",", "")
                gp_list.append(num_value)
            # convert the single string of gp values to a list of gp values
            gp_list = gp_list[0].split(" ")
            # remove the "," from the gp values
            for i in range(len(gp_list)):
                gp_value = gp_list[i].replace(",", "")
                financials_gp_list.append(gp_value)
            # remove first element from scraped gp list and remove 'Profit\n'
            # from second element in the list
            financials_gp_list[1] = financials_gp_list[1][7:]
            financials_gp_list = financials_gp_list[1:]
        except:
            print(f'Error getting Financials Gross Profit Data') 
        
        # scrape financials Tax Provision Data
        # tx_xpath = '//*[@id="Col1-1-Financials-Proxy"]/section/div[3]/div[1]/div/div[2]/div[8]'
        # fin_tax_values = driver.find_elements_by_xpath(tx_xpath)
        
        # for tx_value in fin_tax_values:
        #     num_value = tx_value.text
        #     num_value = num_value.replace(",", "")
        #     num_value = num_value.split(" ")
        #     financials_tp_list.append(num_value)
        #     # remove 'Tax' & 'Tax Provision\n' from the list
        #     financials_tp_list = financials_tp_list[0][1:]
        #     financials_tp_list[0] = financials_tp_list[0][10:]
        
        # increment the counter to keep track of the ticker symbol
        counter +=1

        value = random.randint(3,5)
        time.sleep(value)
         
        # Create a dictionary to hold Financial accounts data
        try:
            fin_accts_df = {'ticker':financials_ticker_list, 'reporting_date':financials_date_list, 'total_revenue':financials_rev_list, \
                            'gross_profit':financials_gp_list, 'total_years_reporting':fin_reporting_years_list}
            # append the fin stats dictionary to a dataframe list
            fin_accts_dataframes.append(fin_accts_df)
        except:
            print(f'Error creating fin accts dictionary')

    # FIN STATS DATAFRAME: Create a Pandas dataframe and append each page of fin stats
    financial_stats_df = pd.DataFrame()
    # For each dictionary of financial stats data in the list create a dataframe and append to previous
    try:
        for d in fin_stats_dataframes:
            data = pd.DataFrame(d)
            financial_stats_df = financial_stats_df.append(data, ignore_index=True, sort=False)
    except:
        print(f'There was an error tyring to create and append the statistics accounts dataframes together.')

    # print(f'Financials Ticker: {financials_ticker_list}')
    # print(f'Tax Provision: {financials_tp_list}')

    # FINANCIAL ACCOUNTS DATAFRAME: Create a Pandas dataframe and append each page of financials
    financial_accts_df = pd.DataFrame()
    # For each dictionary of financial data in the list create a dataframe and append to previous
    try:
        for d in fin_accts_dataframes:
            data = pd.DataFrame(d)
            financial_accts_df = financial_accts_df.append(data, ignore_index=True, sort=False)
    except:
        print(f'There was an error tyring to create and append the financial accounts dataframes together.')
        # print(f'ticker length: {len(financials_ticker_list)}')
        # print(f'date length: {len(financials_date_list)}')
        # print(f'revenue length: {len(financials_rev_list)}')
        # print(f'Gross Profit length: {len(financials_gp_list)}')
        # print(f'Tax provision length: {len(financials_tp_list)}')
        # print(f'Financials Ticker: {financials_ticker_list}')
        # print(f'Tax Provision: {financials_tp_list}')

        
    # use function to convert ##.##B format to a real number
    market_cap_list_to_convert = []
    market_cap_list_to_convert = financial_stats_df['market_cap'].to_list()
    # Call convert function
    market_cap_list = convert_market_cap(market_cap_list_to_convert)
    # add converted values to a new dataframe column
    financial_stats_df['market_cap_num'] = market_cap_list
    # rearrange the column positons in the dataframe
    financial_stats_df = financial_stats_df[['ticker', 'reporting_date', 'market_cap', 'market_cap_num', 'total_years_reporting']]
    driver.quit()

    return financial_stats_df, financial_accts_df


def write_df_to_sql(financial_stats_df, financial_accts_df):

    rds_connection_string = "postgres:password@localhost:5432/project2"
    engine = create_engine(f'postgresql://{rds_connection_string}')

    # Export the DataFrame to SQL
    financial_stats_df.to_sql(name='fin_stats', con=engine, if_exists='append', index=False)
    financial_accts_df.to_sql(name='fin_accts', con=engine, if_exists='append', index=False)  

    # Verify that the data can be read into a DataFrame from SQL
    sql_stats_results = pd.read_sql_query('select * from fin_stats', con=engine).tail()
    sql_accts_results = pd.read_sql_query('select * from fin_accts', con=engine).tail()
    

    return sql_stats_results, sql_accts_results


def main():   

    base_url = 'https://finance.yahoo.com/' 
    driver = sign_in(base_url, user_id, password)
    tickers = get_ticker_values()
    links = create_links(base_url, tickers)    
    pages = scrape_web_page(links, driver, tickers) 

    sql_results = write_df_to_sql(pages[0], pages[1])
    print(sql_results[0])
    print("")
    print(sql_results[1])
    
    
    # pages.to_csv('web_scraping_df.csv', index=False, header=True)

if __name__ == "__main__":
    main()

        
        
        



