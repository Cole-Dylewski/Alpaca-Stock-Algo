# standard libraries
import json
import os
import tkinter.filedialog as fd

import dbmsIO


def get_settings(fullsend=''):
    default_settings = {
        "marketData":
            {
                "DAILY MARKET DATA":
                    {
                        "IEX":
                            {
                                "dateRange": 1,
                                "interval": "1Min"
                            },
                        "YAHOO":
                            {
                                "dateRange": "1 day",
                                "interval": "1 minute"
                            },
                        "offset": 0,
                        "range": 0,
                        "raw": "True",
                        "file name": "data/DAILY MARKET DATA.csv"
                    },
                "YESTERDAY MARKET DATA":
                    {
                        "IEX":
                            {
                                "dateRange": 1,
                                "interval": "1Min"
                            },
                        "YAHOO": {
                            "dateRange": "1 day",
                            "interval": "1 minute"
                        },
                        "offset": 1,
                        "range": 1,
                        "raw": "True",
                        "file name": "data/YESTERDAY MARKET DATA.csv"
                    },
                "WEEKLY MARKET DATA":
                    {
                        "IEX":
                            {
                                "dateRange": 7,
                                "interval": "5Min"
                            },
                        "YAHOO": {
                            "dateRange": "5 days",
                            "interval": "5 minutes"
                        },
                        "offset": 1,
                        "range": 7,
                        "raw": "True",
                        "file name": "data/WEEKLY MARKET DATA.csv"
                    },
                "MONTHLY MARKET DATA":
                    {
                        "IEX":
                            {
                                "dateRange": 30,
                                "interval": "15Min"
                            },
                        "YAHOO": {
                            "dateRange": "1 month",
                            "interval": "1 hour"
                        },
                        "offset": 1,
                        "range": 30,
                        "raw": "True",
                        "file name": "data/MONTHLY MARKET DATA.csv"
                    },
                "YRLY MARKET DATA":
                    {
                        "IEX": {
                            "dateRange": 365,
                            "interval": "1Day"
                        },
                        "YAHOO": {
                            "dateRange": "1 year",
                            "interval": "1 day"
                        },
                        "offset": 1,
                        "range": 365,
                        "raw": "True",
                        "file name": "data/YRLY MARKET DATA.csv"
                    }
            },
        "fundamentals":
            {
                "ACTIONS":
                    {
                        "file name": "data/ACTIONS DATA.csv"
                    },
                "Company Info": {
                    "file name": "data/COMPANY INFO DATA.csv"
                }
            },
        "strategies":
            {
                "MOMENTUM": 20,
                "SCALP": 20,
                "DAY": 20,
                "EOD": 20,
                "SWING": 20
            },
        "fullSend": fullsend
    }
    if fullsend == '':
        settings = dbmsIO.extract_json(fileName="settings.json", defaultValue=default_settings)
        return settings

    else:

        settings = dbmsIO.extract_json(fileName="settings.json", defaultValue=default_settings)
        dbmsIO.load_json(fileName="settings.json", jsonData=default_settings)
        toggle = False
        new = str(default_settings['fullSend']).strip()
        old = str(settings['fullSend']).strip()
        #print('Old:',old,'New:',new)
        if new != old:
            toggle = True

        return settings,toggle


ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
