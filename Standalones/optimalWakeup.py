import random
import json
from datetime import datetime, timedelta
import requests
from paho.mqtt import client as mqtt_client
import sys
from SmartSleep.wakeUpUser import WakeUpScheduler
from util.constants import SLEEP_STAGES
from util.functions import str_to_datetime

class OptimalWakupScheduler:
    broker = 'broker.emqx.io'
    port = 1883
    # generate client ID with pub prefix randomly
    client_id = f'python-mqtt-{random.randint(0, 100)}'
    username = 'emqx'
    password = 'public'
    start = 0
    end = 0
    scores = []
    session = requests.Session()
    admin_user = "admin"
    admin_password = "1234Admin"
    decrease_limit = 3
    requestOptimal = False
    waking_start_hour = 0
    waking_end_hour = 0
    start_to_sleep_hour  =  0
    waking_mode = 'LS'

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

    def trigger_wakeup(self,current_time, client: mqtt_client):
        print("Wake up!")
        time_slept = current_time - self.start_to_sleep_hour
        msg = {'message': "Wake up the user",
               'waking up mode': self.waking_mode,
               'time': str(current_time)}, 200
        client.publish(json.dumps(msg), "SmartSleep/WakeUp")
        total_sec = time_slept.total_seconds()
        h = int(total_sec // 3600)
        min = int((total_sec % 3600) // 60)
        r = self.session.post(f"http://127.0.0.1:5000/config/time_slept?time={h}:{min}")
        if r.status_code == 200:
            msg = {'message': f"User slept for {h} hours and {min} minutes"}, 200
            client.publish(json.dumps(msg), "SmartSleep/WakeUp")

    def handleConnection(self, client: mqtt_client):
        def on_message(client, userdata, msg):
            global start, end, db
            if msg.topic == "SmartSleep/Heartrate":
                time = str_to_datetime(json.loads(msg.payload)['time'])
                print(self.waking_start_hour, time, self.waking_end_hour)
                if self.requestOptimal and self.waking_start_hour <= time <= self.waking_end_hour:
                    print("Taking heartbeats into consideration...")
                    response = self.session.get("http://127.0.0.1:5000/activity/sleep_stage")
                    sleep_stage = response.json()["data"]['stage']
                    stage_start_time = str_to_datetime(response.json()["data"]['time'])
                    # We could also compare the time slept with the miminum required sleeping time by age - when #59 is integrated
                    # response = self.session.get("http://127.0.0.1:5000/config/start_to_sleep")
                    # start_sleeping_time = str_to_datetime(json.loads(response.json())['timestamp'])
                    
                    wakeUp = False
                    if sleep_stage == SLEEP_STAGES['LIGHT'] and time - stage_start_time > timedelta(hours = 0, minutes = 15):
                        wakeUp = True
                    if time >= self.waking_end_hour - timedelta(hours = 0, minutes = 1):
                        wakeUp = True    
                    if wakeUp:
                        self.trigger_wakeup(time,client)
                        self.requestOptimal = False
                    
            elif msg.topic == "SmartSleep/OptimalWakeup":
                self.waking_start_hour = str_to_datetime(json.loads(msg.payload)['start'])
                self.waking_end_hour = str_to_datetime(json.loads(msg.payload)['end'])
                self.start_to_sleep_hour = str_to_datetime(json.loads(msg.payload)['start_to_sleep'])
                self.waking_mode = json.loads(msg.payload)['mode']
                self.requestOptimal = True
                print("Optimal wakeup request was sent.")
                
        client.subscribe("SmartSleep/Heartrate")
        client.subscribe("SmartSleep/OptimalWakeup")
        client.on_message = on_message

    def run(self):
        self.session.post(f"http://127.0.0.1:5000/auth/register?username={self.admin_user}&password={self.admin_password}")
        self.session.post(f"http://127.0.0.1:5000/auth/login?username={self.admin_user}&password={self.admin_password}")
        client = self.connect_mqtt()
        self.handleConnection(client)
        client.loop_forever()

if __name__ == '__main__':
    try:
        optimal_wakeup_scheduler = OptimalWakupScheduler()
        optimal_wakeup_scheduler.run()
    except KeyboardInterrupt:
        print('interrupted')
        sys.exit(0)
