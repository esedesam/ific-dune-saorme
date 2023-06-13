import lmfit
import matplotlib.pyplot as plt
import pandas as ps
import numpy as np
from os import mkdir
from os.path import isfile, isdir
from timeit import default_timer as timer
from lmfit.models import SplineModel, ExpressionModel
from numpy import sqrt
from DFRepo import *

# INIT TIMER
timerStart = timer()

# SET-UP
zeroPath = 'D:/ific-dune-saorme/dichroicFilters/' # Change to user repo path
date = '20230523'
filePath = zeroPath + date + '/'
DFName = '1'
noFilter = 'nofilter'
WLStart = 300
WLEnd = 550
WLStep = 5
WLRange = '%d-%d_%d' % (WLStart, WLEnd, WLStep)
fileExt = '.txt'
fileTag = 'Data'
saveFigs = False
printResults = False
figurePath = filePath + 'figures/'
stepToAngle = 1.0112
angleStart = 0
angleEnd = 70
angleStep = 10
angleRange = '%d-%d_%d' % (angleStart, angleEnd, angleStep)
angleList = range(angleStart, angleEnd + int(angleStep/2), angleStep)
angleValues = 1.0112 * np.array(angleList)
# angleList = [0,5,10,15,20]

if not isdir(filePath):
    mkdir(filePath)
if not isdir(figurePath):
    mkdir(figurePath)

# LAMP STABILITY
plt.figure()
for angle in angleList:
    noFilterFileName = 'df_' + noFilter + '_' + str(angle) + 'deg_' + WLRange
    noFilterData, darkCurrent = loadDFData(filePath, noFilterFileName)
    plt.errorbar(noFilterData['WL'], noFilterData['I'], noFilterData['RMS'], None, '.', label = '%.2f deg' % (1.0112 * angle))

plt.xlabel('wavelength / nm')
plt.ylabel('I / nA')
plt.legend()
if saveFigs:
    plt.savefig(figurePath + date + 'INoFilter.png', bbox_inches = 'tight')

plt.figure()
for angle in angleList:
    noFilterFileName = 'df_' + noFilter + '_' + str(angle) + 'deg_' + WLRange
    noFilterData, darkCurrent = loadDFData(filePath, noFilterFileName)
    if angle == angleList[0]:
        noFilterDataRef = noFilterData
    else:
        errRel = (noFilterData['I'] - noFilterDataRef['I']) / noFilterDataRef['I']
        errRelErr = sqrt( ( (sqrt(noFilterData['RMS']**2 + noFilterDataRef['RMS']**2)) / (noFilterData['I'] - noFilterDataRef['I']) )**2 + (noFilterDataRef['RMS'] / noFilterDataRef['I'])**2 )
        plt.errorbar(noFilterData['WL'], errRel, errRelErr, None, '.', label = '%.2f deg' % (1.0112 * angle))

plt.xlabel('wavelength / nm')
plt.ylabel('Relative error (I)')
plt.legend()
if saveFigs:
    plt.savefig(figurePath + date + 'INoFilterRelErr.png', bbox_inches = 'tight')

plt.figure()
INoFilterData = ps.DataFrame()
for angle in angleList:
    noFilterFileName = 'df_' + noFilter + '_' + str(angle) + 'deg_' + WLRange
    noFilterData, darkCurrent = loadDFData(filePath, noFilterFileName)
    INoFilterData[str(angle)] = noFilterData['I']

IMean = INoFilterData.mean(axis = 1)
IErr = INoFilterData.std(axis = 1)
plt.errorbar(noFilterData['WL'], IMean, IErr, None, '.', label = 'Mean values')
plt.xlabel('wavelength / nm')
plt.ylabel('I / nA')
plt.legend()
if saveFigs:
    plt.savefig(figurePath + date + 'INoFilter.png', bbox_inches = 'tight')

# END AND PRINT TIMER
timerEnd = timer()
print('Elapsed time: ' + str(timerEnd - timerStart) + ' s')

# SHOW FIGURES
plt.show(block = True)