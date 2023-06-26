import math, statistics, lmfit
import pandas as ps
import matplotlib.pyplot as plt
import numpy as np
from os.path import isfile
from datetime import datetime

def loadLampData(filePath, fileName, fileExt = '.txt', fileTag = 'Data', \
                        readHeader = True, headerLimit = 7, substractDC = True):
    # Get header information
    # headerLimit = headerLimit - 1
    if readHeader:
        DFHeader = ps.read_csv(filePath + fileName + fileExt, nrows = headerLimit + 2, header = 1,\
                               delim_whitespace = True, names = ['a', 'b', 'c']) 
        for row in range(headerLimit - 1):
            if DFHeader.iloc[row,0] == 'DC':
                DCValue = DFHeader.iloc[row,1]
                DCError = DFHeader.iloc[row,2]
                darkCurrent = np.asarray([DCValue, DCError], dtype = 'float64')
            if DFHeader.iloc[row,0] == 'Time' and DFHeader.iloc[row,1] == 'Ini:':
                dateAndTime = DFHeader.iloc[row, 2]

    # Get WaveForms data
    DFData = ps.read_csv(filePath + fileName + fileExt, header = headerLimit,\
                         engine = 'python', skipfooter = 1,\
                         dtype = np.float64, delim_whitespace = True)
    if substractDC:
        DFData['I'] = DFData['I'] - darkCurrent[0]
    # Save to .csv
    # DFData.to_csv(filePath + fileName + fileTag + fileExt, index = False)

    return DFData, darkCurrent, dateAndTime

def getTimeDiff(timestamps):
    format = '%d/%m/%Y-%H:%M:%S.%f'
    timeDiff = []
    timeDiffFrmt = []
    for timestamp in timestamps:
        diffTS = datetime.strptime(timestamp, format) - datetime.strptime(timestamps[0], format)
        diff = diffTS.total_seconds() / 60
        timeDiff.append(diff)
        if diff < 60:
            formattedDiff = f'{int(round(diff))} min'
        else:
            hours = diff // 60
            mins = diff % 60
            formattedDiff = f'{int(hours)} h {int(round(mins))} min'
        timeDiffFrmt.append(formattedDiff)
    
    return timeDiff, timeDiffFrmt