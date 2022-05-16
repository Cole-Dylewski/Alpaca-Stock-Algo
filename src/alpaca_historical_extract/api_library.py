# standard libraries
import time
import datetime as dt
import requests

# non-standard libraries
import alpaca_trade_api as tradeapi

# internal libraries
import core_library
import dbmsIO


def enter_credentials(credentials):
    credentials['endpoint']['apiKey'] = input("Enter API KEY:")
    # print(credentials['endpoint']['apiKey'])
    credentials['endpoint']['apiSecret'] = input("Enter API SECRET:")
    # print(credentials['endpoint']['apiSecret'])
    credentials['endpoint']['base_url'] = input("Enter BASE URL: (ex:https://paper-api.alpaca.markets)")
    premiumDataSelected = False
    while premiumDataSelected != True:
        premiumData = input("USE PREMIUM DATA SUBSCRIPTION?: 'TRUE' OR 'FALSE'")
        if premiumData.upper() == str(True).upper():
            print("PREMIUM DATA SERVICE SELECTED")
            credentials['endpoint']["premium_data"] = True
            premiumDataSelected = True
        elif premiumData.upper() == str(False).upper():
            print("STANDARD DATA SERVICE SELECTED")
            credentials['endpoint']["premium_data"] = False
            premiumDataSelected = True
        else:
            print("Data Subscription input not recognized, reattempting login")
    return credentials


def init_credentials():
    credentials = {
        "endpoint": {
            "apiKey": "",
            "apiSecret": "",
            "base_url": "",
            "api_version": "v2",
            "premium_data": False

        }
    }
    credentials = dbmsIO.extract_json(fileName='credentials.json', defaultValue=credentials)

    if (credentials['endpoint']['apiKey'] == "") or (credentials['endpoint']['apiSecret'] == ""):
        credentials = enter_credentials(credentials)
    return credentials


# check if internet is working, return bool. Designed as time delayed while loop
def internet_test():
    url = "http://www.google.com"
    timeout = 5
    try:
        request = requests.get(url, timeout=timeout)
        print("Connected to the Internet")
        core_library.log_entry(logFile="project_log.txt",
                               logText=(dt.datetime.now().strftime("%m/%d/%Y, %H:%M:%S"), " Connected to the Internet"),
                               logMode='a')

        return True
    except (requests.ConnectionError, requests.Timeout) as exception:
        # print("No internet connection...")
        time.sleep(5)
        return False


def login(credentials):
    try:
        api = tradeapi.REST(
            key_id=credentials['endpoint']['apiKey'],
            secret_key=credentials['endpoint']['apiSecret'],
            base_url=credentials['endpoint']['base_url'],
            api_version=credentials['endpoint']['api_version']
        )
        account = api.get_account()
        print("LOGIN SUCCESSFUL")
        #print(api.get_account())

        dbmsIO.load_json("credentials.json", credentials)

        return True, api, credentials
    except Exception as e:
        print("LOGIN FAILED")
        print(e)
        enter_credentials(credentials)
        return False, api, credentials


def get_barset(credentials, symbols, timeframe, start, end, limit=1000, adjustment='raw', feed='sip',pageToken=''):
    #url = credentials['endpoint']['base_url'] + r"/" + credentials['endpoint']['api_version'] + r"/stocks/bars"
    url = r'https://data.alpaca.markets'+ r"/" + credentials['endpoint']['api_version'] + r"/stocks/bars"
    headers = {
        "APCA-API-KEY-ID": credentials['endpoint']['apiKey'],
        "APCA-API-SECRET-KEY": credentials['endpoint']['apiSecret']
    }
    symbolStr = ''
    for i in range(len(symbols)):
        if i==0:
            symbolStr=symbols[i]
        else:
            symbolStr+= ','+symbols[i]

    params = {
        "symbols": symbolStr,
        "timeframe":timeframe,
        "start": start,
        "end": end,
        "limit": limit,
        "adjustment": adjustment,
        "feed": feed,
        'page_token':pageToken
    }
    try:
        response = requests.get(
            url=url,
            headers=headers,
            params=params
        )
        #print(response.content)
        #data = response.json()
        if response.status_code == 200:
            #print(response.status_code)
            data = response.json()
            return data['bars'], data['next_page_token']

        elif response.status_code == 429:
            #print('params',params)
            #print('url',url)
            #print('headers',headers)

            print(response.status_code)
            print(response.content)
            print('Max limit of API CALLS per MINUTE reached. Delaying Extraction to reset Request limit')
            time.sleep(60)
            return {},pageToken
        elif response.status_code == 422:
            print(response.status_code)
            print(response.content)
            return {}, None

        else:
            print(response.status_code)
            print(response.content)
            time.sleep(60)
            return {}, pageToken
    except Exception as e:
        print(e)
        time.sleep(60)
        return {}, pageToken
