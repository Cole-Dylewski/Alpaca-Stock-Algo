# STOCK_DATA
Library for extracting full list of active tradeable stocks available, and creating detailed data of trends and statistics in daily, weekly, monthly, and yearly intervals. Requires Alpaca trading account for stock data extraction

from alpaca_historical_extract import hub

if __name__ == '__main__':
	loginSuccessful, api, credentials = hub.init()
    	#print(loginSuccessful, api, credentials)
     	hub.update_dbs(credentials, 
                       api,                 #API Object
                       tckrs='',            #List of Stock Symbols ex: ['TSLA','AAPL','MSFT'], if blank will pull all viable stocks
                       modeling=False,      #sets timeframe, if False will pull todays data with a 15 min delay, if true will use last open market day as last viable date. Defaults to False
                       forceFDataPull=True, #if true, will bypass file checks and pull company level dat, if False will skip if data already has been pulled for that day. Defaults to False
                       forceMDataPull=True, #if true, will bypass file checks and pull market level dat, if False will skip if data already has been pulled for that day. Defaults to False
                       verbose=True)        #if True, will print additional time and stat metrics during runtime. Defaults to True
     	keys = hub.get_datasets() #returns list of dict keys that correspond to individual data sets ex :['DAILY MARKET DATA', 'YESTERDAY MARKET DATA', 'WEEKLY MARKET DATA', 'MONTHLY MARKET DATA', 'YRLY MARKET DATA']
	dataset = hub.get_table(dataset=keys, raw=True) #uses key to identify and return corresponding data set in {key:[STAT DATAFRAME, RAW DATAFRAME]}