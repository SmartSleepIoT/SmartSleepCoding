from pathlib import Path
import sys
import time
import requests


class ReadSensorsData:
    def __init__(self, temperaturefilename):
        self.path = str(Path("../").resolve()) + "\\SensorsData\\"
        self.temp_end_point = "http://127.0.0.1:5000/config/current_temp?"
        self.sleep_end_point = "http://127.0.0.1:5000/config/start_to_sleep?"

        self.user = "admin"
        self.password = "1234Admin"

        self.session = requests.Session()

        try:
            self.temp = open(self.path + temperaturefilename, "r")
            # self.heartb = open(self.path + heartbeatfilename, "r")

        except FileNotFoundError as err:
            print(err)
            print("solve file names before feeding sensor data")
            sys.exit(0)

    def register_login(self):
        self.session.post(f"http://127.0.0.1:5000/auth/register?username={self.user}&password={self.password}")
        self.session.post(f"http://127.0.0.1:5000/auth/login?username={self.user}&password={self.password}")

    def post_temperature_data(self):
        fails = 0
        totals = 0
        print("Posting temperature sensor data to endpoint")
        for line in self.temp:
            if line != "\n":
                print(line.replace("\n", "").replace(" ", "").split("C"))
                totals += 1
                temp = line.replace("\n", "").replace(" ", "").split("C")[0]
                delay = line.replace("\n", "").replace(" ", "").split("C")[1]
                r = self.session.post(self.temp_end_point + f"sensor={temp}")
                if r.status_code != 200:
                    fails += 1
                time.sleep(float(delay))

        print(f"Posted data: total {totals} sent; {fails} fails")


# files have the following format: on each line is the sensor data/unit  time (between it and the next sensor detected)
data = ReadSensorsData("TemperatureSensorData.txt")
data.register_login()
data.post_temperature_data()
