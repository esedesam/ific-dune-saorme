# WFAnalysisRepo.py

# Repository of function for analyzing waveforms
#
# Author: Samuel Ortega
# Last Rev.: 07/06/2023

import math, statistics, lmfit
import pandas as ps
import matplotlib.pyplot as plt
import numpy as np
from os import mkdir
from os.path import isfile, isdir
from scipy.optimize import curve_fit
from scipy.integrate import simpson
from scipy.signal import find_peaks
from scipy.stats import poisson
from timeit import default_timer as timer
from lmfit.models import GaussianModel, LinearModel
from matplotlib.ticker import MaxNLocator

# FIT FUNCTIONS
def Gauss(x, A, B, C):
    y = A * np.exp(-1 * B * (x - C)**2)
    return y

def Lorentz(x, amp1, cen1, wid1):
    y = amp1*wid1**2/((x-cen1)**2+wid1**2)
    return y

def polyAnd2Lorentz(x, poly0, poly1, amp1, cen1, wid1, amp2, cen2, wid2):
    y = poly0 + poly1*x + amp1*wid1**2/((x-cen1)**2+wid1**2) + amp2*wid2**2/((x-cen2)**2+wid2**2)
    return y

def Gauss3(x, A1, B1, C1, A2, B2, C2, A3, B3, C3):
    y = A1 * np.exp(-1 * B1 * (x - C1)**2) + A2 * np.exp(-1 * B2 * (x - C2)**2) + A3 * np.exp(-1 * B3 * (x - C3)**2)
    return y

def polyG1(x, poly0, poly1):
    y = poly0 + poly1 * x
    return y

def nGaussFit(x, *args):
    x = np.asarray(x).reshape(-1, 1)
    A = np.array(args[0::3]).reshape(1, -1)
    B = np.array(args[1::3]).reshape(1, -1)
    C = np.array(args[2::3]).reshape(1, -1)
    return np.sum(A * np.exp(-B * (x - C)), axis = 1)

def nGauss(x, args):
    x = np.asarray(x).reshape(-1, 1)
    A = np.array(args[0::3]).reshape(1, -1)
    B = np.array(args[1::3]).reshape(1, -1)
    C = np.array(args[2::3]).reshape(1, -1)
    return np.sum(A * np.exp(-B * (x - C)), axis = 1)

def poisson1(k, lamb):
    '''poisson function, parameter lamb is the fit parameter'''
    return poisson.pmf(k, lamb)

# loadAndNumberWFData: Load raw WF data and number each WF
# Inputs after readHeader only taken if readHeader = False
def preprocessWFData(filePath, fileName, fileExt = '.csv', fileTag = 'Numbered', \
                        readHeader = True, headerLimit = 9, WFCount = 1000, recordLength = 1250, \
                        yColName = 'MATH1', xUnits = "s", yUnits = "V"):

    # Get header information
    headerLimit = headerLimit - 1
    if readHeader:
        WFHeader = ps.read_csv( filePath + 'rawData/' + fileName + fileExt, nrows = headerLimit + 2, header = None )
        for row in range(headerLimit):
            if WFHeader.iloc[row,0] == 'Horizontal Units': xUnits = WFHeader.iloc[row,1]
            elif WFHeader.iloc[row,0] == 'Record Length': recordLength = int( WFHeader.iloc[row,1] )
            elif WFHeader.iloc[row,0] == 'Vertical Units': yUnits = WFHeader.iloc[row,1]
            elif WFHeader.iloc[row,0] == 'FastFrame Count': WFCount = int( WFHeader.iloc[row,1] )

    # Get WaveForms data
    WFData = ps.read_csv(filePath + 'rawData/' + fileName + fileExt, header = headerLimit)

    # WF numberation
    WFHeight = len(WFData.index)
    WFData['WFNumber'] = -1

    if WFCount == WFHeight / recordLength:
        interval = np.array(range(recordLength))
        for WFIdx in range(WFCount):
            WFInterval = WFIdx * recordLength + interval
            WFData.iloc[WFInterval, 2] = WFIdx
    else:
        auxCount = 0
        idxInf = 0
        for idx in range(0, WFHeight - 1):
            if WFData.iloc[idx, 0] >  WFData.iloc[idx + 1, 0]:
                WFData.iloc[idxInf : idx, 2] = auxCount
                auxCount = auxCount + 1
                idxInf = idx + 1

    resultsPath = filePath + 'results/' + fileName + '/'
    if not isdir(resultsPath):
        mkdir(resultsPath)
    figurePath = resultsPath + 'figures/'
    if not isdir(figurePath):
        mkdir(figurePath)
    
    # Save to .csv
    WFData.to_csv(resultsPath + fileName + fileTag + fileExt, index = False)

    return WFData

