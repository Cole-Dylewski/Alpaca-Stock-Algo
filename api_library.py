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
import core_library
import extract_library
import hub
import load_library
import dbmsIO

def enterCredentials(credentials):
    credentials['endpoint']['apiKey'] = input("Enter API KEY:")
    #print(credentials['endpoint']['apiKey'])
    credentials['endpoint']['apiSecret'] = input("Enter API SECRET:")
    #print(credentials['endpoint']['apiSecret'])
    credentials['endpoint']['base_url'] = input("Enter BASE URL: (ex:https://paper-api.alpaca.markets)")
    return credentials

def initCredentials():
    credentials = {
        "endpoint": {
            "apiKey": "",
            "apiSecret": "",
            "base_url": "",
            "api_version": "v2"
        }
    }
    credentials = dbmsIO.extractJson(fileName='credentials.json',defaultValue=credentials)

    if ((credentials['endpoint']['apiKey']=="") or (credentials['endpoint']['apiSecret']=="")):
        credentials = enterCredentials(credentials)
    return credentials

#check if internet is working, return bool. Designed as time delayed while loop
def internetTest():
    url = "http://www.google.com"
    timeout = 5
    try:
        request = requests.get(url, timeout=timeout)
        print("Connected to the Internet")
        core_library.logEntry(logFile="project_log.txt",
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
        print(api.get_account())

        dbmsIO.loadJson("credentials.json", credentials)

        return True, api, credentials
    except Exception as e:
        print("LOGIN FAILED")
        print(e)
        enterCredentials(credentials)
        return False, api, credentials



















