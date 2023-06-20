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
groupName = 'g_rt_sam'
fileNameList = ['sam_34v_3k_131v', 'sam_34v_3k_135v', 'sam_34v_3k_140v', 'sam_34v_3k_145v', 'sam_34v_3k_150v',\
                'sam_34v_3k_155v', 'sam_34v_3k_160v', 'sam_34v_3k_165v', 'sam_34v_3k_170v', 'sam_34v_3k_180v',\
                'sam_34v_3k_185v', 'sam_34v_3k_200v', 'sam_34v_3k_210v', 'sam_34v_3k_220v', 'sam_34v_3k_250v']
voltList = [1.31, 1.35, 1.40, 1.45, 1.50, 1.55, 1.60, 1.65, 1.70, 1.80, 1.85, 2.00, 2.10, 2.20, 2.50]

filePath = zeroPath + 'results/' + groupName + '/'
fileExt = '.csv'
fileTag = 'Numbered'
figurePath = filePath + 'figures/'

if not isdir(filePath):
    mkdir(filePath)
if not isdir(figurePath):
    mkdir(figurePath)

# Optional figures(.png) and results(.txt) saving
saveFigs = True
printResults = True

voltageThreshold = 0.01
nBins = 200
qScale = 10**9

#####################################################################

# GET DATA, PROCESS AND HISTOGRAM
fitHist = True # False -> plot histograms | True -> fit histograms and get gain
centroidList = np.zeros(len(fileNameList))
centroidListError = np.zeros(len(fileNameList))
sigmaListError = np.zeros(len(fileNameList))
sigmaList = np.zeros(len(fileNameList))
plt.figure()
for idx, fileName in enumerate(fileNameList):
    # Preprocessing
    dataPath = zeroPath + 'results/' + fileName + '/'
    preprocessedName = dataPath + fileName + fileTag + fileExt
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
                                figurePath, fileName, doHist = False, saveFig = saveFigs)
    if not fitHist:
        plt.hist(WFCharge, bins = nBins, label = 'V = ' + str(voltList[idx]) + 'V')
    else:
        # Get histogram data
        frec, binEdges = np.histogram(WFCharge, bins = nBins)
        binCenters = np.zeros(len(binEdges) - 1)
        for jdx in range(binCenters.size):
            binCenters[jdx] = qScale * (binEdges[jdx + 1] + binEdges[jdx]) / 2
        # Find centroid
        peaks, _ = find_peaks(frec, distance = len(frec))
        # Gaussian fit of histogram
        model = GaussianModel()
        params = lmfit.Parameters()
        params.add_many(('center', int(binCenters[peaks]), True, int(binCenters[peaks]) - 20, int(binCenters[peaks]) + 20, None, None),
                        ('amplitude', 30, True, 0.0, None, None, None),
                        ('sigma', 5, True, 0.0, None, None, None))
        result = model.fit(frec, params, x = binCenters)
        if False:
            report = result.fit_report() # Report of each gaussian fit
            reportName = figurePath + fileName + 'Hist' + str(nBins) + 'FitReport.txt'
            if not isfile(reportName):
                reportFile = open(reportName, 'x')
            else:
                reportFile = open(reportName, 'wt')
            reportFile.write(report)
            reportFile.close()
        dataPlot = plt.plot(binCenters, frec, '.', label = 'V = ' + str(voltList[idx]) + 'V')
        lastColor = dataPlot[0].get_color()
        # plt.plot(binCenters[peaks], frec[peaks], 'x', color = 'k', label = 'V = ' + str(voltList[idx]) + 'V (centroid)')
        plt.plot(binCenters, result.best_fit, '-', color = lastColor) # , label = 'V = ' + str(voltList[idx]) + 'V (gaussian fit)')
        # Store gaussian params for subsequent linear fit
        fitParams = result.best_values
        fitCovMatrix = result.covar
        centroidList[idx] = fitParams['center']
        centroidListError[idx] = fitCovMatrix[0, 0]
        sigmaList[idx] = fitParams['sigma'] **2
        sigmaListError[idx] = fitCovMatrix[2, 2] * 2 * fitParams['sigma']

if not fitHist:
    plt.xlabel('Q / C')
    plt.ylabel('Cumulative frecuency')
    plt.legend()
    if saveFigs:
        plt.savefig(figurePath + groupName + str(nBins) + '.png', bbox_inches = 'tight')
else:
    plt.xlabel('Q / nC')
    plt.ylabel('Cumulative frecuency')
    plt.legend()
    if saveFigs:
        plt.savefig(figurePath + groupName + str(nBins) + 'Fit.png', bbox_inches = 'tight')
    # Linear fit of gaussian params
    model = LinearModel()
    params = model.make_params(m = 1, b = 0)
    result = model.fit(sigmaList, params, x = centroidList)
    if printResults:
        report = result.fit_report()
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
    plt.savefig(figurePath + groupName + str(nBins) + 'FitCentroidsFit.png', bbox_inches = 'tight')

    # Quad fit of gaussian params
    model = QuadraticModel()
    params = model.make_params(a = 1, b = 1, c = 0)
    result = model.fit(sigmaList, params, x = centroidList)
    if printResults:
        report = result.fit_report()
        reportName = figurePath + groupName + str(nBins) + 'FitCentroidsFitQuadReport.txt'
        if not isfile(reportName):
            reportFile = open(reportName, 'x')
        else:
            reportFile = open(reportName, 'wt')
        reportFile.write(report)
        reportFile.close()
    plt.figure()
    # plt.plot(centroidList, sigmaList, '.', label = 'Gaussian fit results')
    plt.errorbar(centroidList, sigmaList, sigmaListError, centroidListError, '.', label = 'Gaussian fit results')
    plt.plot(centroidList, result.best_fit, '-', label = 'Quad fit')
    plt.xlabel('centroid / nC')
    plt.ylabel('sigma^2 / nC^2')
    plt.legend()
    plt.savefig(figurePath + groupName + str(nBins) + 'FitCentroidsFitQuad.png', bbox_inches = 'tight')

# END AND PRINT TIMER
timerEnd = timer()
print('Elapsed time: ' + str(timerEnd - timerStart) + ' s')

# SHOW FIGURES
plt.show(block = True)