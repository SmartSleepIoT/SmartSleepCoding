cd SmartSleep
flask init-db
START %COMSPEC% /k flask run
cd ..\\Standalones
START %COMSPEC% /k py subMQTT.py
START %COMSPEC% /k py snoring.py
START %COMSPEC% /k py sleepStages.py
START %COMSPEC% /k py readSensorData.py
EXIT