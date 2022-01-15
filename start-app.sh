cd SmartSleep
flask init-db
START flask run
cd ../Standalones
START python subMQTT.py
START python snoring.py
START python breathing.py
START python temperature.py
START python readSoundSensorData.py
START python readTemperatureSensorData.py
EXIT
