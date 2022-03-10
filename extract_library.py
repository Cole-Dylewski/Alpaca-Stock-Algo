#standard libraries
import math
import pandas as pd
import datetime as dt
import os
import json


#non-standard libraries
from yahoo_fin import stock_info as si

#internal libraries
import core_library as basic
import transform_library
import multiprocessing_library as mpl


def getMarketDataIEX(api, symbols,timeFrame,startDate,endDate,fileName,actionsDf,verbose=True):
    #print(timeFrame)
    #print(type(startDate))
    #print(startDate)
    #print(endDate)

    #startDate='2022-03-07T00:00:00-05:00'
    #endDate = '2022-03-08T00:00:00-05:00'
    #print(type(startDate))
    #print(startDate)
    ##print(endDate)
    tStart = dt.datetime.now()
    print('Pulling Market Data...')

    tStart = dt.datetime.now()
    recordCount = 100
    totalRecords = len(symbols)
    print('total Records',totalRecords)
    limit = math.ceil(totalRecords/recordCount)
    increment = 5
    lastPercentComplete=increment
    tempDT = dt.datetime.now()
    barSizeList = []
    dfCounter=0
    for i in range(limit):
        start = i * recordCount
        end = (i + 1) * recordCount
        percentComplete = round((start / totalRecords) * 100, 2)
        print(start,end, percentComplete)
        if end > len(symbols):
            end = len(symbols)
        barset = api.get_barset(symbols[start:end], timeframe=timeFrame, limit=1000, start=startDate, end=endDate)
        transform_library.batchBarSetToDF(barset=barset,timeFrame=timeFrame,actionsDf=actionsDf,dfCounter=dfCounter,fileName=fileName)
        dfCounter = dfCounter + 1

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
        if (len(tckr) > 4 and tckr[-1] in exclude) or len(tckr) ==0:
            del_set.add(tckr)
        else:
            sav_set.add(tckr)

    print(f'Removed {len(del_set)} unqualified stock symbols...')
    print(f'There are {len(sav_set)} qualified stock symbols...')
    return list(sav_set)

def extractFundamentalData(tckrs,settings):
    forceFDataPull = True

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

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))