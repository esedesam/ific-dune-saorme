# WFGainAtRT.py

# - Analysis of waveforms with several peaks each.
# - Gain estimation from single PE and charge histogram.
# - Study of the effect of baseline calculation in the gain value.
#
# If too many peaks are detected in the histogram, change the
# inputs of doHistGaussianFit function.
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
fileName = 'sam_34v_0vledtrigg' # example: '3k_sigtrig'

filePath = zeroPath + 'results/' + fileName + '/'
fileExt = '.csv'
fileTag = 'Numbered'
figurePath = filePath + 'figures/'

# Optional figures(.png) and results(.txt) saving
saveFigs = True
printResults = False

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
indFigs = False # True -> Plot several WF | False -> Obtain gain
WFCharge = np.empty(0)
baselines = np.empty(0)
qIdx = 0
if indFigs:
    firstWF = 1
    lastWF = 10
    forRange = range(firstWF - 1, lastWF)
else:
    forRange = range(WFCount)
for num in forRange:
    condition = WFData[colNames[2]] == num
    time = np.array(WFData.loc[condition, colNames[0]])
    voltage = np.array(WFData.loc[condition, colNames[1]])
    # Baseline and thresholds
    customTh = min(voltage) + 0.5 * voltageThreshold
    blMedian = np.median(voltage[voltage < customTh])
    # blMedian = np.median(voltage[time < 0])
    baselines = np.append(baselines, blMedian)
    voltageBl = voltage - blMedian
    # Peak detection
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
    # Find peaks extension and do individual integration
    nextPeaks = 0
    for peakIdx in range(len(peaks)):
        if nextPeaks > 0:
            nextPeaks = nextPeaks - 1
            continue # Go over peaks that were together

        # Start at peak position and find the closest intersections with baseline at both sides
        idx = peaks[peakIdx]
        while (idx > 0) and (voltageBl[idx] > 0):
            idx = idx - 1
        minLim = idx
        idx = peaks[peakIdx]
        while (idx < len(voltageBl)) and (voltageBl[idx] > 0):
            idx = idx + 1
        maxLim = idx
        # Check if 2 or more peaks are in between two baselines intersections and separate them
        prevPeakIdx = peakIdx
        sepIdxArray = minLim
        for peakJdx in [peakKdx for peakKdx in range(peakIdx + 1, len(peaks))\
                          if minLim < peaks[peakKdx] and peaks[peakKdx] < maxLim]:
            sep = np.inf
            # Find minimum between two peaks as its separation
            for jdx in range(peaks[prevPeakIdx], peaks[peakJdx]):
                if voltageBl[jdx] < sep:
                    sep = min(sep, voltageBl[jdx])
                    sepIdx = jdx
            sepIdxArray = np.append(sepIdxArray, sepIdx)
            prevPeakIdx = peakJdx
            nextPeaks = nextPeaks + 1
        sepIdxArray = np.append(sepIdxArray, maxLim)
        # Integrate each peak extension
        for sepIdxIdx in range(len(sepIdxArray) - 1):
            intMinLim = sepIdxArray[sepIdxIdx]
            intMaxLim = sepIdxArray[sepIdxIdx + 1]
            peakTime = time[intMinLim:intMaxLim]
            peakVolt = voltageBl[intMinLim:intMaxLim]
            if indFigs:
                plt.plot(peakTime, peakVolt, '-', label = 'Peak %d' % qIdx)
            try:
                WFChargeAux = simpson(peakVolt, peakTime)
            except:
                disp('Error integrating peak no. %d in wf no. %d.' % (qIdx, num))
            else:
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
    baselineMedian = 10**3 * np.median(baselines)
    baselineStd = 10**3 * np.std(baselines)
    disp('baseline / mV = %0.4f +- %0.4f' % (baselineMedian, baselineStd))
    nBins = int(len(WFCharge)/10)
    plt.figure()
    plt.hist(WFCharge, bins = nBins, label = 'RT baseline\'d histogram')
    plt.xlabel('Q / C')
    plt.ylabel('Cumulative frequency')
    plt.legend()
    if saveFigs:
        plt.savefig(figurePath + fileName + 'Hist' + str(nBins) + '.png', bbox_inches = 'tight')
    # Fill histogram with charge data (or load it if done previously)
    QHistData = filePath + fileName + 'HistData' + str(nBins) + fileExt
    if not isfile(QHistData):
        FrecVsCharge = fillQHistBins(WFCharge, nBins, filePath, fileName, saveData = False)
    else:
        FrecVsCharge = ps.read_csv(QHistData, header = 0)
    
    # Gaussian fit (scaling needed)
    qScale = 10**9
    gaussParams = doHistGaussianFit(FrecVsCharge, qScale, nBins, figurePath, fileName,\
                                    minPeakHeight = 0.2 * max(FrecVsCharge['F']), maxCenterVar = 10**-9 * qScale,\
                                    minCenterDist = 40, printResult = printResults, doPlot = True, saveFig = saveFigs)
    
    # LINEAR FIT OF CENTROIDS
    doCentroidsLinearFit(gaussParams, qScale, nBins, figurePath, fileName,\
                         printResult = printResults, doPlot = True, saveFig = saveFigs)
    plt.figure()
    plt.hist(baselines, bins = int(len(baselines) / 20), label = 'Baseline values')
    plt.xlabel('Baseline / V')
    plt.ylabel('Cumulative frecuency')
    plt.legend()
    if True:
        plt.savefig(figurePath + fileName + 'BaselinesHist.png', bbox_inches = 'tight')

# END AND PRINT TIMER
timerEnd = timer()
print('Elapsed time: ' + str(timerEnd - timerStart) + ' s')

# SHOW FIGURES
plt.show(block = True)