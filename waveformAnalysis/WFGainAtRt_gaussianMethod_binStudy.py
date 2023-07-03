# WFGainAtRtGaussianMethod.py

# Analysis of waveforms with several peaks
# Gets the gain as a relation of gaussian params
#
# Author: Samuel Ortega
# Last Rev.: 13/06/2023

import lmfit
import pandas as ps
import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import find_peaks
from os.path import isfile
from timeit import default_timer as timer
from lmfit.models import GaussianModel, LinearModel, QuadraticModel
from WFAnalysis_repo import *

# INIT TIMER
timerStart = timer()

# SET-UP
zeroPath = 'D:/ific-dune-saorme/waveformAnalysis/' # Change to user repo path
# groupName = 'g_rt'
# fileNameList = ['3k_ch0_380_rt', '3k_ch0_393_rt', '3k_ch0_400_rt', '3k_ch0_410_rt']
# voltList = [3.80, 3.93, 4.00, 4.10]
# groupName = 'g_rt_sam'
# fileNameList = ['sam_34v_3k_131v', 'sam_34v_3k_135v', 'sam_34v_3k_140v', 'sam_34v_3k_145v', 'sam_34v_3k_150v',\
#                 'sam_34v_3k_155v', 'sam_34v_3k_160v', 'sam_34v_3k_165v', 'sam_34v_3k_170v', 'sam_34v_3k_180v',\
#                 'sam_34v_3k_185v', 'sam_34v_3k_200v', 'sam_34v_3k_210v', 'sam_34v_3k_220v', 'sam_34v_3k_250v']
# voltList = [1.31, 1.35, 1.40, 1.45, 1.50, 1.55, 1.60, 1.65, 1.70, 1.80, 1.85, 2.00, 2.10, 2.20, 2.50]
# groupName = 'g_rt_20230621_ind'
# fileNameList = ['20230621_34v_3k_131v', '20230621_34v_3k_140v', '20230621_34v_3k_150v',\
#                 '20230621_34v_3k_160v', '20230621_34v_3k_170v', '20230621_34v_3k_180v',\
#                 '20230621_34v_3k_200v', '20230621_34v_3k_210v', '20230621_34v_3k_220v']
# voltList = [1.31, 1.40, 1.50, 1.60, 1.70, 1.80, 2.00, 2.10, 2.20]
# groupName = 'g_rt_mas'
# fileNameList = ['mas_34v_3k_131v', 'mas_34v_3k_140v', 'mas_34v_3k_150v',\
#                 'mas_34v_3k_160v', 'mas_34v_3k_170v', 'mas_34v_3k_180v',\
#                 'mas_34v_3k_190v', 'mas_34v_3k_200v', 'mas_34v_3k_210v']
# voltList = [1.31, 1.40, 1.50, 1.60, 1.70, 1.80, 1.90, 2.00, 2.10]
groupName = 'g_rt_samch2_ind'
fileNameList = ['ch2_27_06_180v']
voltList = [1.80]

filePath = zeroPath + 'results/' + groupName + '/'
fileExt = '.csv'
fileTag = 'Numbered'
processedFileExt = '.csv'
figurePath = filePath + 'figures/'

if not isdir(filePath):
    mkdir(filePath)
if not isdir(figurePath):
    mkdir(figurePath)

# Optional figures(.png) and results(.txt) saving
saveFigs = True
printResults = True

voltageThreshold = 0.01
nBins = 50
qScale = 10**9

#####################################################################

