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

    tStart = dt.datetime.now()
    print('Pulling Market Data...')

    tStart = dt.datetime.now()
    recordCount = 100
    totalRecords = len(symbols)
    limit = math.ceil(totalRecords/recordCount)
    increment = 5
    lastPercentComplete=increment
    tempDT = dt.datetime.now()
    barSizeList = []
    dfCounter=0

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

def extractJson(fileName, defaultValue={}):
    jsonFileName = ROOT_DIR + r'/' + fileName

    if not os.path.exists(jsonFileName):
        with open(jsonFileName, "x") as json_file:
            json.dump(defaultValue, json_file)
            json_file.close()

    print("loading JSON", jsonFileName)
    with open(jsonFileName, "r") as json_file:
        jsonData = json.load(json_file)

    return jsonData

def extractFundamentalData(tckrs,settings):
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

def convertFileToDF(sourceFile, sourceDirectory='', good2go=True):
    if (sourceDirectory == ''):
        sourceDirectory = os.path.dirname(sourceFile)
    ###If the data is already in a traditional table format, set below value to true
    if (good2go):
        inputData = []
        name, ext = os.path.splitext(sourceFile)
        # print("Name = ", name)
        # print('EXT = ', ext)
        if (ext == '.csv'):
            # print('CSV')
            inputData = pd.read_csv(sourceFile, low_memory=False)

        if (ext == '.xlsx'):
            # print('XLSX')
            # inputData = pd.read_excel(sourceFile, dtype= str,low_memory=False)
            inputData = pd.read_excel(sourceFile, sheet_name=None)
        return inputData

        return df

def writeToCSV(position, data, tableName,raw=True):

    #print("Updating table")
    #print(keyType)
    #print(position)
    #print(tableName)
    #print(data)
    if(raw):
        if(position ==0):
            name, ext = os.path.splitext(tableName)
            fileName = name + '_RAW' + ext
            data.to_csv(fileName, mode='w', index=False)


        else:
            name, ext = os.path.splitext(tableName)
            fileName = name + '_RAW' + ext
            data.to_csv(fileName,header=False, mode='a',index = False)
        #print(name + '_RAW' + ext+" SAVED")
    else:
        if (position == 0):
            name, ext = os.path.splitext(tableName)
            fileName = name + ext
            data.to_csv(fileName, mode='w', index=False)

        else:
            name, ext = os.path.splitext(tableName)
            fileName = name+ ext
            data.to_csv(fileName, header=False, mode='a', index=False)
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))