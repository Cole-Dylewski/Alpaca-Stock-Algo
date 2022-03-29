# standard libraries
import pandas as pd
import datetime as dt
import numpy as np

# non-standard libraries


# internal libraries
import extract_library
import dbmsIO
import core_library


def batch_barset_to_df(barset, timeFrame, actionsDf, dfCounter, fileName):
    # print(barset)
    # print('len(barset)', len(barset))
    # print(fileName)
    barsetKeys = list(barset.keys())
    # print(barsetKeys)
    totalBarSize = 0
    # print (dfCounter)
    for symbol in barsetKeys:

        if (len(barset[symbol]) > 0):
            barsetDf = pd.DataFrame.from_dict(barset[symbol])
            barsetDf.columns = [x.upper() for x in barsetDf.columns.to_list()]

            barsetDf['T'] = pd.to_datetime(barsetDf['T'])
            barsetDf.insert(0, 'SYMBOL', symbol)
            barsetDf['SOURCE'] = 'IPX'
            barsetDf['TIMEFRAME'] = timeFrame
            barsetDf = barsetDf.rename(
                columns={'T': 'DATETIME', "O": "OPEN", 'H': 'HIGH', 'L': 'LOW', 'C': 'CLOSE', 'V': 'VOLUME'})
            barSize = barsetDf.memory_usage(deep=True).sum()
            totalBarSize = totalBarSize + barSize
            # print(barsetDf)
            barsetDf = split_div_correction(df=barsetDf, actionsDf=actionsDf)

            # print(barsetDf.head(10).to_string())
            # print(barsetDf.tail(10).to_string())

            dbmsIO.to_csv(position=dfCounter, data=barsetDf, tableName=fileName)
            dfCounter = dfCounter + 1
    return totalBarSize, dfCounter


def object_to_df(obj):
    if len(obj) > 0:
        raw = str((list(obj[0].__dict__.keys())[0]))
        assetList = []
        assetHeader = list(obj[0].__dict__[raw].keys())
        for i in obj:
            assetList.append(list(i.__dict__[raw].values()))
        outputDF = pd.DataFrame(data=assetList, columns=assetHeader)
        outputDF.columns = [x.upper() for x in outputDF.columns]
        return outputDF

    else:
        return pd.DataFrame()


def split_div_correction(df, actionsDf):
    df['SPLIT CO-EFFICTIENT'] = 1
    # print(actionsDf)
    if len(actionsDf) > 0:
        splits = actionsDf[['SYMBOL', 'DATETIME', 'SPLITS']]
        splits = splits[splits['SYMBOL'] == df.iloc[0]['SYMBOL']]
        splits['DATETIME'] = pd.to_datetime(splits['DATETIME']).dt.tz_localize('UTC').dt.tz_convert(
            pd.Timestamp(dt.datetime.now().astimezone()).tzinfo)

        splits = splits.loc[splits['SPLITS'] != 0].reset_index(drop=True)

        splitsValue = 1
        # print('SPLITS:',splits)
        for i in range(len(splits) - 1, -1, -1):
            if (splitsValue != splits.iloc[i]['SPLITS']):
                splitsValue = splitsValue * splits.iloc[i]['SPLITS']
                # print(splitsValue)
            df.loc[df['DATETIME'] < splits.iloc[i]['DATETIME'], 'NEW SPLIT CO-EFFICTIENT'] = splits.iloc[i]['SPLITS']
            df.loc[df['DATETIME'] < splits.iloc[i]['DATETIME'], 'SPLIT CO-EFFICTIENT'] = splitsValue

        for i in df.columns.to_list():
            if i in ['OPEN', 'HIGH', 'LOW', 'CLOSE']:
                df[i] = df[i] / df['SPLIT CO-EFFICTIENT']

        df = df.drop('SPLIT CO-EFFICTIENT', axis=1)
        # print(df.head(5).to_string())
        if 'NEW SPLIT CO-EFFICTIENT' in df.columns.to_list():
            df = df.drop('NEW SPLIT CO-EFFICTIENT', axis=1)

        return df

    else:
        return df


