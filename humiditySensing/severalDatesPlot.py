import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import norm

dates = ['20230704', '20230706']
names = ['offsetValue', 'offsetError', 'ccValue', 'ccError']

offsetValue = []
offsetError = []
ccValue = []
ccError = []
for date in dates:
    for name in names:
        with open('D:/ific-dune-saorme/humiditySensing/' + date + '_' + name + '.txt', 'r') as f:
            auxStr = f.read()
        auxStr = auxStr.split(sep = '[')[1]
        auxStr = auxStr.split(sep = ']')[0]
        auxStr = auxStr.split(sep = ',')
        auxNum = [eval(i) for i in auxStr]
        if name == 'offsetValue':
            offsetValue.extend(auxNum)
        elif name == 'offsetError':
            offsetError.extend(auxNum)
        elif name == 'ccValue':
            ccValue.extend(auxNum)
        elif name == 'ccError':
            ccError.extend(auxNum)
        else:
            raise Exception('Jordi explotador.\n')

plt.errorbar(ccValue[0:4], offsetValue[0:4], offsetError[0:4], ccError[0:4], '.', capsize = 5, label = 'T = 30 ºC')
plt.errorbar(ccValue[4:8], offsetValue[4:8], offsetError[4:8], ccError[4:8], '.', capsize = 5, label = 'T = 20 ºC')
plt.errorbar(ccValue[8:12], offsetValue[8:12], offsetError[8:12], ccError[8:12], '.', capsize = 5, label = 'T = 10 ºC')
plt.errorbar(ccValue[12:-1], offsetValue[12:-1], offsetError[12:-1], ccError[12:-1], '.', capsize = 5, label = 'T = 0, -60 ºC')
plt.legend()
# for idx in range(len(ccValue)):
#     plt.errorbar(ccValue[idx], offsetValue[idx], offsetError[idx], ccError[idx], '.', capsize = 5)
# plt.legend(['T = 30 ºC', 'T = 30 ºC', 'T = 30 ºC', 'T = 30 ºC', 'T = 20 ºC', 'T = 20 ºC', 'T = 20 ºC', 'T = 20 ºC', 'T = 10 ºC','T = 10 ºC','T = 10 ºC','T = 10 ºC', 'T = 0 ºC', 'T = -20 ºC', 'T = -30 ºC', 'T = -40 ºC', 'T = -50 ºC', 'T = -60 ºC', 'T = -40 ºC', 'T = -20 ºC', 'T = -10 ºC', 'T = 0 ºC'],\
        #    bbox_to_anchor = (1.02, 1.1))
plt.xlabel('Climatic chamber humidity / %')
plt.ylabel('humidity offset (CC - DHT11) / %')
defLeft, defRight = plt.xlim()
plt.xlim((min([defLeft, 0]), max([defRight, 100])))

plt.savefig('D:/ific-dune-saorme/humiditySensing/several_humidity_offset.png', bbox_inches = 'tight')

offsetMean = np.mean(offsetValue)
offsetStd = np.std(offsetValue)
offsetErrorMean = np.mean(offsetError)
print(f'std: {offsetStd}\nMean error: {offsetErrorMean}')
offsetFinalError = np.sqrt(offsetStd ** 2 + offsetErrorMean ** 2)
plt.figure()
plt.title('Bias and systematic uncertainty of DHT11')
plt.hist(offsetValue, bins = 8, density = True, fill = False, linewidth = 3, label = "Humidity Accuracy \n $\mu$={0:.1f} %; $\sigma$={1:.1f} %".format(offsetMean, offsetStd))
x_axis = np.arange(-9, 9, 0.01)
# plt.plot(x_axis, norm.pdf(x_axis, offsetMean, offsetStd))
defLeft, defRight = plt.ylim()
yPos = (defLeft + defRight) / 2
plt.xlabel('(CC - DHT11) / %')
plt.ylabel('Normalized cumulative frecuency')
plt.legend()

plt.savefig('D:/ific-dune-saorme/humiditySensing/several_humidity_offset_mean.png', bbox_inches = 'tight')

plt.show(block = True)