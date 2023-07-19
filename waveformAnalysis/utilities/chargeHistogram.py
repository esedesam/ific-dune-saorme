import pandas as ps
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import simpson

WFData = ps.read_csv('D:/ific-dune-saorme/waveformAnalysis/rawData/test1999.csv', header = 8)

recordLength = 1250
WFCount = 3000
charge = []

for idx in range(WFCount):
    interval = recordLength * idx + np.array(range(recordLength))

    time = WFData.iloc[interval, 0]
    volt = WFData.iloc[interval, 1]

    charge.append(simpson(volt, time))

plt.hist(charge, bins = 300)
plt.xlabel('Q / C')
plt.ylabel('Cumulative frequency')
plt.show(block = True)