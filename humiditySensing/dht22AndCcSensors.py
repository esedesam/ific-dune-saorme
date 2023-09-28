import numpy as np
import pandas as ps
import matplotlib.pyplot as plt
import xlrd, datetime, pytz

# Funciones de Jordi
def downsample_data(df, bin=1, timeCol = 'timestamp'):
    df[timeCol] = df[timeCol].apply(lambda x: np.round(x/bin, 0))
    downsampled = []
    unique_times = df[timeCol].unique()
    # progress_bar = tqdm(total=len(unique_times), desc="Downsampling data")
    for time in unique_times:
        chunk = df.loc[df[timeCol] == time]
        row = {}
        for col in chunk:
            if col == "Date" or col=="Time" or col=="Datetime" or col == "PolMask":
                continue
            if col == timeCol:
                row[col] = time
            if col != timeCol:
                row[col] = np.mean(chunk[col])
                row[col+"_err"] = np.std(chunk[col])
        downsampled.append(row)
        # progress_bar.update(1)
    # progress_bar.close()
    downsampled = ps.DataFrame(downsampled)
    return downsampled

def time_to_seconds(timestamp):
    try:
        date, time = timestamp.split("-")
        month, day, year = [int(x) for x in date.split("/")]
        h, m, s = [int(x) for x in time.split(":")]
        epoch = datetime.datetime(year, day, month, h, m, s).timestamp()
    except:
        try:
            start = datetime.datetime(1900, 1, 1, 0, 0, 0, 0, pytz.UTC)  # interrogator time epoch (time zero)
            time_arr = start + timestamp/1e6 * datetime.timedelta(milliseconds=1)
            epoch = time_arr.timestamp()
        except:
            date, time = timestamp.split(" ")
            year, month, day = [int(x) for x in date.split("-")]
            h, m, s = [int(x) for x in time.split(":")]
            epoch = datetime.datetime(year, month, day, h, m, s).timestamp()
    return epoch

# Set-up
dates = {'sensorFuera': '20230913', 'sensorDentro': '20230914'}
variableForPlateaus = 'temp' # 'temp' | 'hum'
gradientThreshold = 1e-4
minPlateauPoints = 100

dht22Data = {}
ccData = {}
for key, date in dates.items():
    # Load DHT22 sensor data
    fileName = 'D:/ific-dune-saorme/humiditySensing/' + date + '_dht22.csv'
    sensor = ps.read_csv(fileName, header = 0)
    sensor['humidity_dht22'] = ps.to_numeric(sensor['humidity_dht22'], errors='coerce').dropna()
    sensor['temperature_dht22'] = ps.to_numeric(sensor['temperature_dht22'], errors='coerce').dropna()

    # Load climatic chamber data
    fileName = 'D:/ific-dune-saorme/humiditySensing/' + date + '_cc.csv'
    climChamber = ps.read_csv(fileName, header = 0, sep = ';', decimal = ',')

    # Preprocessing
    colNames = climChamber.columns.values
    colNames[0] = 'timestamp'
    climChamber.columns = colNames # climChamber.rename(columns = {'Fecha/Hora': 'timestamp'})
    climChamber['timestamp'] = climChamber['timestamp'].apply(lambda x: str(xlrd.xldate.xldate_as_datetime(x, 0).date()) + " " + str(xlrd.xldate.xldate_as_datetime(x, 0).time()).split(".")[0])
    climChamber['timestamp'] = climChamber['timestamp'].apply(time_to_seconds)

    # Delete DHT22 pre-run and after-run data
    sensor = sensor[sensor.timestamp >= min(climChamber['timestamp'])]
    sensor = sensor[sensor.timestamp <= max(climChamber['timestamp'])]

    # Downsampling to have same time interval
    sensor = downsample_data(sensor, bin = 10)
    climChamber = downsample_data(climChamber, bin = 10)

    auxLen = len(sensor['timestamp'].unique())
    print(f'Lenght of DHT22 after downsampling: {auxLen}')
    auxLen = len(climChamber['timestamp'].unique())
    print(f'Lenght of climatic chamber after downsampling: {auxLen}')

    dht22Data[key] = sensor
    ccData[key] = climChamber

