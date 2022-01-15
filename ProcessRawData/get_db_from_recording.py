import numpy as np
import librosa as lr
import math

# data comes from https://www.youtube.com/watch?v=RHFfhmE8sxg
y, sr = lr.load("The Dreaded Sound of Sleep Apnea.wav")
print(y)
second = []
for s in range(0,len(y),sr//7):
    value = np.abs(y[s:s+sr]).max()
    if value != 0.0:
        second.append(abs(20 * math.log10(value)))

second = second + second + second

sound_sensor = open("../SensorsData/SoundSensorData.txt", "w")

for value in second:
    sound_sensor.write(f"{value}db 1\n")