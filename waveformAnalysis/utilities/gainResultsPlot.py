import matplotlib.pyplot as plt

x = [1.79, 1.91, 1.66, 2.096,\
     2.11, 2.06, 2.04, 2.00, 2.03, 2.04,\
     1.66, 1.8, 2.12, 2.01, 1.92, 2.158,\
     1.66, 2.1, 2.22, 2.04, 2.35, 1.97]
xErr = [0.03, 0.10, 0.06, 0.004,\
        0.03, 0.03, 0.06, 0.08, 0.12, 0.12,\
        0.06, 0.2, 0.03, 0.12, 0.08, 0.009,\
        0.10, 0.4, 0.03, 0.10, 0.02, 0.04]
y = ['1-MG-L', '1-MG-Q', '1-RandTrig', '1-SigTrig',\
     '2-RandTrig1', '2-RandTrig2', '2-RandTrig3', '2-SigTrig1', '2-SigTrig2', '2-SigTrig3',\
     '3-MG-L', '3-MG-Q', '3-RandTrig1', '3-RandTrig2', '3-SigTrig1', '3-SigTrig2',\
     '4-MG-L', '4-MG-Q', '4-RandTrig1', '4-RandTrig2', '4-SigTrig1', '4-SigTrig2']

plt.figure()
for i in range(len(x)):
    if (0 <= i) and (i <= 3):
        color = 'r'
    elif (4 <= i) and (i <= 9):
        color = 'g'
    elif (10 <= i) and (i <= 15):
        color = 'b'
    elif (16 <= i) and (i <= 21):
        color = 'y'
    plt.errorbar(x[i], y[i], None, xErr[i], '.', ecolor = color, color = color)
    
plt.savefig('./waveformAnalysis/gainResultsPlot.png', bbox_inches = 'tight')


plt.show(block = True)