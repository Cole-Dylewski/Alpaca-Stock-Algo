# standard libraries

import datetime as dt

# non-standard libraries

# internal libraries
import hub
import random


# global variables
scriptStart = ''

if __name__ == '__main__':
    loginSuccessful, api, credentials = hub.init()
    # print(loginSuccessful,api,credentials)

    if loginSuccessful:
        # print(api.get_account())
        tckrs = hub.get_tckrs()
        #tckrs = ''
        #tckrs = random.sample(tckrs, 500)
        tckrs = ['TSLA', 'AAPL', 'MSFT']
        fixedDate = dt.datetime(year=2022, month=3, day=12, hour=10, minute=40)
        hub.update_dbs(credentials, api, tckrs=tckrs, fixedDate = fixedDate,
                       modeling=False, forceFDataPull=False, forceMDataPull=True,
                       verbose=False)
        keys = hub.get_datasets()
        # print(keys)
        #dataset = hub.get_table(dataset=keys, raw=False)
        # print(dataset)
        #for key, value in dataset.items():
         #   print(key)
          #  print(value)
            # print(value['STAT DATA'].to_string())
        # print(dataset['DAILY MARKET DATA'])
        # data = hub.get_table(keys[0],True)
        # print(data)
    # ttr = str(dt.timedelta(seconds=(dt.datetime.now() - scriptStart).seconds))
    # print("script time to run:", ttr)
    # core_library.log_entry(logFile="project_log.txt", logText=("script time to run: ", ttr), logMode='a')
