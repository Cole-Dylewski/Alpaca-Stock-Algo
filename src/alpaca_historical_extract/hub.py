# standard libraries
import pandas as pd
import os
import datetime as dt
import time
import pytz

# non-standard libraries
import pandas_market_calendars as mcal
from dateutil.relativedelta import relativedelta

# internal libraries
import core_library
import dbmsIO
import extract_library
import transform_library
import api_library
import load_library


def get_clock(fixedDate='', modeling=False):
    # localTZOffset = time.timezone / 3600.0
    # get local time and timezone

    # nowTS = pd.Timestamp(dt.datetime(year=2022, month=4, day=6, hour=2, minute=40).astimezone())

    if fixedDate != '':
        nowTS = pd.Timestamp(fixedDate.astimezone())
    else:
        nowTS = pd.Timestamp(dt.datetime.now().astimezone())

    localTZ = nowTS.tzinfo
    print('LOCAL TIMEZONE:',localTZ)

    # convert to UTC for standard comparison
    nowUTC = nowTS.tz_convert('UTC')
    print('Converting to:', nowUTC.tzinfo)
    # nowUTC = nowUTC + relativedelta(days=4)
    # nowlocalTZ = pd.Timestamp(dt.datetime.now().astimezone()).tz_convert('localTZ')

    nyse = mcal.get_calendar('NYSE')

    marketSchedule = nyse.schedule(start_date=nowUTC.date() - relativedelta(years=1), end_date=nowUTC.date())
    validDays = []

    flag = True
    for i in range(len(marketSchedule.index.to_list())):
        if (flag):
            mDay = marketSchedule.index.to_list()[i]
            # print(nowUTC.date(), mDay.date(),nowUTC.date() < mDay.date())
            if (nowUTC.date() < mDay.date()):
                validDays.append(mDay)
                flag = False
                # print('THIS')
                # print(mDay)
            else:
                validDays.append(mDay)
    # if modeling:
    # validDays.remove(validDays[-1])

    marketSchedule = marketSchedule.loc[validDays]
    validDays.reverse()

    lastOpen = pd.Timestamp(marketSchedule['market_open'][-2])
    lastClose = pd.Timestamp(marketSchedule['market_close'][-2])
    nextOpen = pd.Timestamp(marketSchedule['market_open'][-1])
    nextClose = pd.Timestamp(marketSchedule['market_close'][-1])

    isOpen = nowUTC >= nextOpen and nowUTC <= nextClose
    preMarket = nowUTC < nextOpen
    postMarket = nowUTC > nextClose

    clock = {}

    clock['nowUTC'] = nowUTC
    clock['lastOpen'] = lastOpen
    clock['lastClose'] = lastClose
    clock['nextOpen'] = nextOpen
    clock['nextClose'] = nextClose

    clock['isOpen'] = isOpen
    clock['preMarket'] = preMarket
    clock['postMarket'] = postMarket

    clock['validDays'] = validDays
    clock['marketSchedule'] = marketSchedule

    return clock


