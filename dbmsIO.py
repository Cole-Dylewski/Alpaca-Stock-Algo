#standard libraries
import math
import pandas as pd
import datetime as dt
import os
import json
import tkinter.filedialog as fd


def extractJson(fileName, defaultValue={}):
    jsonFileName = ROOT_DIR + r'/' + fileName

    if not os.path.exists(jsonFileName):
        with open(jsonFileName, "x") as json_file:
            json.dump(defaultValue, json_file)
            json_file.close()

    print("loading JSON", jsonFileName)
    with open(jsonFileName, "r") as json_file:
        jsonData = json.load(json_file)

    return jsonData

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

def writeToCSV(position, data, tableName,raw=True):

    #print("Updating table")
    #print(keyType)
    #print(position)
    #print(tableName)
    #print(data)
    if(raw):
        if(position == 0):
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

def loadJson(fileName,jsonData):

    jsonFileName = ROOT_DIR + r'/'+fileName

    if not os.path.exists(jsonFileName):
        with open(jsonFileName, "x") as json_file:
            json.dump(jsonData, json_file)
            json_file.close()
    else:
        print("Saving JSON Data", jsonFileName)
        with open(jsonFileName, "w") as json_file:
            json.dump(jsonData, json_file)
            json_file.close()

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

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))