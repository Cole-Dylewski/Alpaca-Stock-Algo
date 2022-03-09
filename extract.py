#standard libraries
import random
import time
import pytz
import pandas
import pandas as pd
import os
import datetime as dt



#non-standard libraries
import pandas_market_calendars as mcal
from tzlocal import get_localzone
from dateutil.relativedelta import relativedelta

#internal libraries
import coreFuncs
import multiprocessing_library as mpl

def getClock():
    print('')
    localTZOffset = time.timezone / 3600.0
    #get local time and timezone
    nowTS = pd.Timestamp(dt.datetime.now().astimezone())
    localTZ = nowTS.tzinfo

    #convert to UTC for standard comparison
    nowUTC = pd.Timestamp(dt.datetime.now().astimezone()).tz_convert('UTC')
    #nowlocalTZ = pd.Timestamp(dt.datetime.now().astimezone()).tz_convert('localTZ')

    nyse = mcal.get_calendar('NYSE')

    marketSchedule = nyse.schedule(start_date=nowUTC.date() - relativedelta(years=1), end_date=nowUTC.date())
    lastOpen = pd.Timestamp(marketSchedule['market_open'][0])
    lastClose = pd.Timestamp(marketSchedule['market_close'][0])

    marketOpen = nowUTC>lastOpen and nowUTC<lastClose
    #print(marketSchedule)
    return marketOpen, marketSchedule

def fundamentalData(tckrs,settings):
    forceFDataPull = False

    if (not os.path.exists(ROOT_DIR + r'/' + "data")):
        os.mkdir(ROOT_DIR + r'/' + 'data')

    actionDf = pd.DataFrame()
    infoDf = pd.DataFrame()
    pullFunData = False

    for key in settings['fundamentals']:
        sourceFile = ROOT_DIR + r'/' + settings['fundamentals'][key]['file name']
        #print(sourceFile)
        isFileValid = (os.path.exists(sourceFile) and (dt.datetime.fromtimestamp(os.path.getmtime(sourceFile)).date() == dt.datetime.now().date()))

        #print(isFileValid)
        if (not isFileValid):
            pullFunData = not isFileValid

    if pullFunData or forceFDataPull:
        mpl.companyInfo(ROOT_DIR, tckrs=tckrs, coreMultiplier=4)

    #actionDf = pd.read_csv(ROOT_DIR + r'/' + "data/ACTIONS DATA.csv")
    #infoDf = pd.read_csv(ROOT_DIR + r'/' + "data/COMPANY INFO DATA.csv")

    #print(actionDf)
    #print(infoDf)

    return

def marketData(tckrs,settings,api):
    forceMDataPull = False
    #check if market is open
    marketOpen, marketSchedule = getClock()
    print(marketOpen)
    print(marketSchedule)
    print(marketSchedule.index.to_list())
    print(marketSchedule['market_open'])

    for key in settings['marketData']:
        print(key)
        sourceFile = ROOT_DIR + r'/' + settings['marketData'][key]['file name']
        print(sourceFile)
        isFileValid = (os.path.exists(sourceFile) and (
                dt.datetime.fromtimestamp(os.path.getmtime(sourceFile)).date() == dt.datetime.now().date()))
        print('isFileValid',isFileValid)
        dataValid = (isFileValid and forceMDataPull)
        print('dataValid',dataValid)
        print('')

        if (dataValid):
            print(key, 'saved Data is up to date...')
            coreFuncs.logEntry(logFile="project_log.txt", logText=(key, ' saved Data is up to date...'),
                           logMode='a', gap=False)
        else:
            data = ''
            print(key, 'Dataset is either missing or out of date, retrieving now...')
            coreFuncs.logEntry(logFile="project_log.txt",
                           logText=(key, ' Dataset is either missing or out of date, retrieving now...'),
                           logMode='a', gap=False)

            # print('YEARLY')
            startDate = ''
            endDate = ''






ROOT_DIR = os.path.dirname(os.path.abspath(__file__))