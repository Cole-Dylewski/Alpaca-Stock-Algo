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
projectSettings = {}
api = ''
marketData = {}
fundamentalData = {}
strats = {}
tckrs = []
ROOT_DIR = ''


#check if internet is working, return bool. Designed for time delayed while loop
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

def getSettings():
    global projectSettings
    global marketData
    global fundamentalData
    global strats

    jsonFileName = ROOT_DIR + r"/settings.json"
    print("settings file:", jsonFileName)
    with open(jsonFileName, "r") as settings_file:
        settingsFile = json.load(settings_file)

    # print(settingsFile)
    projectSettings = settingsFile['settings']
    marketData = settingsFile['marketData']
    fundamentalData = settingsFile['fundamentals']
    strats = settingsFile['strategies']


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
    getSettings()
    print(projectSettings)
    print(marketData)


    ttr = str(dt.timedelta(seconds=(dt.datetime.now() - scriptStart).seconds))
    print("script time to run:", ttr)
    coreFuncs.logEntry(logFile="project_log.txt", logText=("script time to run: ", ttr),
                   logMode='a')