def peakDetection(WFData, voltageThreshold, figurePath, fileName, \
                  doPeakDetectionPlot = False, doPeakFit = False, maxNumberOfPeakPlots = 10):
    WFPeakCount = 0
    uniqueWFNumber = set(WFData['WFNumber'])
    colNames = WFData.columns
    plotCount = 0

    for num in uniqueWFNumber:
        condition = WFData[colNames[2]] == num
        time = np.array(WFData.loc[condition, colNames[0]])
        voltage = np.array(WFData.loc[condition, colNames[1]])
        maxValue = - np.inf

        for idx, voltValue in enumerate(voltage):
            if voltValue > maxValue:
                maxValueIdx = idx
                maxValue = max([maxValue, voltValue])

        # If peak was detected, then:
        if maxValue > 1.1 * voltageThreshold:
            WFPeakCount = WFPeakCount + 1

            for idx in range(maxValueIdx, 1, -1):
                if voltage[idx] < 0.8 * voltageThreshold:
                    voltageGrad = (voltage[idx] - voltage[idx-1]) / (time[idx] - time[idx-1])
                    if voltageGrad <= 0:
                        infLimitIdx = idx
                        break

            for idx in range(maxValueIdx + 1, len(time)):
                if voltage[idx] < 0.8 * voltageThreshold:
                    voltageGrad = (voltage[idx] - voltage[idx-1]) / (time[idx] - time[idx-1])
                    if voltageGrad >= 0:
                        supLimitIdx = idx
                        break

            if doPeakDetectionPlot and plotCount < maxNumberOfPeakPlots:
                plt.figure()
                peakTime = time[infLimitIdx : supLimitIdx]
                peakVoltage = voltage[infLimitIdx : supLimitIdx]
                plt.plot(time, voltage, "b.", label = "Data")
                plt.plot(peakTime, peakVoltage, 'g.', label = 'Detected peak')
                plt.plot(time[maxValueIdx], voltage[maxValueIdx], 'r.', label = 'Detected peak maximum')
                plt.xlabel('t / s')
                plt.ylabel('V / V')
                plt.legend()
                plt.savefig(figurePath + fileName + '_WF' + str(num) + '.png', bbox_inches = 'tight')
                plotCount = plotCount + 1
            
            if doPeakFit and plotCount < maxNumberOfPeakPlots:
                xScale = 10**6
                yScale = 10**3
                peakTime = xScale * time[infLimitIdx : supLimitIdx]
                peakVoltage = yScale * voltage[infLimitIdx : supLimitIdx]

                plt.figure()
                plt.plot(peakTime, peakVoltage, 'r.', label = 'Detected peak')

                gaussParams, gaussCov = curve_fit(Gauss, peakTime, peakVoltage)
                fitA = gaussParams[0]
                fitB = gaussParams[1]
                fitC = gaussParams[2]
                fitVoltage = Gauss(peakTime, fitA, fitB, fitC)
                plt.plot(peakTime, fitVoltage, '-', label = 'Gaussian fit')

                lorentzParams, lorentzCov = curve_fit(Lorentz, peakTime, peakVoltage)
                fitAmp1 = lorentzParams[0]
                fitCen1 = lorentzParams[1]
                fitWid1 = lorentzParams[2]
                fitVoltage = Lorentz(peakTime, fitAmp1, fitCen1, fitWid1)
                plt.plot(peakTime, fitVoltage, '-', label = 'Lorentz fit')

                customParams, customCov = curve_fit(polyAnd2Lorentz, peakTime, peakVoltage)
                fitPoly0 = customParams[0]
                fitPoly1 = customParams[1]
                fitAmp1 = customParams[2]
                fitCen1 = customParams[3]
                fitWid1 = customParams[4]
                fitAmp2 = customParams[5]
                fitCen2 = customParams[6]
                fitWid2 = customParams[7]
                fitVoltage = polyAnd2Lorentz(peakTime, fitPoly0, fitPoly1, fitAmp1, fitCen1, fitWid1, fitAmp2, fitCen2, fitWid2)
                plt.plot(peakTime, fitVoltage, '-', label = 'Custom fit')

                plt.legend()
                plt.xlabel('t / ' + str(xScale) + '·s')
                plt.ylabel('V / ' + str(yScale) + '·V')
                plotCount = plotCount + 1

    print('Number of peaks detected: ' + str(WFPeakCount) + ' (' + str(100 * WFPeakCount / len(uniqueWFNumber)) + '% of total events)')
    return WFPeakCount

