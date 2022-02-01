from pathlib import Path
import sys
import time
import requests
import csv

class ReadSensorsData:
    def __init__(self, heartbeatfilename):
        self.path = str(Path("../").resolve()) + "\\SensorsData\\"
        self.heartb_end_point = "http://127.0.0.1:5000/activity/heartrate?"

        self.user = "admin"
        self.password = "1234Admin"

        self.session = requests.Session()

        try:
            self.heartb = open(self.path + heartbeatfilename, "r")

        except FileNotFoundError as err:
            print(err)
            print("solve file names before feeding sensor data")
            sys.exit(0)

    def register_login(self):
        self.session.post(f"http://127.0.0.1:5000/auth/register?username={self.user}&password={self.password}")
        self.session.post(f"http://127.0.0.1:5000/auth/login?username={self.user}&password={self.password}")    
    
    def post_heartbeat_data(self):
        fails = 0
        totals = 0
        delay = 1    # for development only
        print("Posting hearbeat sensor data to endpoint")
        csv_reader = csv.DictReader(self.heartb)
        next(csv_reader)
        for line in csv_reader:
           print(line['heartrate'], line['time'])
           if line != "\n":
            totals += 1
            response = self.session.post(self.heartb_end_point + f"heartrate={line['heartrate']}&time={line['time']}")
            if response.status_code != 200:
                fails += 1
            time.sleep(float(delay))
            
        print(f"Posted data: total {totals} sent; {fails} fails")

sensor = ReadSensorsData("Heartrate.csv")
sensor.register_login()
sensor.post_heartbeat_data()
