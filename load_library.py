#standard libraries
import json
import os


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



ROOT_DIR = os.path.dirname(os.path.abspath(__file__))