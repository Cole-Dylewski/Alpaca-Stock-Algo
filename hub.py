#standard libraries
import random
import time

import numpy as np
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
import core_library
import dbmsIO
import multiprocessing_library as mpl
import extract_library
import transform_library

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

    marketSchedule = nyse.schedule(start_date=nowUTC.date() - relativedelta(years=1), end_date=nowUTC.date()+ relativedelta(days=1))
    lastOpen = pd.Timestamp(marketSchedule['market_open'][0])
    lastClose = pd.Timestamp(marketSchedule['market_close'][0])

    marketOpen = nowUTC>lastOpen and nowUTC<lastClose

    #print(marketSchedule)
    return marketOpen, marketSchedule



def genMarketData(tckrs,settings,api):
    forceMDataPull = True
    #check if market is open

    marketOpen, marketSchedule = getClock()
    actionDf = pd.read_csv(ROOT_DIR + r'/' + "data/ACTIONS DATA.csv")
    active_assets = transform_library.objectToDF(api.list_assets(status='active'))
    # print(active_assets.head(25).to_string())
    active_assets.sort_values('SYMBOL', inplace=True)
    active_assets = active_assets.reset_index(drop=True)

    #print(active_assets.head(5).to_string())

    #print(marketSchedule.tail(5).to_string())

    validDays = marketSchedule.index.to_list()
    validDays.reverse()
    print('Market Open:', marketOpen)
    preMarket = validDays[1].date() == dt.datetime.now().date() and not marketOpen
    postMarket = validDays[1].date()>dt.datetime.now().date()
    print('preMarket',preMarket)
    print('postMarket',postMarket)

    print('valid days',validDays)
     #case scenario if after market close, but same day
    #if(validDays[0].date()>dt.datetime.now().date()):
        #print('deleting first valid day')
        #del validDays[0]
    #print(marketSchedule['market_open'])

    keys = list(settings['marketData'].keys())
    #keys.reverse()
    print(keys)

    for key in keys:
        print(key)
        sourceFile = ROOT_DIR + r'/' + settings['marketData'][key]['file name']
        #print(sourceFile)
        isFileValid = (os.path.exists(sourceFile) and (
                dt.datetime.fromtimestamp(os.path.getmtime(sourceFile)).date() == dt.datetime.now().date()))
        #print('isFileValid',isFileValid)
        dataValid = (isFileValid and not forceMDataPull)
        #print('dataValid',dataValid)
        #print('')

        if (dataValid):
            #print(key, 'saved Data is up to date...')
            core_library.logEntry(logFile="project_log.txt", logText=(key, ' saved Data is up to date...'),
                           logMode='a', gap=False)
        else:
            data = ''
            #print(key, 'Dataset is either missing or out of date, retrieving now...')
            core_library.logEntry(logFile="project_log.txt",
                           logText=(key, ' Dataset is either missing or out of date, retrieving now...'),
                           logMode='a', gap=False)

            offset = settings['marketData'][key]['offset']
            #if preMarket:
                #offset+=1
            range = settings['marketData'][key]['range'] +offset

            if range>len(validDays):
                range=len(validDays)-1
            #print(range,offset)
            startDate = validDays[range]
            endDate = validDays[offset]
            #print(startDate.date(), endDate.date())
            startDate = pd.Timestamp(startDate.strftime("%Y-%m-%d"), tz='America/New_York').isoformat()
            endDate = pd.Timestamp(endDate.strftime("%Y-%m-%d"), tz='America/New_York').isoformat()
            #print(startDate.tzinfo)
            #print(startDate,endDate)

            #if (key == 'DAILY MARKET DATA'):
            #if(key != 'YESTERDAY MARKET DATA'):
            if (True):
                data = extract_library.getMarketDataIEX(api=api, symbols=tckrs, timeFrame=settings['marketData'][key]['IEX']['interval'],
                                                startDate=startDate, endDate=endDate, fileName=sourceFile,
                                                actionsDf=actionDf, verbose=False)
                data['DATETIME'] = pd.to_datetime(data['DATETIME'])
                #print("PRINTING DATA")
                #print(data)
                #print(data.info())
                statData = transform_library.marketDataToSTAT2(data, fileName=key, verbose=False)
#                print(statData.head(5).to_string())
                mergedData = pd.merge(active_assets, statData, how="left", on=['SYMBOL'])
                mergedData = mergedData.dropna(how='any').reset_index(drop=True)

                core_library.logEntry(logFile="project_log.txt", logText=(mergedData.head(5).to_string()),
                                      logMode='a')

                core_library.logEntry(logFile="project_log.txt", logText=(key,str(mergedData.shape)),
                                      logMode='a')
                print(mergedData.head(5).to_string())
                print('post-filter shape', mergedData.shape)
                print('pre-len TCKRS',len(tckrs))
                if(key == 'YESTERDAY MARKET DATA'):
                    tckrs=mergedData['SYMBOL'].to_list()

                #tckrs = mergedData['SYMBOL'].to_list()
                print('post-len TCKRS', len(tckrs))
                dbmsIO.file_save(mergedData, sourceFile)
                core_library.logEntry(logFile="project_log.txt", logText=(key, " Saved..."),
                               logMode='a')


ROOT_DIR = os.path.dirname(os.path.abspath(__file__))