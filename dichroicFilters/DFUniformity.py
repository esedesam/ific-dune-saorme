import matplotlib.pyplot as plt
import pandas as ps
from os import mkdir
from os.path import isdir
from timeit import default_timer as timer
from numpy import sqrt
from DFRepo import *

# INIT TIMER
timerStart = timer()

# SET-UP
zeroPath = 'D:/ific-dune-saorme/dichroicFilters/' # Change to user repo path
filePath = zeroPath + '20230530/'
DFName = '1'
noFilter = 'nofilter'
WLStart = 300
WLEnd = 550
WLStep = 5
WLRange = '%d-%d_%d' % (WLStart, WLEnd, WLStep)
fileExt = '.txt'
fileTag = 'Data'
saveFigs = True
figurePath = filePath + 'figures/'
angle = '0'
dirList = ['horizontal', 'vertical']
posOrigin = [144, 44] # barrido horizontal -> 144 - 24 mm | barrido vertical -> 44 - 164 mm
posConstant = 70
posRefStart = 70
posRefEnd = 190
posRefStep = 30
posRefRange = '%d-%d_%d' % (posRefStart, posRefEnd, posRefStep)
posRefList = range(posRefStart, posRefEnd + int(posRefStep/2), posRefStep)

if not isdir(filePath):
    mkdir(filePath)
if not isdir(figurePath):
    mkdir(figurePath)

# PLOT CURVE OF TRANSMISION VS WL OF EACH ANGLE OF INCIDENCE
plt.figure()
for dir in dirList:
    direction = '_' + dir + '_'
    for idx, posRef in enumerate(posRefList):
        fileName = 'df_' + DFName + '_' + angle + 'deg_' + WLRange + direction + str(posRef)
        noFilterFileName = 'df_' + noFilter + '_' + angle + 'deg_' + WLRange + direction + str(posRef)
        DFData, darkCurrent = loadDFData(filePath, fileName)
        noFilterData, darkCurrent = loadDFData(filePath, noFilterFileName)
        transmissivity = DFData['I'] / noFilterData['I']
        if dir == 'horizontal':
            posFirst = 144
            posLabel = '%d | %d mm' % (posOrigin[0] - idx * posRefStep, posConstant)
        elif dir == 'vertical':
            posLabel = '%d | %d mm' % (posConstant, posOrigin[1] + idx * posRefStep)
        else:
            posLabel = '---'
        plt.plot(DFData['WL'], transmissivity, '-', label = posLabel) # label = '%s %.2f mm' % (dir, posRef)

plt.xlabel('wavelenght / nm')
plt.ylabel('transmissivity')
plt.ylim(0,1)
plt.legend()
if saveFigs:
    plt.savefig(figurePath + 'df_' + WLRange + '_deg' + posRefRange + 'Transmissivity.png', bbox_inches = 'tight')

# MEAN AND STD AT EACH WL
tDataFrame = ps.DataFrame()
for dir in dirList:
    direction = '_' + dir + '_'
    for idx, posRef in enumerate(posRefList):
        fileName = 'df_' + DFName + '_' + angle + 'deg_' + WLRange + direction + str(posRef)
        noFilterFileName = 'df_' + noFilter + '_' + angle + 'deg_' + WLRange + direction + str(posRef)
        DFData, darkCurrent = loadDFData(filePath, fileName)
        noFilterData, darkCurrent = loadDFData(filePath, noFilterFileName)
        tDataFrame[dir + str(posRef)] = DFData['I'] / noFilterData['I']

tMean = tDataFrame.mean(axis = 1)
tErr = tDataFrame.std(axis = 1)
plt.figure()
plt.errorbar(noFilterData['WL'], tMean, tErr, None, '.', label = 'Mean values')
plt.xlabel('wavelength / nm')
plt.ylabel('transmissivity')
plt.ylim(0,1)
plt.legend()
if saveFigs:
    plt.savefig(figurePath + 'df_' + WLRange + '_deg' + posRefRange + 'TransmissivityMeanAndStd.png', bbox_inches = 'tight')

