#standard libraries
import json
import os
import tkinter.filedialog as fd

def getSettings():

    settingsFileName = ROOT_DIR + r"/settings.json"
    print("settings file:", settingsFileName)
    with open(settingsFileName, "r") as settings_file:
        settings = json.load(settings_file)

    #print(settings)
    return settings

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