def doBaseLineCorrection(WFData, colNames, WFHeight, uniqueWFNumber, voltageThreshold,\
                         filePath, fileName, fileTag, fileExt, saveCorrV = False):
    WFData['V_BL/C'] = np.zeros(WFHeight)
    for num in uniqueWFNumber:
        condition = WFData[colNames[2]] == num
        rawVolt = np.array(WFData.loc[condition, colNames[1]])
        customBL = statistics.median(rawVolt[rawVolt < voltageThreshold])
        WFData.loc[condition, 'V_BL/C'] = rawVolt - customBL

    if saveCorrV:
        WFData.to_csv(filePath + fileName + fileTag + fileExt, index = False)

    colNames = WFData.columns
    return WFData, colNames

def doBaseLineCorrectionV2(WFData, colNames, WFHeight, uniqueWFNumber, voltageThreshold,\
                         filePath, fileName, fileTag, fileExt, saveCorrV = False):
    WFData['V_BL/C'] = np.zeros(WFHeight)
    for num in uniqueWFNumber:
        condition = WFData[colNames[2]] == num
        rawVolt = np.array(WFData.loc[condition, colNames[1]])
        customTh = min(rawVolt) + 1 * voltageThreshold
        customBL = statistics.median(rawVolt[rawVolt < voltageThreshold])
        WFData.loc[condition, 'V_BL/C'] = rawVolt - customBL

    if saveCorrV:
        WFData.to_csv(filePath + fileName + fileTag + fileExt, index = False)

    colNames = WFData.columns
    return WFData, colNames

def getChargeAndHist(WFData, colNames, WFCount, uniqueWFNumber, nBins,\
                     figurePath, fileName, doHist = True, saveFig = False):
    WFCharge = np.zeros(WFCount)
    for idx, num in enumerate(uniqueWFNumber):
        condition = WFData[colNames[2]] == num
        time = np.array(WFData.loc[condition, colNames[0]])
        voltage = np.array(WFData.loc[condition, colNames[3]])
        if fileName == 'pruebaMass1_0_34_00': # Custom correction for weird high charge value
            charge = simpson(voltage, time)
            if charge < 4e-7:
                WFCharge[idx] = charge
        else:
            charge = simpson(voltage, time)
            if charge < np.inf:
                WFCharge[idx] = charge

    if doHist:
        plt.figure()
        plt.hist(WFCharge, bins = nBins, label = 'Custom median corrected histogram')
        plt.xlabel('Q / C')
        plt.ylabel('Cumulative frequency')
        plt.legend()
        if saveFig:
            plt.savefig(figurePath + fileName + 'Hist' + str(nBins) + '.png', bbox_inches = 'tight')
            
    return WFCharge

def fillQHistBins(WFCharge, nBins, filePath, fileName, saveData = True):
    chargeMin = min(WFCharge)
    chargeMax = max(WFCharge)
    chargeBin = abs(chargeMax - chargeMin) / nBins

    WFChargeCenters = np.zeros(nBins)
    WFChargeFrec = np.zeros(nBins)
    for idx in range(nBins): # Get frecuency of each charge bin
        WFChargeCenters[idx] = chargeMin + (1/2 + idx) * chargeBin
        
        for chargeValue in WFCharge:
            if (WFChargeCenters[idx] - 1/2 * chargeBin) < chargeValue and \
                chargeValue < (WFChargeCenters[idx] + 1/2 * chargeBin):
                WFChargeFrec[idx] = WFChargeFrec[idx] + 1

    auxDict = {'Q': WFChargeCenters, 'F': WFChargeFrec}
    FrecVsCharge = ps.DataFrame(data = auxDict)
    if saveData:
        FrecVsCharge.to_csv(filePath + fileName + 'HistData' + str(nBins) + '.csv', index = False)

    return FrecVsCharge