# Plot humidity and temperature
fig = plt.figure()
gs = fig.add_gridspec(2, hspace = 0)
(tempPlot, humPlot) = gs.subplots(sharex = 'col')
for key in dht22Data.keys():
    tempPlot.plot(dht22Data[key]['timestamp'] - ccData[key]['timestamp'][0], dht22Data[key]['temperature_dht22'], '-', label = f'{key}_DHT22')
    tempPlot.plot(ccData[key]['timestamp'] - ccData[key]['timestamp'][0], ccData[key]['camara_climatica.10-200-1-1-502-ID001-2604.LP1_VIEW.Main.wSP'], '--', label = f'{key}_CC (target)')
    tempPlot.plot(ccData[key]['timestamp'] - ccData[key]['timestamp'][0], ccData[key]['camara_climatica.10-200-1-1-502-ID001-2604.LP1_VIEW.Main.PV'], '-.', label = f'{key}_CC')
tempPlot.set(xlabel = 'time / s', ylabel = 'temperature / ºC')
tempPlot.legend(bbox_to_anchor=(1.02, 0.7))
for key in dht22Data.keys():
    humPlot.plot(dht22Data[key]['timestamp'] - ccData[key]['timestamp'][0], dht22Data[key]['humidity_dht22'], '-', label = f'{key}_DHT22')
    humPlot.plot(ccData[key]['timestamp'] - ccData[key]['timestamp'][0], ccData[key]['camara_climatica.10-200-1-1-502-ID001-2604.LP2_VIEW.Main.wSP'], '--', label = f'{key}_CC (target)')
    humPlot.plot(ccData[key]['timestamp'] - ccData[key]['timestamp'][0], ccData[key]['camara_climatica.10-200-1-1-502-ID001-2604.LP2_VIEW.Main.PV'], '-.', label = f'{key}_CC')
humPlot.set(xlabel = 'time / s', ylabel = 'humidity / %')
humPlot.legend(bbox_to_anchor=(1.02, 0.7))

plt.savefig('D:/ific-dune-saorme/humiditySensing/' + date + '_sensors_data.pngw', bbox_inches = 'tight')

plt.show(block = True)

