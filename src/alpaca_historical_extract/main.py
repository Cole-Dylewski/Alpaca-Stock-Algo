# standard libraries

import datetime as dt

# non-standard libraries

# internal libraries
import hub
import random

# global variables
scriptStart = ''

settings = {
    "marketData": {
        "DAILY MARKET DATA": {
            "IEX": {
                "dateRange": 1,
                "interval": "1Min"
            },
            "YAHOO": {
                "dateRange": "1 day",
                "interval": "1 minute"
            },
            "offset": 0,
            "range": 0,
            "raw": "True",
            "file name": "data/DAILY MARKET DATA.csv"
        }
    },
    "fundamentals": {
        "ACTIONS": {
            "file name": "data/ACTIONS DATA.csv"
        },
        "Company Info": {
            "file name": "data/COMPANY INFO DATA.json"
        }
    },
    "strategies": {
        "MOMENTUM": 20,
        "SCALP": 20,
        "DAY": 20,
        "EOD": 20,
        "SWING": 20
    },
    "fullSend": True
}

if __name__ == '__main__':
    loginSuccessful, api, credentials = hub.init()
    # print(loginSuccessful,api,credentials)

    if loginSuccessful:
        # print(api.get_account())
        tckrs = hub.get_tckrs()
        # tckrs = ''
        # tckrs = random.sample(tckrs, 500)
        tckrs = ['TSLA', 'AAPL', 'MSFT']
        fixedDate = ''
        #fixedDate = dt.datetime(year=2022, month=7, day=22, hour=7, minute=40)
        if True:
            hub.update_dbs(
                credentials, api,settings='', tckrs=tckrs, fixedDate = fixedDate,
                modeling=False, forceFDataPull=True, forceMDataPull=True,
                verbose=True)
        if False:
            hub.update_dbs(
                credentials, api,settings='', tckrs=tckrs, fixedDate = fixedDate,
                modeling=False, forceFDataPull=True, forceMDataPull=True,
                verbose=True)
       # hub.update_dbs(credentials, api, tckrs=['TSLA', 'AAPL', 'MSFT', 'TWTR'], modeling=False, settings='',
        #               forceFDataPull='SKIP', forceMDataPull=False, verbose=True,timeframe=60)

        keys = hub.get_datasets()
        # print(keys)
        # dataset = hub.get_table(dataset=keys, raw=False)
        dailyDataSet = hub.get_table(dataset='DAILY MARKET DATA', raw=True)
        print(dailyDataSet['marketData']['DAILY MARKET DATA']['STAT DATA'].to_string())
        # print(dataset)
        # for key, value in dataset.items():
        #   print(key)
        #  print(value)
        # print(value['STAT DATA'].to_string())
        # print(dataset['DAILY MARKET DATA'])
        # data = hub.get_table(keys[0],True)
        # print(data)
    # ttr = str(dt.timedelta(seconds=(dt.datetime.now() - scriptStart).seconds))
    # print("script time to run:", ttr)
    # core_library.log_entry(logFile="project_log.txt", logText=("script time to run: ", ttr), logMode='a')
