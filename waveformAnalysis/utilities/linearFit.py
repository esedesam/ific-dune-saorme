import matplotlib, lmfit
import matplotlib.pyplot as plt
from lmfit.models import LinearModel

# Signal trigger
# x = [-2.1664, -1.7535, -1.5824, -1.4969, -1.4359, -1.3867, -1.3469, -1.3078]
# y = [2.24, 2.153, 2.116, 2.096, 2.0766, 2.063, 2.053, 2.046]
# x2 = -3.8074
# y2 = 1.65245853

# Random trigger
x = [-5.0754, -4.4703, -4.0750, -3.8074, -3.5953, -3.4125, -3.2297, -3.0313]
y = [1.84913543, 1.73510885, 1.67744292, 1.63973745, 1.61343897, 1.57905680, 1.55199385, 1.54175496]

model = LinearModel()
params = model.make_params(m = 1, b = 0)
result = model.fit(y, params, x = x)
report = result.fit_report()
print(report)
plt.plot(x, y, '.', label = 'Random trigger')
plt.plot(x, result.best_fit, '-', label = 'Linear fit')
# plt.plot(x2, y2, 'x', label = 'Random trigger')
plt.xlabel('Median of baselines / mV')
plt.ylabel('G / ADC/e-')
plt.legend()
plt.savefig('./waveformAnalysis/linearFit.png', bbox_inches = 'tight')
plt.show(block = True)