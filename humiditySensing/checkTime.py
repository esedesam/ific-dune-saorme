import pandas as ps
import matplotlib.pyplot as plt

date = '20230913'
fileName = 'D:/ific-dune-saorme/humiditySensing/' + date + '_dht22.csv'
dht22Data1 = ps.read_csv(fileName, header = 0, sep=',')
dht22Data1['humidity_dht22'] = ps.to_numeric(dht22Data1['humidity_dht22'], errors='coerce').dropna()

date = '20230914'
fileName = 'D:/ific-dune-saorme/humiditySensing/' + date + '_dht22.csv'
dht22Data2 = ps.read_csv(fileName, header = 0, sep=',')
dht22Data2['humidity_dht22'] = ps.to_numeric(dht22Data2['humidity_dht22'], errors='coerce').dropna()

plt.plot(dht22Data1['timestamp'] - dht22Data1['timestamp'][0], dht22Data1['humidity_dht22'])
plt.plot(dht22Data2['timestamp'] - dht22Data2['timestamp'][0], dht22Data2['humidity_dht22'])

plt.show(block = True)