# GET DATA, PROCESS AND HISTOGRAM
centroidList = np.zeros(len(fileNameList))
centroidListError = np.zeros(len(fileNameList))
sigmaListError = np.zeros(len(fileNameList))
sigmaList = np.zeros(len(fileNameList))
for idx, fileName in enumerate(fileNameList):
    # Preprocessing
    dataPath = zeroPath + 'results/' + fileName + '/'
    preprocessedName = dataPath + fileName + fileTag + processedFileExt
    if not isfile(preprocessedName):
        WFData = preprocessWFData(zeroPath, fileName, fileExt, fileTag)
    else:
        WFData = ps.read_csv(preprocessedName, header = 0)
    WFHeight = len(WFData.index)
    uniqueWFNumber = set(WFData['WFNumber'])
    WFCount = len(uniqueWFNumber)
    colNames = WFData.columns
    # Baseline correction
    if not 'V_BL/C' in WFData:
        WFData, colNames = doBaseLineCorrectionV2(WFData, colNames, WFHeight, uniqueWFNumber, voltageThreshold,\
                                                  dataPath, fileName, fileTag, fileExt, saveCorrV = False)
    # Calculate charge
    WFCharge = getChargeAndHist(WFData, colNames, WFCount, uniqueWFNumber, nBins,\
                                figurePath, fileName, doHist = True, saveFig = saveFigs)
    # Get histogram data
    frec, binEdges = np.histogram(WFCharge, bins = nBins)
    binCenters = np.zeros(len(binEdges) - 1)
    for jdx in range(binCenters.size):
        binCenters[jdx] = qScale * (binEdges[jdx + 1] + binEdges[jdx]) / 2
    # Find centroid
    peaks, _ = find_peaks(frec, distance = len(frec))
    # Gaussian fit of histogram
    plt.figure()
    model = GaussianModel()
    params = lmfit.Parameters()
    params.add_many(('center', int(binCenters[peaks]), True, int(binCenters[peaks]) - 20, int(binCenters[peaks]) + 20, None, None),
                    ('amplitude', 30, True, 0.0, None, None, None),
                    ('sigma', 5, True, 0.0, None, None, None))
    result = model.fit(frec, params, x = binCenters)
    report = result.fit_report() # Report of each gaussian fit
    print(report)
    if printResults:
        reportName = figurePath + fileName + 'Hist' + str(nBins) + 'Fit' + str(idx + 1) + 'Report.txt'
        if not isfile(reportName):
            reportFile = open(reportName, 'x')
        else:
            reportFile = open(reportName, 'wt')
        reportFile.write(report)
        reportFile.close()
    dataPlot = plt.plot(binCenters, frec, '.', label = 'V = ' + str(voltList[idx]) + 'V')
    lastColor = dataPlot[0].get_color()
    plt.plot(binCenters, result.best_fit, '-', color = lastColor)
    plt.xlabel('Q / nC')
    plt.ylabel('Cumulative frecuency')
    plt.legend()
    if saveFigs:
        plt.savefig(figurePath + groupName + str(nBins) + 'Fit' + str(idx + 1) + '.png', bbox_inches = 'tight')
    # Store gaussian params for subsequent linear fit
    fitParams = result.best_values
    fitCovMatrix = result.covar
    centroidList[idx] = fitParams['center']
    centroidListError[idx] = fitCovMatrix[0, 0]
    sigmaList[idx] = fitParams['sigma'] **2
    sigmaListError[idx] = fitCovMatrix[2, 2] * 2 * fitParams['sigma']
# Linear fit of gaussian params
if False:
    model = LinearModel()
    params = model.make_params(m = 1, b = 0)
    result = model.fit(sigmaList, params, x = centroidList)
    report = result.fit_report()
    print(report)
    if printResults:
        reportName = figurePath + groupName + str(nBins) + 'FitCentroidsFitReport.txt'
        if not isfile(reportName):
            reportFile = open(reportName, 'x')
        else:
            reportFile = open(reportName, 'wt')
        reportFile.write(report)
        reportFile.close()
    plt.figure()
    # plt.plot(centroidList, sigmaList, '.', label = 'Gaussian fit results')
    plt.errorbar(centroidList, sigmaList, sigmaListError, centroidListError, '.', label = 'Gaussian fit results')
    plt.plot(centroidList, result.best_fit, '-', label = 'Linear fit')
    plt.xlabel('centroid / nC')
    plt.ylabel('sigma^2 / nC^2')
    plt.legend()
    if saveFigs:
        plt.savefig(figurePath + groupName + str(nBins) + 'FitCentroidsFit.png', bbox_inches = 'tight')

# END AND PRINT TIMER
timerEnd = timer()
print('Elapsed time: ' + str(timerEnd - timerStart) + ' s')

# SHOW FIGURES
plt.show(block = True)