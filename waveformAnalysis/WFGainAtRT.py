# WFGainAtRT.py

# Analysis of waveforms with several peaks
# Study of optimal baseline value
#
# Author: Samuel Ortega
# Last Rev.: 13/06/2023

import pandas as ps
import matplotlib
matplotlib.use("TkAgg")
from pylab import *
import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import find_peaks
from scipy.integrate import simpson
from os.path import isfile
from timeit import default_timer as timer
from WFAnalysis_repo import *

# INIT TIMER
timerStart = timer()

# SET-UP
zeroPath = 'D:/ific-dune-saorme/waveformAnalysis/' # Change to user repo path
fileName = 'sam_34v_3k_135v' # example: '3k_sigtrig'

filePath = zeroPath + 'results/' + fileName + '/'
fileExt = '.csv'
fileTag = 'Numbered'
figurePath = filePath + 'figures/'

# Optional figures(.png) and results(.txt) saving
saveFigs = True
printResults = True

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

# WF + BASELINES PLOT
indFigs = False
firstWF = 1
lastWF = 10
WFCharge = np.empty(0)
baselines = np.empty(0)
qIdx = 0
if indFigs:
    forRange = range(firstWF - 1, lastWF)
else:
    forRange = range(WFCount)
for num in forRange:
    condition = WFData[colNames[2]] == num
    time = np.array(WFData.loc[condition, colNames[0]])
    voltage = np.array(WFData.loc[condition, colNames[1]])
    customTh = min(voltage) + 0.5 * voltageThreshold
    blMedian = np.median(voltage[voltage < customTh])
    baselines = np.append(baselines, blMedian)
    voltageBl = voltage - blMedian
    peaks, _ = find_peaks(voltage, height = customTh, prominence = voltageThreshold)
    if indFigs:
        plt.figure()
        plt.plot(time, voltage, '-', label = 'Waveform ' + str(num + 1))
        plt.hlines(y = blMedian, xmin = time[0], xmax = time[-1],\
                linestyles = 'dashed', colors = 'r', label = 'Median (points under %.3f V)' % customTh)
        plt.plot(time[peaks], voltage[peaks], 'x', label = 'Detected peaks: %d' % len(peaks))
        plt.xlabel('t / s')
        plt.ylabel('V / V')
        plt.legend()
        if saveFigs:
            plt.savefig(figurePath + 'WF' + str(num) + '.png', bbox_inches = 'tight')
        thismanager = get_current_fig_manager()
        thismanager.window.wm_geometry("+0+100")
        plt.figure()
        plt.plot(time, voltageBl, '-', label = 'Waveform %d - BL ' % (num + 1))
    nextPeaks = 0
    for peakIdx in range(len(peaks)):
        if nextPeaks > 0:
            nextPeaks = nextPeaks - 1
            continue

        idx = peaks[peakIdx]
        while (idx > 0) and (voltageBl[idx] > 0):
            idx = idx - 1
        minLim = idx
        idx = peaks[peakIdx]
        while (idx < len(voltageBl)) and (voltageBl[idx] > 0):
            idx = idx + 1
        maxLim = idx
        peakTime = time[minLim:maxLim]
        peakVolt = voltageBl[minLim:maxLim]

        prevPeakIdx = peakIdx
        sepIdxArray = minLim
        for peakJdx in [peakKdx for peakKdx in range(peakIdx + 1, len(peaks))\
                          if minLim < peaks[peakKdx] and peaks[peakKdx] < maxLim]:
            sep = np.inf
            for jdx in range(peaks[prevPeakIdx], peaks[peakJdx]):
                if voltageBl[jdx] < sep:
                    sep = min(sep, voltageBl[jdx])
                    sepIdx = jdx
            sepIdxArray = np.append(sepIdxArray, sepIdx)
            prevPeakIdx = peakJdx
            nextPeaks = nextPeaks + 1
        sepIdxArray = np.append(sepIdxArray, maxLim)
        for sepIdxIdx in range(len(sepIdxArray) - 1):
            intMinLim = sepIdxArray[sepIdxIdx]
            intMaxLim = sepIdxArray[sepIdxIdx + 1]
            peakTime = time[intMinLim:intMaxLim]
            peakVolt = voltageBl[intMinLim:intMaxLim]
            if indFigs:
                plt.plot(peakTime, peakVolt, '-', label = 'Peak %d' % qIdx)
            WFChargeAux = simpson(peakVolt, peakTime)
            if WFChargeAux < np.inf:
                WFCharge = np.append(WFCharge, WFChargeAux)
            qIdx = qIdx + 1
        if indFigs:
            plt.xlabel('t / s')
            plt.ylabel('V / V')
            plt.legend()
            if saveFigs:
                plt.savefig(figurePath + 'WF' + str(num) + 'Peaks.png', bbox_inches = 'tight')
            thismanager = get_current_fig_manager()
            thismanager.window.wm_geometry("+950+100")
    if indFigs:
        plt.show(block = True)

if not indFigs:
    nBins = int(len(WFCharge)/10)
    plt.figure()
    plt.hist(WFCharge, bins = nBins, label = 'RT baseline\'d histogram')
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
    
    qScale = 10**9
    gaussParams = doHistGaussianFit(FrecVsCharge, qScale, nBins, figurePath, fileName,\
                                    minPeakHeight = 0.12 * max(FrecVsCharge['F']), maxCenterVar = 10**-9 * qScale,\
                                    minCenterDist = 20, printResult = printResults, doPlot = True, saveFig = saveFigs)
    
    # LINEAR FIT OF CENTROIDS
    doCentroidsLinearFit(gaussParams, qScale, nBins, figurePath, fileName,\
                         printResult = printResults, doPlot = True, saveFig = saveFigs)
    plt.figure()
    plt.hist(baselines, bins = int(len(baselines) / 20), label = 'Baseline values')
    plt.xlabel('Baseline / V')
    plt.ylabel('Cumulative frecuency')
    plt.legend()
    if saveFigs:
        plt.savefig(figurePath + fileName + 'BaselinesHist.png', bbox_inches = 'tight')

# END AND PRINT TIMER
timerEnd = timer()
print('Elapsed time: ' + str(timerEnd - timerStart) + ' s')

# SHOW FIGURES
plt.show(block = True)