def gen_market_data(credentials, tckrs, settings, api, fullSend, fixedDate='', forceMDataPull=False, verbose=True,
                    modeling=False):
    # check if market is open
    clock = get_clock(fixedDate=fixedDate, modeling=modeling)
    print(credentials)
    paidSubscription = credentials['endpoint']['premium_data']

    if verbose:
        print('PRINTING CLOCK')

    for key, value in clock.items():
        if key != 'validDays':
            if key == 'marketSchedule':
                if verbose:
                    print(key, ':  ')
                    print(value)
                core_library.log_entry(logFile="project_log.txt", logText=(key, ':  '),
                                       logMode='a', gap=False)
                core_library.log_entry(logFile="project_log.txt", logText=(str(value)),
                                       logMode='a', gap=False)
            else:
                if verbose:
                    print(key, ':  ', value)
                core_library.log_entry(logFile="project_log.txt", logText=(str(key), ':  ', str(value)),
                                       logMode='a', gap=False)

    core_library.log_entry(logFile="project_log.txt", logText=("Modeling:", str(modeling)), logMode='a', gap=True)

    # print('FULL SEND',fullSend)
    actionDf = pd.read_csv(ROOT_DIR + r'/' + "data/ACTIONS DATA.csv")

    active_assets = transform_library.object_to_df(api.list_assets(status='active'))
    active_assets.sort_values('SYMBOL', inplace=True)
    active_assets = active_assets.reset_index(drop=True)
    # print(len(tckrs))
    # if tckrs is full stock pull, then add those in active_assets that are missing from get_tckrs(
    if fullSend:
        tckrs = list(set().union(*[tckrs, active_assets['SYMBOL'].to_list()]))
    # print(len(tckrs))
    print('FINAL STOCK SYMBOL POPULATION SIZE:', len(tckrs))

    keys = list(settings['marketData'].keys())

    for key in keys:
        # print(key)
        sourceFile = ROOT_DIR + r'/' + settings['marketData'][key]['file name']
        # print(sourceFile)
        fileExists = os.path.exists(sourceFile)
        postMarketDataExists = False
        if fileExists:

            fileTimestamp = pd.Timestamp(
                dt.datetime.fromtimestamp(os.path.getmtime(sourceFile)).astimezone()).tz_convert('UTC')
            # print('fileTimestamp',fileTimestamp,clock['nextClose'],fileTimestamp>clock['nextClose'])
            isFileValid = fileTimestamp.date() == clock['nowUTC'].date()
            postMarketDataExists = fileTimestamp > clock['nextClose']
        else:
            isFileValid = False

        # print('isFileValid',isFileValid)
        dataValid = (isFileValid and not forceMDataPull)

        # print('postMarketDataExists',postMarketDataExists)
        if key == 'DAILY MARKET DATA' and not modeling:
            if clock['isOpen']:
                if verbose:
                    print('MARKET IS OPEN, RE-SAMPLING DAILY STOCK DATA')
                dataValid = False
            if not postMarketDataExists:
                if verbose:
                    print('MARKET IS CLOSED, PULLING FINAL DATA SET FOR TODAY')
                dataValid = False

        # print('dataValid',dataValid)
        # print('')

        if (dataValid):
            print(key, 'saved Data is up to date...')
            core_library.log_entry(logFile="project_log.txt", logText=(key, ' saved Data is up to date...'),
                                   logMode='a', gap=False)
        else:

            print(key, 'Dataset is either missing or out of date, retrieving now...')
            core_library.log_entry(logFile="project_log.txt",
                                   logText=(key, ' Dataset is either missing or out of date, retrieving now...'),
                                   logMode='a', gap=False)

            offset = settings['marketData'][key]['offset']
            if clock['preMarket']:
                offset += 1
            if modeling:
                if clock['isOpen']:
                    offset += 1

            range = settings['marketData'][key]['range'] + offset

            if range > len(clock['validDays']):
                range = len(clock['validDays']) - 1
            # print(range,offset)

            startDate = clock['validDays'][range]
            endDate = clock['validDays'][offset]

            startDate = clock['marketSchedule']['market_open'].loc[str(startDate.date())]
            endDate = clock['marketSchedule']['market_close'].loc[str(endDate.date())]

            nowish = clock['nowUTC'] - relativedelta(minutes=15)
            timeOffset = endDate - relativedelta(minutes=15)
            # print('offset compare', nowish, endDate, (nowish) <= endDate)
            if not modeling:
                if key == 'DAILY MARKET DATA' and paidSubscription == False:
                    if clock['isOpen'] :
                        endDate = clock['nowUTC'] - relativedelta(minutes=15)
                        if nowish <= startDate:
                            startDate = startDate - relativedelta(minutes=15)
                    else:
                        if (nowish) <= endDate:
                            endDate = timeOffset
            startDate = pd.Timestamp(startDate.strftime("%Y-%m-%d %H:%M:%S"), tz='UTC').isoformat()
            endDate = pd.Timestamp(endDate.strftime("%Y-%m-%d %H:%M:%S"), tz='UTC').isoformat()

            # print(startDate.tzinfo)
            if verbose:
                print(key, 'Timeframe:', startDate, '-', endDate)
                # print('START: ', startDate, )
                # print('END: ', endDate)

            # if(key == 'YESTERDAY MARKET DATA'):
            # if (key == 'DAILY MARKET DATA'):
            if (True):
                # if key == 'MONTHLY MARKET DATA':
                data = extract_library.get_iex(credentials=credentials, api=api, symbols=tckrs,
                                               timeFrame=settings['marketData'][key]['IEX']['interval'],
                                               startDate=startDate, endDate=endDate, fileName=sourceFile,
                                               actionsDf=actionDf, verbose=verbose)
                # print('DATA')
                # print(data)
                if not data.empty:

                    data['DATETIME'] = pd.to_datetime(data['DATETIME'])
                    # print("PRINTING DATA")
                    # print(data)
                    # print(data.info())
                    statData = transform_library.m_data_to_stats(data, fileName=key, verbose=verbose)
                    #                print(statData.head(5).to_string())
                    mergedData = pd.merge(active_assets, statData, how="left", on=['SYMBOL'])

                    # mergedData = mergedData.dropna(how='any').reset_index(drop=True)
                    mergedData = mergedData.dropna(subset=['START PRICE']).reset_index(drop=True)
                    # print(mergedData.head(10).to_string())
                    if (key == 'YESTERDAY MARKET DATA'):
                        tckrs = mergedData['SYMBOL'].to_list()
                    # print('HERE I AM ', tckrs)
                    dbmsIO.file_save(mergedData, sourceFile)
                    core_library.log_entry(logFile="project_log.txt", logText=(key, " Saved..."), logMode='a')


