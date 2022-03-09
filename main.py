#standard libraries
import random
import time
import pandas as pd
import os
import datetime as dt
import json
import requests

#non-standard libraries
import pandas_market_calendars as mcal
import alpaca_trade_api as tradeapi
from yahoo_fin import stock_info as si

#internal libraries
import coreFuncs
import extract

#global variables
endpoint = {}
api = ''
marketData = {}
fundamentalData = {}
strats = {}
tckrs = []
ROOT_DIR = ''
credentials = {
  "endpoint": {
		"apiKey" : "",
		"apiSecret" : "",
		"base_url" : "https://paper-api.alpaca.markets",
		"api_version" : "v2"
	}
}




#check if internet is working, return bool. Designed as time delayed while loop
def internetTest():
    url = "http://www.google.com"
    timeout = 5
    try:
        request = requests.get(url, timeout=timeout)
        print("Connected to the Internet")
        coreFuncs.logEntry(logFile="project_log.txt",
                       logText=(dt.datetime.now().strftime("%m/%d/%Y, %H:%M:%S"), " Connected to the Internet"),
                       logMode='a')

        return True
    except (requests.ConnectionError, requests.Timeout) as exception:
        # print("No internet connection...")
        time.sleep(5)
        return False

def enterCredentials():
    global credentials
    credentials['endpoint']['apiKey'] = input("Enter API KEY:")
    #print(credentials['endpoint']['apiKey'])
    credentials['endpoint']['apiSecret'] = input("Enter API SECRET:")
    #print(credentials['endpoint']['apiSecret'])

def initCredentials():
    global credentials
    attempts =0

    credentialsFileName = ROOT_DIR + r"/credentials.json"
    if not os.path.exists(credentialsFileName):
        with open(credentialsFileName, "x") as credentials_file:
            json.dump(credentials,credentials_file)
            credentials_file.close()


    #print("credentials file:", credentialsFileName)
    with open(credentialsFileName, "r") as credentials_file:
        credentials = json.load(credentials_file)


        #print(credentials)
        #print(credentials['endpoint']['apiKey']=="")
        #print(credentials['endpoint']['apiSecret']=="")

    if ((credentials['endpoint']['apiKey']=="") or (credentials['endpoint']['apiSecret']=="")):
        enterCredentials()


def login(credentials):
    global api
    attempts = 0
    while(attempts<5):
        try:

            global api
            api = tradeapi.REST(
                key_id=credentials['endpoint']['apiKey'],
                secret_key=credentials['endpoint']['apiSecret'],
                base_url=credentials['endpoint']['base_url'],
                api_version=credentials['endpoint']['api_version']
            )
            account = api.get_account()
            print("LOGIN SUCCESSFUL")
            print(api.get_account())

            credentialsFileName = ROOT_DIR + r"/credentials.json"
            with open(credentialsFileName, "w") as credentials_file:
                json.dump(credentials, credentials_file)
                credentials_file.close()
            return True

        except Exception as e:
            attempts += 1
            print("LOGIN FAILED")
            print(e)
            print("Remaining Attempts:", 5-attempts)
            enterCredentials()
    return False


#read project settings json
def getSettings():

    settingsFileName = ROOT_DIR + r"/settings.json"
    print("settings file:", settingsFileName)
    with open(settingsFileName, "r") as settings_file:
        settings = json.load(settings_file)

    #print(settings)
    return settings

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

if __name__ == '__main__':

    scriptStart = dt.datetime.now()
    coreFuncs.logEntry(logFile="project_log.txt",
                   logText=(dt.datetime.now().strftime("%m/%d/%Y, %H:%M:%S"), " Project Starting... "),
                   logMode='w')
    ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
    while (not internetTest()):
        print(dt.datetime.now(), "Internet Connection failed... ")
        coreFuncs.logEntry(logFile="project_log.txt",
                       logText=(dt.datetime.now().strftime("%m/%d/%Y, %H:%M:%S"), "Internet Connection failed... "),
                       logMode='a')

    # print(ROOT_DIR)
    #api = login()
    initCredentials()
    if(login(credentials)):
        login(credentials)
        settings = getSettings()
        print(settings)
        #tckrs = getTCKRS()
        tckrs = ['CIG', 'SWI', 'AIV', 'BRBS', 'ELP', 'ITA', 'MZZ', 'QLD', 'ROL', 'SDD', 'SIJ', 'SMDD', 'SSG', 'SZK']
        #print(tckrs)
        extract.fundamentalData(tckrs,settings)
        extract.marketData(tckrs,settings,api)
        ttr = str(dt.timedelta(seconds=(dt.datetime.now() - scriptStart).seconds))
        print("script time to run:", ttr)
        coreFuncs.logEntry(logFile="project_log.txt",
                           logText=("script time to run: ", ttr),
                           logMode='a')
    else:
        print("Too many failed login attempts, ending program")