import lmfit
import matplotlib.pyplot as plt
import pandas as ps
import numpy as np
from os import mkdir
from os.path import isfile, isdir
from timeit import default_timer as timer
from lmfit.models import SplineModel, ExpressionModel
from numpy import sqrt
from LSRepo import *

# INIT TIMER
timerStart = timer()

# SET-UP
zeroPath = 'D:/ific-dune-saorme/lampStability/' # Change to user repo path
series = '20230619_deuterium'
filePath = zeroPath + series + '/'
noFilter = 'nofilter'
WLStart = 180
WLEnd = 300
WLStep = 10
WLRange = '%d-%d_%d' % (WLStart, WLEnd, WLStep)
angle = 0
fileExt = '.txt'
fileTag = 'Data'

numSeries = 33

saveFigs = True
# printResults = False
figurePath = filePath + 'figures/'

if not isdir(filePath):
    mkdir(filePath)
if not isdir(figurePath):
    mkdir(figurePath)

# LOAD AND PLOT DATA
timestamps = []
plt.figure()
for num in range(0, numSeries):
    fileName = 'df_' + noFilter + '_' + str(angle) + 'deg_' + WLRange + ' (' + str(num) + ')'
    data, darkCurrent, dateAndTime = loadLampData(filePath, fileName)
    plt.errorbar(data['WL'], data['I'], data['RMS'], None, '-')
    timestamps.append(dateAndTime)
timeDiff, timeDiffLg = getTimeDiff(timestamps)
plt.xlabel('wavelenght / nm')
plt.ylabel('I / \u03BCA')
plt.legend(timeDiffLg, ncol = 2, bbox_to_anchor=(1, 1))
if saveFigs:
    plt.savefig(figurePath + series + '.png', bbox_inches = 'tight')

# I VS TIME (poco eficiente)
plt.figure()
for idx, wl in enumerate(range(WLStart, WLEnd + 1, WLStep)):
    IList = []
    errorList = []
    for num in range(0, numSeries):
        fileName = 'df_' + noFilter + '_' + str(angle) + 'deg_' + WLRange + ' (' + str(num) + ')'
        data, darkCurrent, dateAndTime = loadLampData(filePath, fileName, substractDC = False)
        IList.append(data.loc[idx, 'I'])
        errorList.append(data.loc[idx, 'RMS'])
    plt.errorbar(timeDiff, IList, errorList, None, '-', label = f'{wl} nm')
plt.xlabel('time / min')
plt.ylabel('I / \u03BCA')
plt.legend(bbox_to_anchor=(1, 1))
if saveFigs:
    plt.savefig(figurePath + series + 'IVsTime.png', bbox_inches = 'tight')

# RATIOS
# Calculation
LSRatioData = ps.DataFrame()
for num in range(0, numSeries):
    fileName = 'df_' + noFilter + '_' + str(angle) + 'deg_' + WLRange + ' (' + str(num) + ')'
    data, darkCurrent, dateAndTime = loadLampData(filePath, fileName)
    if num == 0:
        LSRatioData['WL'] = data['WL']
        refData = data['I']
        refDataErr = data['RMS']
    LSRatioData['Ratio' + str(num)] = data['I'] / refData
    LSRatioData['Error' + str(num)] = LSRatioData['Ratio' + str(num)] *\
            sqrt((data['RMS'] / data['I'])**2 + (refDataErr / refData)**2)
# Plot
plt.figure()
for num in range(0, numSeries):
    plt.errorbar(LSRatioData['WL'], LSRatioData['Ratio' + str(num)],\
                 LSRatioData['Error' + str(num)], None, '-', label = timeDiffLg[num])
plt.xlabel('wavelenght / nm')
plt.ylabel('ratio (ref: ' + str(timestamps[0]) + ')')
plt.legend(ncol = 2, bbox_to_anchor=(1, 1))
if saveFigs:
    plt.savefig(figurePath + series + 'RatioVsWl.png', bbox_inches = 'tight')

# # RELATIVE ERRORS
# # Calculation
# LSRelErrData = ps.DataFrame()
# for num in range(0, numSeries):
#     fileName = 'df_' + noFilter + '_' + str(angle) + 'deg_' + WLRange + ' (' + str(num) + ')'
#     data, darkCurrent, dateAndTime = loadLampData(filePath, fileName)
#     if num == 0:
#         LSRelErrData['WL'] = data['WL']
#         refData = data['I']
#         refDataErr = data['RMS']
#     else:
#         LSRelErrData['RelErr' + str(num) + ' / %'] = 100 * abs(data['I'] - refData) / refData
#         LSRelErrData['Error' + str(num)] = sqrt((sqrt(data['RMS']**2 + refDataErr**2) / (data['I'] - refData))**2\
#                                                 + (refDataErr / refData)**2)
# # Plot
# plt.figure()
# for num in range(1, numSeries):
#     plt.errorbar(LSRelErrData['WL'], LSRelErrData['RelErr' + str(num) + ' / %'],\
#                  LSRelErrData['Error' + str(num)], None, '-', label = timeDiffLg[num])
# plt.xlabel('wavelenght / nm')
# plt.ylabel('Relative error (ref: ' + str(timestamps[0]) + ') / %')
# # plt.legend()
# if saveFigs:
#     plt.savefig(figurePath + series + 'RelErr.png', bbox_inches = 'tight')

# RATIO VS TIME
plt.figure()
for idx, wl in enumerate(range(WLStart, WLEnd + 1, WLStep)):
    ratioList = []
    errorList = []
    for num in range(0, numSeries):
        ratioList.append(LSRatioData.loc[idx, 'Ratio' + str(num)])
        errorList.append(LSRatioData.loc[idx, 'Error' + str(num)])
    plt.errorbar(timeDiff, ratioList, errorList, None, '-', label = f'{wl} nm') # timeDiff[1:]
plt.xlabel('time / min')
plt.ylabel('ratio (ref: ' + str(timestamps[0]) + ')')
plt.legend(bbox_to_anchor=(1, 1))
if saveFigs:
    plt.savefig(figurePath + series + 'RatioVsTime.png', bbox_inches = 'tight')

# END AND PRINT TIMER
timerEnd = timer()
print('Elapsed time: ' + str(timerEnd - timerStart) + ' s')

# SHOW FIGURES
plt.show(block = True)