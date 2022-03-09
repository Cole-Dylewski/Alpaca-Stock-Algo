#Library for central functions relied on by other libraries

#standard libraries
import io
import time
import os
import pandas as pd
import tkinter.filedialog as fd

ROOT_DIR =''

def logEntry(logFile,logText='',logMode='w',gap=True):

    global ROOT_DIR
    logMode=logMode.lower()
    logFile = ROOT_DIR+r"/"+logFile

    if logMode=='w':
        logFile = open(logFile, "w")

    if logMode=='a':
        logFile = open(logFile, "a")

    if type(logText)==type(()):
        for i in logText:
            logFile.write(i)

    if type(logText)==type(''):
        logFile.write(logText)

    if(gap):logFile.write('\n')

    logFile.write('\n')
    logFile.close()
    return

def convertFileToDF(sourceFile, sourceDirectory='', good2go=True):
    if (sourceDirectory == ''):
        sourceDirectory = os.path.dirname(sourceFile)
    ###If the data is already in a traditional table format, set below value to true
    if (good2go):
        inputData = []
        name, ext = os.path.splitext(sourceFile)
        # print("Name = ", name)
        # print('EXT = ', ext)
        if (ext == '.csv'):
            # print('CSV')
            inputData = pd.read_csv(sourceFile, low_memory=False)

        if (ext == '.xlsx'):
            # print('XLSX')
            # inputData = pd.read_excel(sourceFile, dtype= str,low_memory=False)
            inputData = pd.read_excel(sourceFile, sheet_name=None)
        return inputData

        return df


def file_save(df, saveName=''):
    ###check if name is given when function is called, if no name then a prompt will be given
    if (saveName == ''):
        saveName = fd.asksaveasfilename(defaultextension='.csv',
                                        filetypes=(("Excel files", "*.xlsx"), ('Comma Seperated File', "*.csv")))
    # print(saveName)
    name, ext = os.path.splitext(saveName)
    if (ext == '.csv'):
        df.to_csv(saveName, index=False)
    if (ext == '.xlsx'):
        df.to_excel(saveName, index=False)
    print("File Saved: ", saveName)


def writeToCSV(position, data, tableName,raw=True):

    #print("Updating table")
    #print(keyType)
    #print(position)
    #print(tableName)
    #print(data)
    if(raw):
        if(position ==0):
            name, ext = os.path.splitext(tableName)
            fileName = name + '_RAW' + ext
            data.to_csv(fileName, mode='w', index=False)


        else:
            name, ext = os.path.splitext(tableName)
            fileName = name + '_RAW' + ext
            data.to_csv(fileName,header=False, mode='a',index = False)
        #print(name + '_RAW' + ext+" SAVED")
    else:
        if (position == 0):
            name, ext = os.path.splitext(tableName)
            fileName = name + ext
            data.to_csv(fileName, mode='w', index=False)

        else:
            name, ext = os.path.splitext(tableName)
            fileName = name+ ext
            data.to_csv(fileName, header=False, mode='a', index=False)

def convertDict2DF(items):
    return pd.DataFrame({k: [v] for k, v in items})

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
