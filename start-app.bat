cd SmartSleep
flask init-db
START %COMSPEC% /k flask run
cd ..\\Standalones
START %COMSPEC% /k python subMQTT.py
START %COMSPEC% /k python snoring.py
START %COMSPEC% /k python readSensorData.py
EXIT