# standard libraries
import json
import os
import tkinter.filedialog as fd


def get_settings():
    settingsFileName = ROOT_DIR + r"/settings.json"
    print("settings file:", settingsFileName)
    with open(settingsFileName, "r") as settings_file:
        settings = json.load(settings_file)

    # print(settings)
    return settings


ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