def doHistGaussianFit(FrecVsCharge, qScale, nBins, figurePath, fileName,\
                      minPeakHeight = np.inf, maxCenterVar = np.inf, minCenterDist = 0,\
                      printResult = False, doPlot = True, saveFig = False):
    scaledCharge = np.asarray(qScale * FrecVsCharge['Q']) # Charge scaling
    frecuency = np.asarray(FrecVsCharge['F'])

    histPeaks, _ = find_peaks(FrecVsCharge['F'], height = minPeakHeight, distance = minCenterDist) # Find histogram peaks
    histPeakNum = len(histPeaks)
    print('No. of peaks detected in charge histogram: %d' % histPeakNum)

    if histPeakNum < 1:
        print('No peaks detected. Change minimum height (current: ' + str(minPeakHeight) + ')')
    else:
        centers = scaledCharge[histPeaks]
        sigmas = np.ones(len(centers)) * 0.01 # 0.35 # 0.01

        model = GaussianModel(prefix = 'g1_')
        for idx in range(1, histPeakNum):
            model = model + GaussianModel(prefix = 'g' + str(idx + 1) + '_')

        params = lmfit.Parameters()
        for idx in range(histPeakNum):
            #               (NAME VALUE VARY MIN  MAX  EXPR  BRUTE_STEP)
            params.add_many(('g' + str(idx + 1) + '_center', centers[idx], True, centers[idx] - maxCenterVar, centers[idx] + maxCenterVar, None, None),
                            ('g' + str(idx + 1) + '_amplitude', 2, True, 0.0, None, None, None),
                            ('g' + str(idx + 1) + '_sigma', sigmas[idx], True, 0.0, 1, None, None))

    result = model.fit(frecuency, params, x = scaledCharge)
    report = result.fit_report()
    print(report)
    if printResult:
        reportName = figurePath + fileName + 'Hist' + str(nBins) + 'FitReport.txt'
        if not isfile(reportName):
            reportFile = open(reportName, 'x')
        else:
            reportFile = open(reportName, 'wt')
        reportFile.write(report)
        reportFile.close()

    if doPlot:
        plt.figure()
        plt.plot(scaledCharge, frecuency, '.', label = 'Data')
        plt.plot(scaledCharge[histPeaks], frecuency[histPeaks], 'x', label = 'Detected peaks')
        plt.plot(scaledCharge, result.best_fit, '-', label = str(histPeakNum) + ' gaussian(s) fit')
        plt.xlabel('Q / '+ getQScalePrefix(qScale) + 'C')
        plt.ylabel('Cumulative frequency')
        plt.legend()
        if saveFig:
            plt.savefig(figurePath + fileName + 'Hist' + str(nBins) + 'Fit.png', bbox_inches = 'tight')

    return result.best_values

def getQScalePrefix(qScale):
    if qScale == 10**9:
        prefix = 'n'
    else:
        order = int(math.floor(math.log(qScale, 10)))
        prefix = '10^' + str(-order)
    
    return prefix

def doCentroidsLinearFit(gaussParams, qScale, nBins, figurePath, fileName,\
                         printResult = False, doPlot = True, saveFig = False):
    numFittedPeaks = int(len(gaussParams) / 3)
    if numFittedPeaks > 1:
        auxNums = np.zeros(numFittedPeaks)
        auxCentroids = np.zeros(numFittedPeaks)
        for idx in range(numFittedPeaks):
            auxNums[idx] = idx + 1
            auxCentroids[idx] = gaussParams['g' + str(idx + 1) + '_center']

        # auxDict = {'N': auxNums, 'Q': auxCentroids}
        # chargeCentroids = ps.DataFrame(data = auxDict)

        model = LinearModel()
        params = model.make_params(m = 1, b = 0)
        result = model.fit(auxCentroids, params, x = auxNums)
        report = result.fit_report()
        print(report)
        if printResult:
            reportName = figurePath + fileName + 'Hist' + str(nBins) + 'CentroidsFitReport.txt'
            if not isfile(reportName):
                reportFile = open(reportName, 'x')
            else:
                reportFile = open(reportName, 'wt')
            reportFile.write(report)
            reportFile.close()

        if doPlot:
            ax = plt.figure().gca()
            plt.plot(auxNums, auxCentroids, '.', label = 'Data')
            plt.plot(auxNums, result.best_fit, '-', label = 'Linear fit')
            plt.xlabel('# peak')
            ax.xaxis.set_major_locator(MaxNLocator(integer = True))
            plt.ylabel('Q / '+ getQScalePrefix(qScale) + 'C')
            plt.legend()
            if saveFig:
                plt.savefig(figurePath + fileName + 'Hist' + str(nBins) + 'CentroidsFit.png', bbox_inches = 'tight')
    else:
        print('Not enough centroids detected')