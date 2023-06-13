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
fileName = 'sam_34v_3k_drknoise' # example: 'test1999'

filePath = zeroPath + 'results/' + fileName + '/'
fileExt = '.csv'
fileTag = 'Numbered'
figurePath = filePath + 'figures/'

# Optional figures(.png) saving
saveFigs = False

voltageThreshold = 0.01 # 10 mV

#####################################################################

# LOAD WAVEFORMS DATAFRAME
preprocessedName = filePath + fileName + fileTag + fileExt
if not isfile(preprocessedName):
    WFData = preprocessWFData(zeroPath, fileName, fileExt, fileTag)
else:
    WFData = ps.read_csv(preprocessedName, header = 0)

WFHeight = len(WFData.index)
uniqueWFNumber = set(WFData['WFNumber'])
WFCount = len(uniqueWFNumber)

colNames = WFData.columns

# WF GROUPED PLOT
firstWF = 1
lastWF = 10
for num in range(firstWF - 1, lastWF):
    condition = WFData[colNames[2]] == num
    time = np.array(WFData.loc[condition, colNames[0]])
    voltage = np.array(WFData.loc[condition, colNames[1]])
    # plt.figure()
    plt.plot(time, voltage, label = 'WaveForm ' + str(num + 1))
    plt.xlabel('t / s')
    plt.ylabel('V / V')
    plt.legend()
    if saveFigs:
        plt.savefig(figurePath + fileName + '_WF' + str(firstWF) + '-' + str(lastWF) + '.png', bbox_inches = 'tight')
plt.show(block = True)
