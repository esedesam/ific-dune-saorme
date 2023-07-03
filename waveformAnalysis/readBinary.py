import tekwfm
import numpy as np
import matplotlib.pyplot as plt

volts, tstart, tscale, tfrac, tdatefrac, tdate = tekwfm.read_wfm('D:/ific-dune-saorme/waveformAnalysis/rawData/ch2_27_06_130v.wfm')
toff = tfrac * tscale
samples, frames = volts.shape
tstop = samples * tscale + tstart
t = np.linspace(tstart + toff, tstop + toff, num = samples, endpoint = False)
plt.plot(t, volts)
plt.xlabel('time (s)')
plt.ylabel('volts (V)')

plt.show(block = True)