def get_slope(subDF, subset):
    # print('calculating Slope')
    # print(subDF,subset)
    slope = 0
    slopeDf = pd.DataFrame()
    slopeDf['Y'] = subDF[subset]
    slopeDf['X'] = pd.Series(slopeDf.index.to_list()) + 1
    slopeDf['XY'] = slopeDf['X'] * slopeDf['Y']
    slopeDf['XX'] = slopeDf['X'] * slopeDf['X']
    slopeDf['YY'] = slopeDf['Y'] * slopeDf['Y']
    # print(slopeDf)
    n = len(slopeDf)
    sumXY = slopeDf['XY'].sum()
    sumXX = slopeDf['XX'].sum()
    sumX = slopeDf['X'].sum()
    sumY = slopeDf['Y'].sum()
    top = ((n * sumXY) - (sumX * sumY))
    bottom = ((n * sumXX) - (sumX * sumX))
    # print(n,sumY,sumX,sumXY)
    # print("top",top,"bottom",bottom)
    # print('SLOPE CHECK')
    # print(slope)
    # print(top/bottom)
    # slope = top/bottom
    if bottom == 0:
        slope = 0
    else:
        slope = top / bottom
    # print(slope)
    return slope


def df_stat_calcs(subDF, verbose=True):
    global counter
    global increment
    global setPoint
    global tStart
    global tempDt

    subDF = subDF.reset_index(drop=True)
    tempDF = {}
    tempDF['SYMBOL'] = subDF.iloc[0]['SYMBOL']
    if (len(subDF) != 0):
        tempDF['START TIMESTAMP'] = subDF.iloc[0]['DATETIME']
        tempDF['END TIMESTAMP'] = subDF.iloc[-1]['DATETIME']

        tempDF['START PRICE'] = subDF.iloc[0]['OPEN']
        tempDF['END PRICE'] = subDF.iloc[-1]['CLOSE']
        tempDF['GAIN'] = subDF.iloc[-1]['CLOSE'] - subDF.iloc[0]['OPEN']
        if subDF.iloc[0]['OPEN'] == 0:
            tempDF['% GAIN'] = 0
        else:
            tempDF['% GAIN'] = ((subDF.iloc[-1]['CLOSE'] - subDF.iloc[0]['OPEN']) / subDF.iloc[0]['OPEN']) * 100

    tempDF['AVG OPEN'] = subDF['OPEN'].mean()
    tempDF['AVG LOW'] = subDF['LOW'].mean()
    tempDF['AVG HIGH'] = subDF['HIGH'].mean()
    tempDF['AVG CLOSE'] = subDF['CLOSE'].mean()
    tempDF['MIN'] = subDF['LOW'].min()
    tempDF['25%'] = np.percentile(subDF['CLOSE'], 25)
    tempDF['MEDIAN'] = subDF['CLOSE'].median()
    tempDF['75%'] = np.percentile(subDF['CLOSE'], 75)
    tempDF['MAX'] = subDF['HIGH'].max()

    if (len(subDF) != 0):
        # slope, intercept, r_value, p_value, std_err = stats.linregress(subDF.index, subDF['CLOSE'])

        tempDF['SLOPE'] = get_slope(subDF, 'CLOSE')

        tempDF['% SLOPE'] = get_slope(subDF, 'CLOSE') / (subDF['CLOSE']).mean() * 100

        tempDF['VOLUME TREND'] = get_slope(subDF, 'VOLUME')
        # tempDF['% Volume Trend'] = getSlope(subDF, 'VOLUME')/ (subDF['VOLUME']).mean() * 100

        dy = subDF['CLOSE'] - subDF['OPEN']
        tempDF['AVG INTERVAL SLOPE'] = dy.mean()

    tempDF['STD DEV'] = subDF['CLOSE'].std()
    tempDF['% STD DEV'] = (subDF['CLOSE'].std()) / subDF['CLOSE'].mean()
    tempDF['AVG RANGE'] = (subDF['HIGH'] - subDF['LOW']).mean()
    tempDF['% AVG RANGE'] = ((subDF['HIGH'] - subDF['LOW']) / (subDF['HIGH'] - subDF['LOW']).mean() * 100).mean()
    tempDF['AVG PRICE'] = ((subDF['CLOSE'] + subDF['OPEN'] + subDF['HIGH'] + subDF['LOW']) / 4).mean()

    if (len(subDF) != 0):
        # print(subDF.iloc[0]['CLOSE'],subDF.iloc[-1]['CLOSE'],(subDF.iloc[0]['CLOSE'] - subDF.iloc[-1]['CLOSE']),((subDF.iloc[-1]['CLOSE']-subDF.iloc[0]['CLOSE'])/subDF.iloc[0]['CLOSE'])*100)

        tempDF['TIME DELTA'] = (subDF.iloc[-1]['DATETIME'] - subDF.iloc[0]['DATETIME'])
        # tempDF['FIDELITY'] = round(((len(subDF) / recordLen) * 100), 2)
        tempDF['DATA POINTS'] = len(subDF)
        tempDF['TIMEFRAME'] = subDF.iloc[0]['TIMEFRAME']
        # tempDF['INTERVAL'] = subDF['INTERVAL']

    tempDF['AVG VOLUME'] = subDF['VOLUME'].mean()
    counter = counter + 1
    if (verbose):
        percentComplete = counter / len(tckrs)
        if percentComplete * 100 > setPoint:
            timeThusFar = dt.datetime.now() - tStart
            percentLeft = 1 - percentComplete
            timeLeft = ((timeThusFar * percentLeft) / (percentComplete))
            print(dt.datetime.now(),
                  "| Completed", round(percentComplete * 100, 2), "% Stat Transformation completed. Time for Calc:",
                  dt.timedelta(seconds=(dt.datetime.now() - tempDt).seconds),
                  "| Predicted Time left:", timeLeft,
                  "| Predicted Total Time for complete calculation:", timeThusFar + timeLeft)

            # print(round(percentComplete,2),"% Stat Transformation completed. Time for Calc:",dt.timedelta(seconds=(dt.datetime.now() - tempTimer).seconds),"| Predicted Time left:",(100-percentDone)*dt.timedelta(seconds=(dt.datetime.now() - tempTimer).seconds))
            tempDt = dt.datetime.now()
            setPoint = setPoint + increment
    return pd.Series(tempDF, index=tempDF.keys())


