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
from dateutil.relativedelta import relativedelta

#internal libraries
import coreFuncs

def getClock():
    print('')
    localTZOffset = time.timezone / 3600.0
    #get local time and timezone
    nowTS = pd.Timestamp(dt.datetime.now().astimezone())
    localTZ = nowTS.tzinfo

    #convert to UTC for standard comparison
    nowUTC = pd.Timestamp(dt.datetime.now().astimezone()).tz_convert('UTC')

    nyse = mcal.get_calendar('NYSE')
    lastMonth = nyse.valid_days(
        start_date=nowUTC.date() - relativedelta(months=1),
        end_date=nowUTC.date())
    lastWeek = nyse.valid_days(
        start_date=nowUTC.date() - relativedelta(weeks=1),
        end_date=nowUTC.date())
    lastYear = nyse.valid_days(
        start_date=nowUTC.date() - relativedelta(years=1),
        end_date=nowUTC.date())
    lastDate = lastWeek[-1]

    print('last year',lastYear)
    print('last month', lastMonth)
    print('last week', lastWeek)
    print('last date', lastDate)


    todaysSchedule = nyse.schedule(start_date=nowUTC.date(), end_date=nowUTC.date())
    lastOpen = pd.Timestamp(todaysSchedule['market_open'][0])
    lastClose = pd.Timestamp(todaysSchedule['market_close'][0])

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