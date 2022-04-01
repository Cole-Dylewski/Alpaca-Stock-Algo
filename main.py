# standard libraries
import os
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


def update_dbs(tckrs='',modeling=False,forceFDataPull = False,forceMDataPull = False,verbose = True):
    if __name__ == '__main__':
        if loginSuccessful:
            settings = dbmsIO.extract_json("settings.json")
            # print(settings)
            if len(tckrs)==0:
                tckrs = extract_library.get_tckrs()
            # tckrs = ['CIG', 'SWI', 'AIV', 'BRBS', 'ELP', 'ITA', 'MZZ', 'QLD', 'ROL', 'SDD', 'SIJ', 'SMDD', 'SSG', 'SZK']
            #tckrs = ['TSLA','MSFT','FORD','AAPL']
            # print(tckrs)
            # tckrs = random.sample(tckrs, 100)
            # tckrs = tckrs[0:100]
            # print('this part',api, credentials)
            extract_library.get_fun_data(tckrs=tckrs, settings=settings, forceFDataPull=forceFDataPull, verbose=verbose)
            hub.gen_market_data(credentials=credentials, tckrs=tckrs, settings=settings,
                                api=api, forceMDataPull=forceMDataPull,
                                verbose=verbose, modeling = modeling)


def init():

    if __name__ == '__main__':
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


if __name__ == '__main__':
    loginSuccessful, api, credentials = init()
    # print(loginSuccessful,api,credentials)

    if loginSuccessful:
        # print(api.get_account())
        # update_dbs(credentials,api)
        update_dbs()
    ttr = str(dt.timedelta(seconds=(dt.datetime.now() - scriptStart).seconds))
    print("script time to run:", ttr)
    core_library.log_entry(logFile="project_log.txt", logText=("script time to run: ", ttr), logMode='a')
