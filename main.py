#standard libraries
import random
import time
import pandas as pd
import os
import datetime as dt
import json
import requests

#non-standard libraries
import pandas_market_calendars as mcal
import alpaca_trade_api as tradeapi
from yahoo_fin import stock_info as si

#internal libraries
import coreFuncs
import extract

#global variables
endpoint = {}
api = ''
marketData = {}
fundamentalData = {}
strats = {}
tckrs = []
ROOT_DIR = ''
credentials = {
  "endpoint": {
		"apiKey" : "",
		"apiSecret" : ""
	}
}




#check if internet is working, return bool. Designed as time delayed while loop
def internetTest():
    url = "http://www.google.com"
    timeout = 5
    try:
        request = requests.get(url, timeout=timeout)
        print("Connected to the Internet")
        coreFuncs.logEntry(logFile="project_log.txt",
                       logText=(dt.datetime.now().strftime("%m/%d/%Y, %H:%M:%S"), "Connected to the Internet"),
                       logMode='a')

        return True
    except (requests.ConnectionError, requests.Timeout) as exception:
        # print("No internet connection...")
        time.sleep(5)
        return False


#read project settings json
def getSettings():
    settingsFileName = ROOT_DIR + r"/settings.json"
    print("settings file:", settingsFileName)
    with open(settingsFileName, "r") as settings_file:
        settings = json.load(settings_file)

    # print(settingsFile)
    marketData = settings['marketData']
    fundamentalData = settings['fundamentals']
    strats = settings['strategies']
    return marketData,fundamentalData,strats

def getTCKRS():

    df1 = pd.DataFrame(si.tickers_sp500())
    df2 = pd.DataFrame(si.tickers_nasdaq())
    df3 = pd.DataFrame(si.tickers_dow())
    df4 = pd.DataFrame(si.tickers_other())

    tckr1 = set(symbol for symbol in df1[0].values.tolist())
    tckr2 = set(symbol for symbol in df2[0].values.tolist())
    tckr3 = set(symbol for symbol in df3[0].values.tolist())
    tckr4 = set(symbol for symbol in df4[0].values.tolist())
    tckrs = set.union(tckr1, tckr2, tckr3, tckr4)

    exclude = ['W', 'R', 'P', 'Q']
    del_set = set()
    sav_set = set()

    for tckr in tckrs:
        if len(tckr) > 4 and tckr[-1] in exclude:
            del_set.add(tckr)
        else:
            sav_set.add(tckr)

    print(f'Removed {len(del_set)} unqualified stock symbols...')
    print(f'There are {len(sav_set)} qualified stock symbols...')
    return sav_set

if __name__ == '__main__':
    scriptStart = dt.datetime.now()
    coreFuncs.logEntry(logFile="project_log.txt",
                   logText=(dt.datetime.now().strftime("%m/%d/%Y, %H:%M:%S"), " Project Starting... "),
                   logMode='w')
    ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
    while (not internetTest()):
        print(dt.datetime.now(), "Internet Connection failed... ")
        coreFuncs.logEntry(logFile="project_log.txt",
                       logText=(dt.datetime.now().strftime("%m/%d/%Y, %H:%M:%S"), "Internet Connection failed... "),
                       logMode='a')

    # print(ROOT_DIR)

    marketData,fundamentalData,strats = getSettings()
    print(marketData)
    tckrs = getTCKRS()
    print(tckrs)

    ttr = str(dt.timedelta(seconds=(dt.datetime.now() - scriptStart).seconds))
    print("script time to run:", ttr)
    coreFuncs.logEntry(logFile="project_log.txt", logText=("script time to run: ", ttr),
                   logMode='a')