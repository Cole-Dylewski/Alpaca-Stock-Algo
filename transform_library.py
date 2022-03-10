#standard libraries
import pandas as pd
import datetime as dt

#non-standard libraries


#internal libraries
import extract_library
import dbmsIO



def batchBarSetToDF(barset,timeFrame,actionsDf,dfCounter,fileName):
    # print(barset)
    print('len(barset)', len(barset))
    barsetKeys = list(barset.keys())
    totalBarSize = 0

    for symbol in barsetKeys:

        if (len(barset[symbol]) > 0):
            barsetDf = objectToDF(barset[symbol])
            # barsetDf['T'] = pd.to_datetime(barsetDf['T'], unit='s')-dt.timedelta(hours=5)
            # barsetDf['T'] = barsetDf.apply(tzUpdate, axis=1)
            barsetDf['T'] = pd.to_datetime(barsetDf['T'], unit='s').dt.tz_localize('UTC').dt.tz_convert(
                pd.Timestamp(dt.datetime.now().astimezone()).tzinfo)
            barsetDf.insert(0, 'SYMBOL', symbol)
            barsetDf['SOURCE'] = 'IPX'
            barsetDf['TIMEFRAME'] = timeFrame
            barsetDf = barsetDf.rename(
                columns={'T': 'DATETIME', "O": "OPEN", 'H': 'HIGH', 'L': 'LOW', 'C': 'CLOSE', 'V': 'VOLUME'})
            barSize = barsetDf.memory_usage(deep=True).sum()
            totalBarSize = totalBarSize + barSize

            barsetDf = splitDivCorrection(df=barsetDf, actionsDf=actionsDf)
            #print(barsetDf.head(10).to_string())
            #print(barsetDf.tail(10).to_string())
            dbmsIO.writeToCSV(position=dfCounter, data=barsetDf, tableName=fileName)



def objectToDF(obj):
    if len(obj)>0:
        raw=str((list(obj[0].__dict__.keys())[0]))
        assetList = []
        assetHeader = list(obj[0].__dict__[raw].keys())
        for i in obj:
            assetList.append(list(i.__dict__[raw].values()))
        outputDF = pd.DataFrame(data=assetList, columns=assetHeader)
        outputDF.columns = [x.upper() for x in outputDF.columns]
        return outputDF

    else:
        return pd.DataFrame()

def splitDivCorrection(df,actionsDf):
    df['SPLIT CO-EFFICTIENT'] = 1
    #print(actionsDf)
    if len(actionsDf)>0:
        splits = actionsDf[['SYMBOL','DATETIME','SPLITS']]
        splits = splits[splits['SYMBOL']== df.iloc[0]['SYMBOL']]
        splits['DATETIME'] = pd.to_datetime(splits['DATETIME']).dt.tz_localize('UTC').dt.tz_convert(
                pd.Timestamp(dt.datetime.now().astimezone()).tzinfo)

        splits = splits.loc[splits['SPLITS'] != 0].reset_index(drop=True)

        splitsValue=1

        for i in range(len(splits)-1,-1,-1):
            if (splitsValue!=splits.iloc[i]['SPLITS']):
                splitsValue=splitsValue*splits.iloc[i]['SPLITS']
                #print(splitsValue)
            df.loc[df['DATETIME'] < splits.iloc[i]['DATETIME'], 'NEW SPLIT CO-EFFICTIENT'] = splits.iloc[i]['SPLITS']
            df.loc[df['DATETIME'] < splits.iloc[i]['DATETIME'], 'SPLIT CO-EFFICTIENT'] = splitsValue

        for i in df.columns.to_list():
            if i in ['OPEN','HIGH','LOW','CLOSE']:
                df[i] = df[i]/df['SPLIT CO-EFFICTIENT']

        df=df.drop('SPLIT CO-EFFICTIENT',axis=1)
        return df
    else:
        return df