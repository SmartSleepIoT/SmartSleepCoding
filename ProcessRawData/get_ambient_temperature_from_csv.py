import pandas as pd
# dataset comes from https://github.com/IoTsec/Room-Climate-Datasets
data = pd.read_csv("room_climate-location_A-measurement01.csv", usecols = ["Temp"])
print(data)

TemperatureSensorData = open("../SensorsData/TemperatureSensorData.txt", "w")
for row in data.Temp:
    print(row)
    # temperature is measured every 15 mins
    TemperatureSensorData.write(f"{int(row)}C {15*60}\n")