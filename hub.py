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
import core_library
import multiprocessing_library as mpl
import extract_library

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



def genMarketData(tckrs,settings,api):
    forceMDataPull = False
    #check if market is open

    marketOpen, marketSchedule = getClock()
    actionDf = pd.read_csv(ROOT_DIR + r'/' + "data/ACTIONS DATA.csv")
    print(marketSchedule.tail(5).to_string())

    validDays = marketSchedule.index.to_list()
    validDays.reverse()
    print('Market Open:', marketOpen)
    preMarket = validDays[0].date() == dt.datetime.now().date() and not marketOpen
    postMarket = validDays[0].date()>dt.datetime.now().date()
    print('preMarket',preMarket)
    print('postMarket',postMarket)

    print('valid days',validDays)
     #case scenario if after market close, but same day
    if(validDays[0].date()>dt.datetime.now().date()):
        print('deleting first valid day')
        del validDays[0]
    #print(marketSchedule['market_open'])


    for key in settings['marketData']:
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
            range = settings['marketData'][key]['range']
            #print(offset,offset+range,len(validDays))
            #print(validDays[offset:offset+range])
            #newRange = validDays[offset:offset+range]
            #print('newRange',newRange)
            #newRange = validDays[0:7]
            # print('YEARLY')
            if range>len(validDays):
                range=len(validDays)-1
            startDate = validDays[range]
            endDate = validDays[offset]

            startDate = pd.Timestamp(startDate.strftime("%Y-%m-%d"), tz='America/New_York').isoformat()
            endDate = pd.Timestamp(endDate.strftime("%Y-%m-%d"), tz='America/New_York').isoformat()
            #print(startDate.tzinfo)
            print(startDate,endDate)

            #if(key == 'YRLY MARKET DATA'):
            if (True):
                data = extract_library.getMarketDataIEX(api=api, symbols=tckrs, timeFrame=settings['marketData'][key]['IEX']['interval'],
                                                startDate=startDate, endDate=endDate, fileName=sourceFile,
                                                actionsDf=actionDf, verbose=True)

                #data['DATETIME'] = pd.to_datetime(data['DATETIME'])






ROOT_DIR = os.path.dirname(os.path.abspath(__file__))