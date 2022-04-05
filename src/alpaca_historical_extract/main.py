# standard libraries

import datetime as dt

# non-standard libraries

# internal libraries
import core_library
import extract_library
import hub
import api_library
import dbmsIO

# global variables
scriptStart = ''

if __name__ == '__main__':
    loginSuccessful, api, credentials = hub.init()
    # print(loginSuccessful,api,credentials)

    if loginSuccessful:
        # print(api.get_account())

        hub.update_dbs(credentials, api, tckrs=['TSLA', 'AAPL', 'MSFT'], modeling=False, forceFDataPull=True,
                       forceMDataPull=True, verbose=True)
        keys = hub.get_datasets()
        print(keys)
        dataset = hub.get_table(dataset=keys, raw=True)
        # print(dataset)
        # data = hub.get_table(keys[0],True)
        # print(data)
    # ttr = str(dt.timedelta(seconds=(dt.datetime.now() - scriptStart).seconds))
    # print("script time to run:", ttr)
    # core_library.log_entry(logFile="project_log.txt", logText=("script time to run: ", ttr), logMode='a')
