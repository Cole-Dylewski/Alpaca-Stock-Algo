# standard libraries

import datetime as dt

# non-standard libraries
import os, sys; sys.path.append(os.path.dirname(os.path.realpath(__file__)))
# internal libraries
import core_library
import extract_library
from hub import update_dbs,init
import api_library
import dbmsIO

# global variables
scriptStart = ''







if __name__ == '__main__':
    loginSuccessful, api, credentials = init()
    # print(loginSuccessful,api,credentials)

    if loginSuccessful:
        # print(api.get_account())
        # update_dbs(credentials,api)
        update_dbs(credentials,api,tckrs=['TSLA', 'MSFT', 'FORD', 'AAPL'], modeling=False, forceFDataPull=True, forceMDataPull=True, verbose=True)
    #ttr = str(dt.timedelta(seconds=(dt.datetime.now() - scriptStart).seconds))
    #print("script time to run:", ttr)
    #core_library.log_entry(logFile="project_log.txt", logText=("script time to run: ", ttr), logMode='a')
