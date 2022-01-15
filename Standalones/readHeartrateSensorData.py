from pathlib import Path
import sys
import time
import requests
import csv
import random
from paho.mqtt import client as mqtt_client
from util.constants import TOPIC

class ReadSensorsData:
    broker = 'broker.emqx.io'
    port = 1883
    # generate client ID with pub prefix randomly
    client_id = f'python-mqtt-{random.randint(0, 100)}'
    username = 'emqx'
    password = 'public'
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
    
    def connect_mqtt(self) -> mqtt_client:
        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                print("Connected to MQTT Broker!")
            else:
                print("Failed to connect, return code %d\n", rc)

        client = mqtt_client.Client(self.client_id)
        client.username_pw_set(self.username, self.password)
        client.on_connect = on_connect
        client.connect(self.broker, self.port)
        return client
    
    def post_heartbeat_data(self):
        fails = 0
        totals = 0
        delay = 1 # for development only
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
        
    def handle_connection(self, client: mqtt_client):
        def on_message(client, userdata, msg):
                self.post_heartbeat_data()
    
        client.subscribe(TOPIC['START_TO_SLEEP'])
        client.on_message = on_message
        
    def run(self):
        self.register_login()
        client = self.connect_mqtt()
        self.handle_connection(client)
        client.loop_forever()
        
sensor = ReadSensorsData("Heartrate.csv")
sensor.run()