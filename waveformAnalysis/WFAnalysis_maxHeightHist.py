# WFVisualization.py

# Plots several waveforms of a set
#
# Author: Samuel Ortega
# Last Rev.: 13/06/2023

import pandas as ps
import matplotlib.pyplot as plt
import numpy as np
from os.path import isfile
from WFAnalysis_repo import *

# SET-UP
zeroPath = 'D:/ific-dune-saorme/waveformAnalysis/' # Change to user repo path
fileName = 'ch2_27_06_180v' # example: 'test1999'

filePath = zeroPath + 'results/' + fileName + '/'
fileExt = '.wfm'
fileTag = 'Numbered'
processedFileExt = '.csv'
figurePath = filePath + 'figures/'

# Optional figures(.png) saving
saveFigs = False

voltageThreshold = 0.01 # 10 mV

#####################################################################

# LOAD WAVEFORMS DATAFRAME
preprocessedName = filePath + fileName + fileTag + processedFileExt
if not isfile(preprocessedName):
    WFData = preprocessWFData(zeroPath, fileName, fileExt, fileTag)
else:
    WFData = ps.read_csv(preprocessedName, header = 0)

WFHeight = len(WFData.index)
uniqueWFNumber = set(WFData['WFNumber'])
WFCount = len(uniqueWFNumber)

colNames = WFData.columns

# WF MAXIMUM HISTOGRAM
maxArray = []
for num in range(WFCount):
    condition = WFData[colNames[2]] == num
    # time = np.array(WFData.loc[condition, colNames[0]])
    voltage = np.array(WFData.loc[condition, colNames[1]])
    maxArray.append(max(voltage))
plt.hist(maxArray, bins = 100)
plt.xlabel('Vmax / V')
plt.ylabel('Cumulative frecuency')
# plt.legend()
if saveFigs:
    plt.savefig(figurePath + fileName + '_WFMaxsHist.png', bbox_inches = 'tight')
plt.show(block = True)
