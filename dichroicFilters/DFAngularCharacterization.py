import lmfit
import matplotlib.pyplot as plt
import numpy as np
from os import mkdir
from os.path import isfile, isdir
from timeit import default_timer as timer
from lmfit.models import SplineModel, ExpressionModel
from numpy import sqrt, sin, deg2rad, linspace
from DFRepo import *

# INIT TIMER
timerStart = timer()

# SET-UP
zeroPath = 'D:/ific-dune-saorme/dichroicFilters/' # Change to user repo path
filePath = zeroPath + '20230523/'
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
angleEnd = 60
angleStep = 10
angleRange = '%d-%d_%d' % (angleStart, angleEnd, angleStep)
angleList = range(angleStart, angleEnd + int(angleStep/2), angleStep)

if not isdir(filePath):
    mkdir(filePath)
if not isdir(figurePath):
    mkdir(figurePath)

# PLOT CURVE OF TRANSMISION VS WL OF EACH ANGLE OF INCIDENCE
plt.figure()
for angle in angleList:
    fileName = 'df_' + DFName + '_' + str(angle) + 'deg_' + WLRange
    noFilterFileName = 'df_' + noFilter + '_' + str(angle) + 'deg_' + WLRange
    DFData, darkCurrent = loadDFData(filePath, fileName)
    noFilterData, darkCurrent = loadDFData(filePath, noFilterFileName)
    transmissivity = DFData['I'] / noFilterData['I']
    plt.plot(DFData['WL'], transmissivity, '-', label = '%.2f deg' % (1.0112 * angle))

plt.xlabel('wavelenght / nm')
plt.ylabel('transmissivity')
plt.ylim(0,1)
plt.legend()
plt.savefig(figurePath + 'df_' + WLRange + '_deg' + angleRange + 'Transmissivity.png', bbox_inches = 'tight')

# CUSTOM FIT TO GET WL OF HALF HEIGHT ¿MEDIA ALTURA ó t = 0.5?
knot_xvals = np.array(range(320, 550, 20))
model = SplineModel(xknots = knot_xvals)
params = lmfit.Parameters()
WLAtHH = np.zeros(len(angleList))
for idx, angle in enumerate(angleList):
    fileName = 'df_' + DFName + '_' + str(angle) + 'deg_' + WLRange
    noFilterFileName = 'df_' + noFilter + '_' + str(angle) + 'deg_' + WLRange
    DFData, darkCurrent = loadDFData(filePath, fileName)
    noFilterData, darkCurrent = loadDFData(filePath, noFilterFileName)
    transmissivity = DFData['I'] / noFilterData['I']
    params.update(model.guess(transmissivity, DFData['WL']))
    result = model.fit(transmissivity, params, x = DFData['WL'])
    # print(result.fit_report(min_correl = 0.3))
    fitT = 0
    auxWL = 0
    midT = 0.5
    for wl in linspace(350, 500, 1000):
        auxFitT = model.eval(result.params, x = wl)
        if abs(auxFitT - midT) < abs(fitT - midT):
            fitT = auxFitT
            auxWL = wl
    
    WLAtHH[idx] = auxWL
    # plt.figure()
    # plt.plot(DFData['WL'], transmissivity, '.', label = 'Data')
    # plt.plot(DFData['WL'], result.best_fit, '-', label = 'Best fit')
    # plt.plot(auxWL, fitT, 'x', label = 'WL at half height')
    # plt.xlabel('wavelenght / nm')
    # plt.ylabel('transmissivity')
    # plt.ylim(0,1)
    # plt.legend()

# RESULTS AND PLOT HH WL VS ANGLE WITH ECUATION FIT
angleValues = 1.0112 * np.array(angleList)
n0 = 1
n = 1.6
WLAtHHTeo = WLAtHH[0] * sqrt(1 - (n0 / n * sin(deg2rad(angleValues - angleValues[0])))**2)
# model = LinearModel()
# params = model.make_params(m = 1, b = 0)
angleSpace = linspace(angleStart, angleEnd, 100)
model = ExpressionModel('lambda0 * sqrt(1 - (1 / nRel * sin(deg2rad(x - theta0)))**2)', independent_vars = ['x'])
params = lmfit.Parameters()
params.add_many(('lambda0', WLAtHH[0], False, None, None, None, None),
                ('nRel', 1.6, True, 1, 2, None, None),
                ('theta0', angleValues[0], False, None, None, None, None))
result = model.fit(WLAtHH, params, x = angleValues)
report = result.fit_report()
reportName = figurePath + 'df_' + WLRange + '_deg' + angleRange + 'TransmissivityHHFitReport.txt'
if not isfile(reportName):
    reportFile = open(reportName, 'x')
else:
    reportFile = open(reportName, 'wt')
reportFile.write(report)
reportFile.close()
plt.figure()
plt.plot(angleValues, WLAtHH, '.', label = 'WL at half height')
plt.plot(angleSpace, model.eval(result.params, x = angleSpace), '-', label = 'Teorical fit')
plt.plot(angleValues, WLAtHHTeo, 'x', label = 'Teorical values (n=%.1f)' % n)
plt.xlabel('angle / º')
plt.ylabel('wavelenght / nm')
plt.legend()
plt.savefig(figurePath + 'df_' + WLRange + '_deg' + angleRange + 'TransmissivityHHFit.png', bbox_inches = 'tight')

# END AND PRINT TIMER
timerEnd = timer()
print('Elapsed time: ' + str(timerEnd - timerStart) + ' s')

# SHOW FIGURES
plt.show(block = True)