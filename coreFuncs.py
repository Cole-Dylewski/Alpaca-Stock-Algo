#Library for central functions relied on by other libraries

import io
import time
import os

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


ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