# LAMP STABILITY
plt.figure()
for dir in dirList:
    direction = '_' + dir + '_'
    for idx, posRef in enumerate(posRefList):
        noFilterFileName = 'df_' + noFilter + '_' + angle + 'deg_' + WLRange + direction + str(posRef)
        noFilterData, darkCurrent = loadDFData(filePath, noFilterFileName)
        if dir == 'horizontal':
            posFirst = 144
            posLabel = '%d | %d mm' % (posOrigin[0] - idx * posRefStep, posConstant)
        elif dir == 'vertical':
            posLabel = '%d | %d mm' % (posConstant, posOrigin[1] + idx * posRefStep)
        else:
            posLabel = '---'
        plt.errorbar(noFilterData['WL'], noFilterData['I'], noFilterData['RMS'], None, '-', label = posLabel)

plt.xlabel('wavelength / nm')
plt.ylabel('I / nA')
plt.legend()
if saveFigs:
    plt.savefig(figurePath + 'df_' + WLRange + '_deg' + posRefRange + 'INoFilter.png', bbox_inches = 'tight')

# RELATIVE ERROR TO FIRST NO FILTER DATA
plt.figure()
for dir in dirList:
    direction = '_' + dir + '_'
    for idx, posRef in enumerate(posRefList):
        noFilterFileName = 'df_' + noFilter + '_' + angle + 'deg_' + WLRange + direction + str(posRef)
        noFilterData, darkCurrent = loadDFData(filePath, noFilterFileName)
        if (idx == 0) and (dir == 'horizontal'):
            noFilterDataRef = noFilterData
        else:
            errRel = (noFilterData['I'] - noFilterDataRef['I']) / noFilterDataRef['I']
            errRelErr = sqrt( ( (sqrt(noFilterData['RMS']**2 + noFilterDataRef['RMS']**2)) / (noFilterData['I'] - noFilterDataRef['I']) )**2 + (noFilterDataRef['RMS'] / noFilterDataRef['I'])**2 )
            if dir == 'horizontal':
                posFirst = 144
                posLabel = '%d | %d mm' % (posOrigin[0] - idx * posRefStep, posConstant)
            elif dir == 'vertical':
                posLabel = '%d | %d mm' % (posConstant, posOrigin[1] + idx * posRefStep)
            else:
                posLabel = '---'
            plt.errorbar(noFilterData['WL'], 100 * errRel, errRelErr, None, '.', label = posLabel)

plt.xlabel('wavelength / nm')
plt.ylabel('Relative error (I) / %')
plt.legend()
if saveFigs:
    plt.savefig(figurePath + 'df_' + WLRange + '_deg' + posRefRange + 'INoFilterRelErr.png', bbox_inches = 'tight')

# MEAN AND STD AT EACH WL OF NO FILTER DATA
INoFilterDataFrame = ps.DataFrame()
for dir in dirList:
    direction = '_' + dir + '_'
    for idx, posRef in enumerate(posRefList):
        noFilterFileName = 'df_' + noFilter + '_' + angle + 'deg_' + WLRange + direction + str(posRef)
        noFilterData, darkCurrent = loadDFData(filePath, noFilterFileName)
        INoFilterDataFrame[dir + str(posRef)] = noFilterData['I']

IMean = INoFilterDataFrame.mean(axis = 1)
IErr = INoFilterDataFrame.std(axis = 1)
plt.figure()
plt.errorbar(noFilterData['WL'], IMean, IErr, None, '.', label = 'Mean values')
plt.xlabel('wavelength / nm')
plt.ylabel('I / nA')
plt.legend()
if saveFigs:
    plt.savefig(figurePath + 'df_' + WLRange + '_deg' + posRefRange + 'INoFilterMeanAndStd.png', bbox_inches = 'tight')

# END AND PRINT TIMER
timerEnd = timer()
print('Elapsed time: ' + str(timerEnd - timerStart) + ' s')

# SHOW FIGURES
plt.show(block = True)