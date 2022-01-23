cd SmartSleep
flask init-db
START %COMSPEC% /k flask run
cd ..\\Standalones
START %COMSPEC% /k python subMQTT.py
START %COMSPEC% /k python snoring.py
START %COMSPEC% /k python breathing.py
START %COMSPEC% /k python sleepStages.py
START %COMSPEC% /k python readSoundSensorData.py
START %COMSPEC% /k python readTemperatureSensorData.py
START %COMSPEC% /k python readHeartrateSensorData.py
EXIT