if False:
    # Plateaus detection
    if variableForPlateaus == 'temp':
        varName = 'camara_climatica.10-200-1-1-502-ID001-2604.LP1_VIEW.Main.wSP'
        yLabel = 'temperature / ºC'
    elif variableForPlateaus == 'hum':
        varName = 'camara_climatica.10-200-1-1-502-ID001-2604.LP2_VIEW.Main.wSP'
        yLabel = 'humidity / %'
    else:
        raise Exception('Jordi explotador.')
    dataDiff = np.gradient(climChamber[varName].values)
    dataDiff[0] = 0

    plateauPositions = [] # Indexs of plateaus points
    for idx in range(len(dataDiff)):
        if abs(round(dataDiff[idx], 3)) < gradientThreshold:
            plateauPositions.append(idx)
            
    plateauInit = [] # Indexs of plateaus init
    plateauEnd = [] # Indexs of plateaus end
    idx = 0
    while (idx < len(plateauPositions) - 1):
        isPlateau = False
        plateauPoints = 0
        while (idx < len(plateauPositions) - 1) and (plateauPositions[idx + 1] == plateauPositions[idx] + 1):
            if not isPlateau:
                initIdx = idx
            plateauPoints = plateauPoints + 1
            isPlateau = True
            idx = idx + 1
        if isPlateau and plateauPoints > minPlateauPoints:
            if (date == '20230704' and variableForPlateaus == 'hum') and (len(plateauInit) == 3 or len(plateauInit) == 7): # correccion para los plateaus superiores e inferior(T cambia a mitad)
                midIdx = int((initIdx + idx) / 2)
                newInitIdx = int((initIdx + midIdx) / 2)
                plateauInit.append(plateauPositions[newInitIdx])
                plateauEnd.append(plateauPositions[midIdx])
                newMidInitIdx = int((midIdx + idx) / 2)
                plateauInit.append(plateauPositions[newMidInitIdx])
                plateauEnd.append(plateauPositions[idx])
            else:
                newInitIdx = int((initIdx + idx) / 2)
                plateauInit.append(plateauPositions[newInitIdx])
                plateauEnd.append(plateauPositions[idx])
                
        idx = idx + 1

    for plateauIdx in range(len(plateauInit)):

        posInit = plateauInit[plateauIdx]
        posEnd = plateauEnd[plateauIdx]
        print(f'No. of points of plateau {plateauIdx}: {posEnd - posInit}')

    plt.figure()
    plt.plot(xCc, climChamber[varName], '-')
    for pos in plateauPositions:
        plt.plot(xCc[pos], climChamber[varName][pos], '.', color = 'yellow', label = 'plateau')
    for pos in plateauInit:
        plt.plot(xCc[pos], climChamber[varName][pos], 'x', color = 'green', label = 'Start of plateau')
    for pos in plateauEnd:
        plt.plot(xCc[pos], climChamber[varName][pos], 'x', color = 'red', label = 'End of plateau')
    plt.xlabel('time / s')
    plt.ylabel(yLabel)

    plt.savefig('D:/ific-dune-saorme/humiditySensing/' + date + '_humidity_plateaus_' + variableForPlateaus + '.png', bbox_inches = 'tight')

    # Hum DHT22 vs CC
    sensorValue = []
    sensorError = []
    ccValue = []
    ccError = []
    for plateauIdx in range(len(plateauInit)):
        
        posInit = plateauInit[plateauIdx]
        posEnd = plateauEnd[plateauIdx]

        dht11Data = dht22Data['humidity_dht22'][posInit : posEnd].values
        sensorValue.append(np.mean(dht11Data))
        sensorError.append(np.std(dht11Data))

        ccData = climChamber['camara_climatica.10-200-1-1-502-ID001-2604.LP2_VIEW.Main.PV'][posInit : posEnd].values
        ccValue.append(np.mean(ccData))
        ccError.append(np.std(ccData))

    plt.figure()
    if date == '20230704' and variableForPlateaus == 'hum':
        plt.errorbar(ccValue[0:4], sensorValue[0:4], sensorError[0:4], ccError[0:4], '.', capsize = 5, label = 'T = 30 ºC')
        plt.errorbar(ccValue[4:8], sensorValue[4:8], sensorError[4:8], ccError[4:8], '.', capsize = 5, label = 'T = 20 ºC')
        plt.errorbar(ccValue[8:12], sensorValue[8:12], sensorError[8:12], ccError[8:12], '.', capsize = 5, label = 'T = 10 ºC')
        plt.legend()
    elif date == '20230706' and variableForPlateaus == 'temp':
        for idx in range(len(ccValue)):
            plt.errorbar(ccValue[idx], sensorValue[idx], sensorError[idx], ccError[idx], '.', capsize = 5)
        plt.legend(['T = 0 ºC', 'T = -20 ºC', 'T = -30 ºC', 'T = -40 ºC', 'T = -50 ºC', 'T = -60 ºC', 'T = -40 ºC', 'T = -20 ºC', 'T = -10 ºC', 'T = 0 ºC', 'T = 20 ºC'])
    else:
        plt.errorbar(ccValue, sensorValue, sensorError, ccError, '.', label = 'All points')

    plt.xlabel('Climatic chamber humidity / %')
    plt.ylabel('DHT11 humidity / %')
    defLeft, defRight = plt.xlim()
    plt.xlim((min([defLeft, 0]), max([defRight, 100])))
    defLeft, defRight = plt.ylim()
    plt.ylim((min([defLeft, 0]), max([defRight, 100])))

    plt.savefig('D:/ific-dune-saorme/humiditySensing/' + date + '_humidity_comparison.png', bbox_inches = 'tight')

    # Offset
    offset = []
    offsetValue = []
    offsetError = []

    for plateauIdx in range(len(plateauInit)):

        posInit = plateauInit[plateauIdx]
        posEnd = plateauEnd[plateauIdx]

        dht11Data = dht22Data['humidity_dht22'][posInit : posEnd].values
        ccData = climChamber['camara_climatica.10-200-1-1-502-ID001-2604.LP2_VIEW.Main.PV'][posInit : posEnd].values

        if len(dht11Data) == len(ccData):
            offset = ccData - dht11Data
            offsetValue.append(np.mean(offset))
            offsetError.append(np.std(offset))
        else:
            print(f'Plateau no. {plateauIdx} mal.\n')
            
    plt.figure()
    if date == '20230704' and variableForPlateaus == 'hum':
        vsTargetHum = False
        if vsTargetHum:
            humArray = [10, 40, 70, 100]
            humArrayInv = [100, 70, 40, 10]
            plt.errorbar(humArray, offsetValue[0:4], offsetError[0:4], None, '.', capsize = 5, label = 'T = 30 ºC')
            plt.errorbar(humArrayInv, offsetValue[4:8], offsetError[4:8], None, '.', capsize = 5, label = 'T = 20 ºC')
            plt.errorbar(humArray, offsetValue[8:12], offsetError[8:12], None, '.', capsize = 5, label = 'T = 10 ºC')
            plt.xlabel('Target humidity / %')
        else:
            plt.errorbar(ccValue[0:4], offsetValue[0:4], offsetError[0:4], ccError[0:4], '.', capsize = 5, label = 'T = 30 ºC')
            plt.errorbar(ccValue[4:8], offsetValue[4:8], offsetError[4:8], ccError[4:8], '.', capsize = 5, label = 'T = 20 ºC')
            plt.errorbar(ccValue[8:12], offsetValue[8:12], offsetError[8:12], ccError[8:12], '.', capsize = 5, label = 'T = 10 ºC')
            plt.xlabel('Climatic chamber humidity / %')

        plt.legend()
    elif date == '20230706' and variableForPlateaus == 'temp':
        for idx in range(len(ccValue)):
            plt.errorbar(ccValue[idx], offsetValue[idx], offsetError[idx], ccError[idx], '.', capsize = 5)
        plt.legend(['T = 0 ºC', 'T = -20 ºC', 'T = -30 ºC', 'T = -40 ºC', 'T = -50 ºC', 'T = -60 ºC', 'T = -40 ºC', 'T = -20 ºC', 'T = -10 ºC', 'T = 0 ºC', 'T = 20 ºC'])
        plt.xlabel('Climatic chamber humidity / %')
    else:
        plt.errorbar(ccValue, offsetValue, offsetError, ccError, '.', label = 'All points')
        plt.legend()
        plt.xlabel('Climatic chamber humidity / %')

    plt.ylabel('humidity offset (CC - DHT11) / %')
    defLeft, defRight = plt.xlim()
    plt.xlim((min([defLeft, 0]), max([defRight, 100])))

    plt.savefig('D:/ific-dune-saorme/humiditySensing/' + date + '_humidity_offset.png', bbox_inches = 'tight')

    # Save data for plotting with other runs
    with open('D:/ific-dune-saorme/humiditySensing/' + date + '_offsetValue.txt', 'w') as f:
        f.write(str(offsetValue) + '\n')

    with open('D:/ific-dune-saorme/humiditySensing/' + date + '_offsetError.txt', 'w') as f:
        f.write(str(offsetError) + '\n')

    with open('D:/ific-dune-saorme/humiditySensing/' + date + '_ccValue.txt', 'w') as f:
        f.write(str(ccValue) + '\n')

    with open('D:/ific-dune-saorme/humiditySensing/' + date + '_ccError.txt', 'w') as f:
        f.write(str(ccError) + '\n')