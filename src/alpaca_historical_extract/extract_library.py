# standard libraries
import math
import pandas as pd
import datetime as dt
import os

# non-standard libraries
from yahoo_fin import stock_info as si

# internal libraries
import core_library as basic
import transform_library
import multiprocessing_library as mpl
import api_library


def get_iex(credentials,api, symbols, timeFrame, startDate, endDate, fileName, actionsDf, verbose=True):
    tStart = dt.datetime.now()
    if verbose:
        print('Pulling Market Data...')
    recordCount = 100
    totalRecords = len(symbols)
    # print('total Records',totalRecords)
    limit = math.ceil(totalRecords / recordCount)
    increment = 10
    lastPercentComplete = increment
    tempDT = dt.datetime.now()
    barSizeList = []
    dfCounter = 0
    totalApiCalls=0
    dataFound = False
    for i in range(limit):
        start = i * recordCount
        end = (i + 1) * recordCount
        percentComplete = round((start / totalRecords) * 100, 2)
        # print(start,end, percentComplete)
        if end > len(symbols):
            end = len(symbols)
#        barset = api.get_barset(symbols[start:end], timeframe=timeFrame, limit=1000, start=startDate, end=endDate)
        pageToken = ''
        subset=symbols[start:end]

        while type(pageToken)== type(str()):
            barset, pageToken = api_library.get_barset(credentials=credentials,
                                                       symbols=subset,
                                                       timeframe=timeFrame,
                                                       limit=10000,
                                                       start=startDate,
                                                       end=endDate,
                                                       pageToken=pageToken)
            totalApiCalls+=1
            #print(barset)
            #print(pageToken)
            if len(barset)>0:
                ##print('barset:',barset)
                dataFound = True
                totalBarSize, dfCounter = transform_library.batch_barset_to_df(barset=barset, timeFrame=timeFrame,
                                                                               actionsDf=actionsDf, dfCounter=dfCounter,
                                                                               fileName=fileName)
        # print('THIS dfCounter',dfCounter)
        if dataFound:
            if verbose:
                barSizeList.append(totalBarSize)
                if percentComplete >= lastPercentComplete:
                    lastPercentComplete = round(lastPercentComplete + increment, 0)
                    timeThusFar = dt.datetime.now() - tStart
                    percentLeft = 1 - (start / len(symbols))

                    timeLeft = ((timeThusFar * percentLeft) / (percentComplete * .01))
                    avgBarSize = sum(barSizeList) / len(barSizeList)

                    print(dt.datetime.now(),
                          "| Completed", percentComplete,
                          '% | time for subsection extraction:', dt.timedelta(seconds=(dt.datetime.now() - tempDT).seconds),
                          "| Predicted Time left:", timeLeft,
                          "| Predicted Total Time for complete extraction:", timeThusFar + timeLeft,
                          "| avg datapull size:", round(avgBarSize / 1000000, 2), 'MB',
                          "| Total Number of API Calls:", totalApiCalls)
                    tempDT = dt.datetime.now()
                    barSizeList = []

    if dataFound:
        if verbose:
            print("Completed", 100, '%')
            print("TIME TO PULL RAW STOCK DATA FROM ALPACA", dt.timedelta(seconds=(dt.datetime.now() - tStart).seconds))
        basic.log_entry(logFile="project_log.txt", logText=(
            "TIME TO PULL RAW STOCK DATA FROM ALPACA ",
            str(dt.timedelta(seconds=(dt.datetime.now() - tStart).seconds))),
                        logMode='a', gap=False)
        name, ext = os.path.splitext(fileName)
        fileName = name + '_RAW' + ext
        outputDF = pd.read_csv(fileName)
        #print('Calls to API:', totalApiCalls)
        # print(outputDF.to_string())
        # print(outputDF.info())
        return outputDF
    else:
        print('NO DATA FOUND')
        basic.log_entry(logFile="project_log.txt", logText=(
            "No Data Extracted for  ",fileName,
            str(dt.timedelta(seconds=(dt.datetime.now() - tStart).seconds))),
                        logMode='a', gap=False)
        return pd.DataFrame()


def get_tckrs():
    print('Getting stock symbols...')
    markets = [
        si.tickers_sp500(),
        si.tickers_nasdaq(),
        si.tickers_dow(),
        si.tickers_other()
    ]

    exclude = ['W', 'R', 'P', 'Q']
    del_set = set()
    sav_set = set()
    for market in markets:
        for tckr in market:
            if (len(tckr) > 4 and tckr[-1] in exclude) or len(tckr) == 0 or '$' in tckr:
                del_set.add(tckr)
            else:
                sav_set.add(tckr)

    print(f'Removed {len(del_set)} unqualified stock symbols...')
    print(f'There are {len(sav_set)} remaining qualified stock symbols...')
    # print(sav_set)
    sav_set = list(sav_set)
    sav_set.sort()
    # print(sav_set)
    return sav_set

def build_db():

    if not os.path.exists(ROOT_DIR + r'/' + "data"):
        os.mkdir(ROOT_DIR + r'/' + 'data')
    pd.DataFrame().to_csv(ROOT_DIR + r'/' + "data/ACTIONS DATA.csv")
    jsonFileName = ROOT_DIR + r'/' + "data/COMPANY INFO DATA.json"

    if not os.path.exists(jsonFileName):
        with open(jsonFileName, "x") as json_file:
            json_file.close()


def get_fun_data(tckrs, fullSend, settings, forceFDataPull=False, verbose=True):
    build_db()
    #print(len(tckrs), tckrs)
    pullFunData = False
    if os.path.exists(ROOT_DIR + r'/' + "data/YESTERDAY MARKET DATA.csv") and fullSend:
        print('Extant data found for previous market day. Removing companies from data pool')
        ogtckrsLen = len(tckrs)
        tckrs = pd.read_csv(ROOT_DIR + r'/' + "data/YESTERDAY MARKET DATA.csv")
        tckrs = tckrs['SYMBOL'].tolist()
        newtckrsLen = len(tckrs)
        print('Company scope reduced from', ogtckrsLen, 'to', newtckrsLen)

    for key in settings['fundamentals']:
        sourceFile = ROOT_DIR + r'/' + settings['fundamentals'][key]['file name']
        # print(sourceFile)
        isFileValid = (os.path.exists(sourceFile) and (
                    dt.datetime.fromtimestamp(os.path.getmtime(sourceFile)).date() == dt.datetime.now().date()))

        if not isFileValid:
            pullFunData = not isFileValid

    if pullFunData or forceFDataPull:
        mpl.get_company_data(ROOT_DIR, tckrs=tckrs, coreMultiplier=4, verbose=verbose)

    # actionDf = pd.read_csv(ROOT_DIR + r'/' + "data/ACTIONS DATA.csv")
    # infoDf = pd.read_csv(ROOT_DIR + r'/' + "data/COMPANY INFO DATA.csv")

    # print(actionDf)
    # print(infoDf)

    return


ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