def update_dbs(credentials, api, settings='', tckrs='', fixedDate = '', modeling=False, forceFDataPull=False, forceMDataPull=False,
               verbose=True):
    fullSend = False
    genFullSend = False
    if len(tckrs) == 0:
        # print(len(tckrs) )
        tckrs = get_tckrs()
        genFullSend = True
        fullSend = True

    if settings == '':
        settings, toggle = load_library.get_settings(fullSend)
    else:
        toggle = False


    # print(settings)

    # print('FULLSEND AND TOGGLE:',fullSend,toggle)
    if str(forceFDataPull).upper() == 'SKIP':
        extract_library.build_db()
    else:
        if fullSend and toggle:
            fullSend = False
        extract_library.get_fun_data(tckrs=tckrs, fullSend=fullSend, settings=settings, forceFDataPull=forceFDataPull,
                                     verbose=verbose)

    gen_market_data(credentials=credentials, tckrs=tckrs, fixedDate =fixedDate,fullSend=genFullSend, settings=settings,
                    api=api, forceMDataPull=forceMDataPull,
                    verbose=verbose, modeling=modeling)


def init():
    global scriptStart
    scriptStart = dt.datetime.now()
    core_library.log_entry(logFile="project_log.txt",
                           logText=(dt.datetime.now().strftime("%m/%d/%Y, %H:%M:%S"), " Project Starting... "),
                           logMode='w')
    ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

    while not api_library.internet_test():
        print(dt.datetime.now(), "Internet Connection failed... ")
        core_library.log_entry(logFile="project_log.txt", logText=(
            dt.datetime.now().strftime("%m/%d/%Y, %H:%M:%S"),
            "Internet Connection failed... "), logMode='a')

    # print(ROOT_DIR)
    # api = login()
    credentials = api_library.init_credentials()

    loginSuccessful = False
    attempts = 0
    while not loginSuccessful:
        loginSuccessful, api, credentials = api_library.login(credentials)
        attempts += 1
        if attempts > 5:
            return loginSuccessful, api, credentials
    return loginSuccessful, api, credentials


def get_table(dataset=[], raw=False):
    if type(dataset) != type(list()):
        dataset = [dataset]
    output = {}
    output["marketData"] = {}
    settings = load_library.get_settings()
    for dset in dataset:
        output["marketData"][dset] = {}
        # print(dset)
        fileName = ROOT_DIR + r'/' + settings['marketData'][dset]["file name"]
        # print(fileName)
        statData = pd.read_csv(fileName)
        # print(statData)
        output["marketData"][dset]['STAT DATA'] = statData
        if raw:
            name, ext = os.path.splitext(fileName)
            fileName = name + '_RAW' + ext
            rawData = pd.read_csv(fileName)
            # print(rawData)
            output["marketData"][dset]['RAW DATA'] = rawData
    fileName = "data/COMPANY INFO DATA.json"
    #print(os.stat(ROOT_DIR + r'/' +fileName).st_size)
    if os.stat(ROOT_DIR + r'/' +fileName).st_size>5:
        coInfo = dbmsIO.extract_json(fileName=fileName)
        coInfo = pd.DataFrame.from_dict(coInfo['COMPANY INFO'])
        output["Company Info"] = coInfo

    return output


def get_datasets():
    return list(load_library.get_settings()['marketData'].keys())


def get_tckrs():
    return extract_library.get_tckrs()

def obj_to_df(obj):
    return transform_library.object_to_df(obj)

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
