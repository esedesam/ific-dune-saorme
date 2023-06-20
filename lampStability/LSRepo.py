import math, statistics, lmfit
import pandas as ps
import matplotlib.pyplot as plt
import numpy as np
from os.path import isfile
from scipy.optimize import curve_fit
from scipy.integrate import simpson
from scipy.signal import find_peaks
from scipy.stats import poisson
from timeit import default_timer as timer
from lmfit.models import GaussianModel, LinearModel
from matplotlib.ticker import MaxNLocator

def loadLampData(filePath, fileName, fileExt = '.txt', fileTag = 'Data', \
                        readHeader = True, headerLimit = 7):
    # Get header information
    # headerLimit = headerLimit - 1
    if readHeader:
        DFHeader = ps.read_csv(filePath + fileName + fileExt, nrows = headerLimit + 2, header = None,\
                               delim_whitespace = True, names = ['a', 'b', 'c']) 
        for row in range(headerLimit):
            if DFHeader.iloc[row,0] == 'DC':
                DCValue = DFHeader.iloc[row,1]
                DCError = DFHeader.iloc[row,2]
                darkCurrent = np.asarray([DCValue, DCError])
            if DFHeader.iloc[row,0] == 'Time' and DFHeader.iloc[row,1] == 'Ini:':
                dateAndTime = DFHeader.iloc[row,2]

    # Get WaveForms data
    DFData = ps.read_csv(filePath + fileName + fileExt, header = headerLimit,\
                         engine='python', skipfooter = 1,\
                         dtype = np.float64, delim_whitespace = True)

    # Save to .csv
    # DFData.to_csv(filePath + fileName + fileTag + fileExt, index = False)

    return DFData, darkCurrent, dateAndTime