def m_data_to_stats(df, fileName, verbose=True):
    global counter
    global increment
    global setPoint
    global tStart
    global tempDt
    global tckrs

    print("Converting Raw", fileName, "to Stats")
    tckrs = df['SYMBOL'].unique()

    counter = 0
    increment = 10
    setPoint = increment
    tStart = dt.datetime.now()
    tempDt = dt.datetime.now()
    outputDf = df.groupby('SYMBOL').apply(df_stat_calcs, verbose=verbose)

    for col in ['SLOPE', '% SLOPE', 'STD DEV', '% STD DEV']:
        outputDf[col] = outputDf[col].fillna(0)

    for col in ['% GAIN', '% AVG RANGE', '% SLOPE', '% STD DEV', 'AVG VOLUME']:
        percentile = col + " PERCENTILE"
        outputDf[percentile] = round(outputDf[col].rank(pct=True) * 100, 2)
    outputDf['ABSOLUTE SLOPE PERCENTILE'] = round(outputDf['% SLOPE'].abs().rank(pct=True, ascending=True) * 100, 2)
    outputDf['FIDELITY'] = round(((outputDf['DATA POINTS'] / outputDf['DATA POINTS'].max()) * 100), 0)

    if (len(outputDf) > 1):
        outputDf = outputDf.dropna(how='any').reset_index(drop=True)
    else:
        outputDf = outputDf.reset_index(drop=True)
    print('Data Processing Success rate:', len(outputDf) / len(tckrs) * 100, '% (', len(outputDf), '/', len(tckrs), ')')
    print("Total time to run calculations:", dt.datetime.now() - tStart)
    core_library.log_entry(logFile="project_log.txt",
                           logText=("Total time to run calculations: ", str(dt.datetime.now() - tStart)), logMode='a',
                           gap=False)
    # print("input memory usage:", round(df.memory_usage(deep=True).sum() / 1000000, 2), 'MB')
    # print("output memory usage:", round(outputDf.memory_usage(deep=True).sum() / 1000000, 2), 'MB')
    # print(outputDf.to_string())
    return outputDf
