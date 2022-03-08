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

#internal libraries
import coreFuncs

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



if __name__ == '__main__':
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
    scriptStart = dt.datetime.now()
    marketData,fundamentalData,strats = getSettings()
    print(marketData)


    ttr = str(dt.timedelta(seconds=(dt.datetime.now() - scriptStart).seconds))
    print("script time to run:", ttr)
    coreFuncs.logEntry(logFile="project_log.txt", logText=("script time to run: ", ttr),
                   logMode='a')