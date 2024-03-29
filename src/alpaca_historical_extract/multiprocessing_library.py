# standard libraries
import pandas as pd
import datetime as dt
import math

# non-standard libraries


import yfinance as yf

# internal libraries
import core_library as basic
import dbmsIO


def access_data(infoList, actionsList, tckr):
    # print('process id:', os.getpid())
    # print(tckr)
    tempDf = pd.DataFrame()
    data = yf.Ticker(tckr)
    try:

        info = {}
        info['SYMBOL'] = tckr
        info.update(data.info)
        # print(info)
        if (len(info) > 3 and len(info) < 154):
            infoList.append(info)

    except Exception as e:
        x = 1
        # print('ERROR',e,"AFFECTED TCKR:",tckr)
        # print("THIS DROPPED",df[df['SYMBOL']==tckr].reset_index(drop=True).head(10).to_string())
    try:

        actions = data.actions
        tempDf['DATETIME'] = actions.index.tolist()
        actions = actions.reset_index(drop=True)
        tempDf['DIVIDENDS'] = actions['Dividends']
        tempDf['SPLITS'] = actions['Stock Splits']
        tempDf.insert(0, 'SYMBOL', tckr)
        actionsList.append(tempDf)

    except Exception as e:
        x = 1
        # print('ERROR', e, "AFFECTED TCKR:", tckr)
        # print("THIS DROPPED",df[df['SYMBOL']==tckr].reset_index(drop=True).head(10).to_string())


def get_company_data(ROOT_DIR, tckrs, coreMultiplier=1, verbose=True):
    from multiprocessing import Process, Manager
    from multiprocessing import cpu_count
    if verbose:
        print(f'starting stock company data extraction on {cpu_count()} cores')

    counter = 0
    recordCount = cpu_count() * coreMultiplier
    totalRecords = len(tckrs)
    increment = 5
    limit = math.ceil(totalRecords / recordCount)
    lastPercentComplete = increment
    tStart = dt.datetime.now()
    tempDT = dt.datetime.now()

    for i in range(limit):
        # print(i)
        start = i * recordCount
        end = (i + 1) * recordCount

        if end > totalRecords:
            end = totalRecords
        percentComplete = round((end / totalRecords) * 100, 2)
        # print(start, end)
        # print(tckrs[start:end])
        subTckrs = tckrs[start:end]
        # print(subTckrs)

        with Manager() as manager:
            infoList = manager.list()
            actionsList = manager.list()
            processes = []
            for tckr in subTckrs:
                # print("THIS PART")
                p = Process(target=access_data, args=(infoList, actionsList, tckr))
                p.start()
                processes.append(p)
            for p in processes:
                # print("THIS OTHER PART")
                p.join()

            infoList = [x for x in infoList]
            actionsList = [x for x in actionsList]
            infoDf = pd.DataFrame(infoList)
            actionDf = pd.concat(actionsList)

            dbmsIO.to_csv(position=counter, data=actionDf, tableName=ROOT_DIR + r"/data/ACTIONS DATA.csv", raw=False)
            #dbmsIO.to_csv(position=counter, data=infoDf, tableName=ROOT_DIR + "/data/COMPANY INFO DATA.csv", raw=False)

            dbmsIO.df_to_json(position=counter, data=infoDf, tableName=ROOT_DIR + "/data/COMPANY INFO DATA.json",completed= i==limit-1)

        counter = counter + 1
        if (verbose):
            if percentComplete >= lastPercentComplete:
                lastPercentComplete = round(lastPercentComplete + increment, 0)
                timeThusFar = dt.datetime.now() - tStart
                percentLeft = 1 - (start / totalRecords)

                timeLeft = ((timeThusFar * percentLeft) / (percentComplete * .01))

                print(dt.datetime.now(),
                      "| Completed", percentComplete,
                      '% | time for company data subsection extraction:',
                      dt.timedelta(seconds=(dt.datetime.now() - tempDT).seconds),
                      "| Predicted Time left:", timeLeft,
                      "| Predicted Total Time for complete extraction:", timeThusFar + timeLeft,
                      )
                tempDT = dt.datetime.now()

    if verbose:
        print("Completed", 100, '%')
        print("TIME TO PULL STOCK COMPANY DATA", dt.timedelta(seconds=(dt.datetime.now() - tStart).seconds))
    basic.log_entry(logFile="project_log.txt", logText=(
        "TIME TO PULL STOCK COMPANY DATA ", str(dt.timedelta(seconds=(dt.datetime.now() - tStart).seconds))),
                    logMode='a')
    return
