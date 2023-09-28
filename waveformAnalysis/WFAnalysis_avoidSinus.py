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
fileName = '495nd39v25_9' # example: 'test1999'

filePath = zeroPath + 'results/' + fileName + '/'
fileExt = '.csv'
fileTag = 'Numbered'
processedFileExt = '.csv'
figurePath = filePath + 'figures/'

rValue = 50
nBins = 150
qScale = 10**9
chargeValuesToPlot = [0.14404254e-9, 0.30697786e-9, 0.47152013e-9, 0.60013079e-9]

# Optional figures(.png) saving
saveFigs = False
printResults = False

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

firstWF = 3
lastWF = 3
for num in range(firstWF - 1, lastWF):
    condition = WFData[colNames[2]] == num
    time = np.array(WFData.loc[condition, colNames[0]])
    voltage = np.array(WFData.loc[condition, colNames[1]])
    if sum(voltage < -0.1) != 0 or time.size == 0:
        continue
    # plt.figure()
    plt.plot(time, voltage, '-', label = 'WaveForm ' + str(num + 1))
    # plt.hlines(np.median(voltage[voltage < 0.01]), min(time), max(time), colors = 'red', linestyles = 'dashed', label = 'Baseline')
plt.xlabel('t / s')
plt.ylabel('V / V')
plt.legend()
if saveFigs:
    plt.savefig(figurePath + fileName + '_WF' + str(firstWF) + '-' + str(lastWF) + '.png', bbox_inches = 'tight')

# Plot 1 waveform of 1,2,3,4 photons
if False:
    firstWF = 1
    lastWF = 2000
    for auxChargeToPlot in chargeValuesToPlot:
        for num in range(firstWF - 1, lastWF):
            condition = WFData[colNames[2]] == num
            time = np.array(WFData.loc[condition, colNames[0]])
            voltage = np.array(WFData.loc[condition, colNames[3]])
            if sum(voltage < -0.1) != 0 or time.size == 0:
                continue
            intensity = voltage / rValue
            charge = simpson(intensity, time)
            if (charge > auxChargeToPlot * 0.99) and (charge < auxChargeToPlot * 1.01):
                plt.plot(time, voltage, '-')#, label = 'WaveForm ' + str(num + 1))
                break
    plt.xlabel('t / s')
    plt.ylabel('V / V')
    plt.legend(['1 photon', '2 photons', '3 photons', '4 photons'])
    if saveFigs:
        plt.savefig(figurePath + 'severalPhotons.png', bbox_inches = 'tight')

    if not 'V_BL/C' in WFData:
        WFData, colNames = doBaseLineCorrection(WFData, colNames, WFHeight, uniqueWFNumber, voltageThreshold,\
                                                filePath, fileName, fileTag, fileExt, saveCorrV = True)

    WFCharge = np.zeros(WFCount)
    for idx, num in enumerate(uniqueWFNumber):
        condition = WFData[colNames[2]] == num
        time = np.array(WFData.loc[condition, colNames[0]])
        voltage = np.array(WFData.loc[condition, colNames[3]])
        if sum(voltage < -0.1) != 0:
            continue
        intensity = voltage / rValue
        charge = simpson(intensity, time)
        if charge < 1.5e-9: # np.inf
            WFCharge[idx] = charge

    plt.figure()
    plt.hist(WFCharge, bins = nBins, label = 'Custom median corrected histogram')
    plt.xlabel('Q / C')
    plt.ylabel('Cumulative frequency')
    plt.legend()
    if saveFigs:
        plt.savefig(figurePath + fileName + 'Hist' + str(nBins) + '.png', bbox_inches = 'tight')

    QHistData = filePath + fileName + 'HistData' + str(nBins) + fileExt
    if not isfile(QHistData):
        FrecVsCharge = fillQHistBins(WFCharge, nBins, filePath, fileName)
    else:
        FrecVsCharge = ps.read_csv(QHistData, header = 0)

    gaussParams = doHistGaussianFit(FrecVsCharge, qScale, nBins, figurePath, fileName,\
                                    initSigma = 0.005, minPeakHeight = 0.05 * max(FrecVsCharge['F']), maxCenterVar = 10**-9 * qScale,\
                                    minCenterDist = 10, printResult = printResults, doPlot = True, saveFig = saveFigs)

    # LINEAR FIT OF CENTROIDS
    doCentroidsLinearFit(gaussParams, qScale, nBins, figurePath, fileName,\
                        ignoredLastPeaks = 2, printResult = printResults, doPlot = True, saveFig = saveFigs)

plt.show(block = True)