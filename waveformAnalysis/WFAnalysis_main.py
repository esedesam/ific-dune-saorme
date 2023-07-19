# WFAnalysis.py

# Main script for usual waveforms analysis
#
# Author: Samuel Ortega
# Last Rev.: 13/06/2023

import pandas as ps
import matplotlib.pyplot as plt
import numpy as np
from os.path import isfile
from scipy.optimize import curve_fit
from timeit import default_timer as timer
from matplotlib.ticker import MaxNLocator
from WFAnalysis_repo import *

# INIT TIMER
timerStart = timer()

# SET-UP
zeroPath = 'D:/ific-dune-saorme/waveformAnalysis/' # Change to user repo path
fileName = 'dune_darkn' # example: 'test1999'

filePath = zeroPath + 'results/' + fileName + '/'
fileExt = '.csv'
fileTag = 'Numbered'
processedFileExt = '.csv'
figurePath = filePath + 'figures/'

# Optional figures(.png) and results(.txt) saving
saveFigs = True
printResults = True

voltageThreshold = 0.01 # 10 mV
nBins = 300
qScale = 10**9

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
colNames = WFData.columns # 'TIME' | 'MATH1' | 'WFNumber' | 'V_BL/C'

# INDIVIDUAL PEAK DETECTION AND COUNT (OPTIONAL: FIT AND PLOT)
doPeakDet = False
if doPeakDet:
    WFPeakCount = peakDetection(WFData, voltageThreshold, figurePath, fileName)

# BASELINE CORRECTION
if not 'V_BL/C' in WFData:
    WFData, colNames = doBaseLineCorrection(WFData, colNames, WFHeight, uniqueWFNumber, voltageThreshold,\
                                            filePath, fileName, fileTag, fileExt, saveCorrV = True)

# Q HISTOGRAM
WFCharge = getChargeAndHist(WFData, colNames, WFCount, uniqueWFNumber, nBins,\
                            figurePath, fileName, doHist = True, saveFig = saveFigs)

# Q HISTOGRAM GAUSSIAN FIT
QHistData = filePath + fileName + 'HistData' + str(nBins) + fileExt
if not isfile(QHistData):
    FrecVsCharge = fillQHistBins(WFCharge, nBins, filePath, fileName)
else:
    FrecVsCharge = ps.read_csv(QHistData, header = 0)

gaussParams = doHistGaussianFit(FrecVsCharge, qScale, nBins, figurePath, fileName,\
                                minPeakHeight = 0.02 * max(FrecVsCharge['F']), maxCenterVar = 10**-9 * qScale,\
                                minCenterDist = 20, printResult = printResults, doPlot = True, saveFig = saveFigs)

# LINEAR FIT OF CENTROIDS
doCentroidsLinearFit(gaussParams, qScale, nBins, figurePath, fileName,\
                     printResult = printResults, doPlot = True, saveFig = saveFigs)

#####################################################################

# POISSONIAN FIT OF AREAS
# numFittedPeaks = int(len(gaussParams) / 3)
# auxNums = np.zeros(numFittedPeaks)
# auxAreas = np.zeros(numFittedPeaks)
# for idx in range(numFittedPeaks):
#     auxNums[idx] = idx + 1
#     auxAreas[idx] = gaussParams['g' + str(idx + 1) + '_amplitude']

# auxAreas = auxAreas / sum(auxAreas)

# poissParam, poissCov = curve_fit(poisson1, auxNums, auxAreas)
# print('Poissonian fit: lamb = ' + str(poissParam[0]) + ' ± ' + str(poissCov[0,0]))
# fitAreas = poisson1(auxNums, poissParam)
# ax = plt.figure().gca()
# plt.plot(auxNums, auxAreas, '.', label = 'Data')
# plt.plot(auxNums, fitAreas, '-', label = 'Poissonian fit')
# plt.xlabel('# photons')
# ax.xaxis.set_major_locator(MaxNLocator(integer = True))
# plt.ylabel('Probability')
# plt.legend()

# END AND PRINT TIMER
timerEnd = timer()
print('Elapsed time: ' + str(timerEnd - timerStart) + ' s')

# SHOW FIGURES
plt.show(block = True)