cd SmartSleep
flask init-db
START flask run
cd ../Standalones
START python subMQTT.py
START python snoring.py
START python readSensorData.py
EXIT
