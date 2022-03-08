#standard libraries
import random
import time
import pytz
import pandas
import pandas as pd
import os
import datetime as dt



#non-standard libraries
import pandas_market_calendars as mcal
from tzlocal import get_localzone

#internal libraries
import coreFuncs

def getClock():
    print('')
    localTZOffset = time.timezone / 3600.0
    localTZ = pd.Timestamp(dt.datetime.now().astimezone()).tzinfo
    nowTS = pd.Timestamp(dt.datetime.now().astimezone())
    nowUTC = pd.Timestamp(dt.datetime.now().astimezone()).tz_convert('UTC')

    #nowTS = pd.Timestamp(dt.datetime.now().astimezone()).tz_convert(localTZ)

    nyse = mcal.get_calendar('NYSE')
    lastWeek = nyse.valid_days(
        start_date=nowUTC.date() - dt.timedelta(days=7),
        end_date=nowUTC.date())
    lastDate = nyse.valid_days(
        start_date=nowUTC.date() - dt.timedelta(days=7),
        end_date=nowUTC.date())[-1]

    print('last week', lastWeek)
    print('last date', lastDate)
    weekSchedule = nyse.schedule(start_date=lastWeek[0].date(), end_date=nowUTC.date())
    todaysSchedule = nyse.schedule(start_date=nowUTC.date(), end_date=nowUTC.date())
    lastOpen = pd.Timestamp(todaysSchedule['market_open'][0])
    lastClose = pd.Timestamp(todaysSchedule['market_close'][0])
    print(weekSchedule)
    print(todaysSchedule)
    print('Last Open',lastOpen.tz_convert(localTZ))
    #print(dt.datetime.fromtimestamp(lastOpen))
    print('Last Close',lastClose.tz_convert(localTZ))
    print('Now',nowTS)
    open = nowUTC>lastOpen and nowUTC<lastClose
    print(open)

def getFundamentalData(tckrs):
    byPassClockCheck = False
    print(tckrs)
    #print(dt.datetime.now())
    nyse = mcal.get_calendar('NYSE')

    #check is market is open
    getClock()