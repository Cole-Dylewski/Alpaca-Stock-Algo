# standard libraries
import pandas as pd
import os
import datetime as dt

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


def get_clock(modeling=False):
    # localTZOffset = time.timezone / 3600.0
    # get local time and timezone
    nowTS = pd.Timestamp(dt.datetime.now().astimezone())
    #nowTS = pd.Timestamp(dt.datetime(year=2022, month=4, day=6, hour=2, minute=40).astimezone())

    localTZ = nowTS.tzinfo

    # convert to UTC for standard comparison
    nowUTC = nowTS.tz_convert('UTC')
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


def gen_market_data(credentials, tckrs, settings, api, forceMDataPull=False, verbose=True, modeling=False):
    # check if market is open
    clock = get_clock(modeling)
    if verbose:
        print('PRINTING CLOCK')
        for key, value in clock.items():
            if key !='validDays':
                if key =='marketSchedule':
                    print(key, ':  ')
                    print(value)
                else:
                    print(key, ':  ', value)

    #    print(clock)
    # apiClock = api.get_clock()
    # print(apiClock)
    # print(clock['marketSchedule'])

    actionDf = pd.read_csv(ROOT_DIR + r'/' + "data/ACTIONS DATA.csv")

    active_assets = transform_library.object_to_df(api.list_assets(status='active'))
    active_assets.sort_values('SYMBOL', inplace=True)
    active_assets = active_assets.reset_index(drop=True)
    keys = list(settings['marketData'].keys())

    for key in keys:
        # print(key)
        sourceFile = ROOT_DIR + r'/' + settings['marketData'][key]['file name']
        # print(sourceFile)
        fileExists = os.path.exists(sourceFile)
        postMarketDataExists = False
        if fileExists:

            fileTimestamp = pd.Timestamp(dt.datetime.fromtimestamp(os.path.getmtime(sourceFile)).astimezone()).tz_convert('UTC')
            #print('fileTimestamp',fileTimestamp,clock['nextClose'],fileTimestamp>clock['nextClose'])
            isFileValid = fileTimestamp.date() == clock['nowUTC'].date()
            postMarketDataExists = fileTimestamp > clock['nextClose']
        else:
            isFileValid = False

        # print('isFileValid',isFileValid)
        dataValid = (isFileValid and not forceMDataPull)

        #print('postMarketDataExists',postMarketDataExists)
        if key == 'DAILY MARKET DATA':
            if clock['isOpen']:
                dataValid = False
            if not postMarketDataExists:
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
            # print(startDate.date(), endDate.date())
            # print(clock['marketSchedule'].loc[str(endDate.date())])
            # print(clock['marketSchedule'].loc[str(startDate.date())])
            # print(startDate, endDate)

            startDate = clock['marketSchedule']['market_open'].loc[str(startDate.date())]
            endDate = clock['marketSchedule']['market_close'].loc[str(endDate.date())]

            startDate = pd.Timestamp(startDate.strftime("%Y-%m-%d %H:%M:%S"), tz='UTC').isoformat()
            nowish = clock['nowUTC'] - relativedelta(minutes=15)
            timeOffset = endDate - relativedelta(minutes=15)
            #print('offset compare', nowish, timeOffset, (nowish) > timeOffset)
            if not modeling:
                if key == 'DAILY MARKET DATA':
                    if clock['isOpen']:
                        endDate = clock['nowUTC'] - relativedelta(minutes=15)
                    else:
                        if (nowish) > timeOffset:
                            endDate = endDate

            endDate = pd.Timestamp(endDate.strftime("%Y-%m-%d %H:%M:%S"), tz='UTC').isoformat()

            # print(startDate.tzinfo)
            if verbose:
                print(key,'Timeframe:',startDate,'-',endDate)
                #print('START: ', startDate, )
                #print('END: ', endDate)

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
                    mergedData = mergedData.dropna(how='any').reset_index(drop=True)
                    if (key == 'YESTERDAY MARKET DATA'):
                        tckrs = mergedData['SYMBOL'].to_list()
                    dbmsIO.file_save(mergedData, sourceFile)
                    core_library.log_entry(logFile="project_log.txt", logText=(key, " Saved..."), logMode='a')


def update_dbs(credentials, api, settings='', tckrs='', modeling=False, forceFDataPull=False, forceMDataPull=False,
               verbose=True):
    fullSend = False
    if len(tckrs) == 0:
        # print(len(tckrs) )
        tckrs = extract_library.get_tckrs()
        fullSend = True

    if settings == '':
        settings, toggle = load_library.get_settings(fullSend)
    if fullSend and toggle:
        fullSend = False
    # print(settings)

    # print(fullSend,tckrs)
    # tckrs = ['CIG', 'SWI', 'AIV', 'BRBS', 'ELP', 'ITA', 'MZZ', 'QLD', 'ROL', 'SDD', 'SIJ', 'SMDD', 'SSG', 'SZK']
    # tckrs = ['TSLA', 'MSFT', 'FORD', 'AAPL']
    # print(tckrs)
    # tckrs = random.sample(tckrs, 100)
    # tckrs = tckrs[0:100]
    # print('this part',api, credentials)
    extract_library.get_fun_data(tckrs=tckrs, fullSend=fullSend, settings=settings, forceFDataPull=forceFDataPull,
                                 verbose=verbose)
    gen_market_data(credentials=credentials, tckrs=tckrs, settings=settings,
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
    settings = load_library.get_settings()
    companyInfoDf = pd.read_csv(ROOT_DIR + r'/' + "data/COMPANY INFO DATA.csv")
    for dset in dataset:
        output[dset] = {}
        # print(dset)
        fileName = ROOT_DIR + r'/' + settings['marketData'][dset]["file name"]
        # print(fileName)
        statData = pd.read_csv(fileName)
        # print(statData)
        output[dset]['STAT DATA'] = statData
        if raw:
            name, ext = os.path.splitext(fileName)
            fileName = name + '_RAW' + ext
            rawData = pd.read_csv(fileName)
            # print(rawData)
            output[dset]['RAW DATA'] = rawData
    output['COMPANY INFO DATA'] = companyInfoDf

    return output


def get_datasets():
    return list(load_library.get_settings()['marketData'].keys())


ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
