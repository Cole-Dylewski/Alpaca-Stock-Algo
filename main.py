# standard libraries
import random
import time
import pandas as pd
import os
import datetime as dt
import json
import requests

# non-standard libraries
import pandas_market_calendars as mcal
import alpaca_trade_api as tradeapi
from yahoo_fin import stock_info as si

# internal libraries
import core_library
import extract_library
import hub
import load_library
import api_library
import dbmsIO

# global variables
loginSuccessful = ''
api = ''
scriptStart = dt.datetime.now()


def update_dbs():
    if __name__ == '__main__':
        if loginSuccessful:
            settings = dbmsIO.extractJson("settings.json")
            # print(settings)
            tckrs = extract_library.getTCKRS()
            # tckrs = ['CIG', 'SWI', 'AIV', 'BRBS', 'ELP', 'ITA', 'MZZ', 'QLD', 'ROL', 'SDD', 'SIJ', 'SMDD', 'SSG', 'SZK']
            # tckrs = ['FNGD']
            # print(tckrs)
            # tckrs = random.sample(tckrs, 100)
            #tckrs = tckrs[0:100 ]
            extract_library.extractFundamentalData(tckrs=tckrs, settings=settings, forceFDataPull=False, verbose=True)
            hub.genMarketData(tckrs=tckrs, settings=settings, api=api, forceMDataPull=False, verbose=True)

            ttr = str(dt.timedelta(seconds=(dt.datetime.now() - scriptStart).seconds))
            print("script time to run:", ttr)
            core_library.logEntry(logFile="project_log.txt",
                                  logText=("script time to run: ", ttr),
                                  logMode='a')


def init():
    global loginSuccessful
    global api

    if __name__ == '__main__':

        core_library.logEntry(logFile="project_log.txt",
                              logText=(dt.datetime.now().strftime("%m/%d/%Y, %H:%M:%S"), " Project Starting... "),
                              logMode='w')
        ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
        while (not api_library.internetTest()):
            print(dt.datetime.now(), "Internet Connection failed... ")
            core_library.logEntry(logFile="project_log.txt",
                                  logText=(
                                      dt.datetime.now().strftime("%m/%d/%Y, %H:%M:%S"),
                                      "Internet Connection failed... "),
                                  logMode='a')

        # print(ROOT_DIR)
        # api = login()
        credentials = api_library.initCredentials()

        loginSuccessful = False
        attempts = 0
        while not loginSuccessful:
            loginSuccessful, api, credentials = api_library.login(credentials)
            attempts += 1
            if attempts > 5:
                return False
        return api


init()
update_dbs()
