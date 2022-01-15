import random
import json
from datetime import datetime, timedelta
import requests
from paho.mqtt import client as mqtt_client
import sys
from util.constants import SLEEP_STAGES, TOPIC
from util.functions import datetime_to_pair
from SmartSleep.secrets import ADMIN_CREDENTIALS

class SleepStagesManager:
    broker = 'broker.emqx.io'
    port = 1883
    # generate client ID with pub prefix randomly
    client_id = f'python-mqtt-{random.randint(0, 100)}'
    username = 'emqx'
    password = 'public'
    patience = 3
    rem_patience = 2
    nr_of_cycles = 0
    start_hour = 0
    time_slept = 0
    session = requests.Session()
    user = "admin"
    password = "1234Admin"
    
    def init_sleep_cycle(self, time):
        self.nr_of_cycles += 1 
        self.stage = SLEEP_STAGES['LIGHT']
        self.SLEEP_DURATION = {
            'LIGHT': 0,
            'DEEP': 0,
            'REM': 0
        }
        self.heartbeats = []
        self.earlyDropStopping = 0
        self.earlyIncreaseStopping = 0
        self.start_cycle_time = time

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


    def on_stage_light(self, minutes, current_heartbeat):
        self.heartbeats.append(current_heartbeat)
        if minutes > 5 and len(self.heartbeats) - 1 and current_heartbeat <= self.heartbeats[len(self.heartbeats) - 2]:
            self.earlyDropStopping += 1
            
            if self.earlyDropStopping == self.patience:
                response = self.session.post(f"http://127.0.0.1:5000/config/sleep_stage?stage={SLEEP_STAGES['DEEP']}")
                if response.status_code  == 200:
                        print("We succesfully changed the stage!")
                self.SLEEP_DURATION['LIGHT'] = minutes
                self.stage = SLEEP_STAGES['DEEP']
                self.earlyDropStopping = 0
                self.heartbeats = []
                    
    def on_stage_deep(self, cycle_time_elapsed, current_hearbeat):
        if cycle_time_elapsed.seconds // 60 > 80:
            self.heartbeats.append(current_hearbeat)
            if len(self.heartbeats) - 1 and self.heartbeats[len(self.heartbeats) - 2] < current_hearbeat:
                self.earlyIncreaseStopping += 1
                if self.earlyIncreaseStopping == self.patience:
                    # TO DO: we also have to check the breathing rate is increasing
                    self.stage = SLEEP_STAGES['REM']
                    response = self.session.post(f"http://127.0.0.1:5000/config/sleep_stage?stage={self.stage}")
                    if response.status_code  == 200:
                        print("We succesfully changed the stage!")
                   
                    self.SLEEP_DURATION['DEEP'] = cycle_time_elapsed.seconds // 60 - self.SLEEP_DURATION['LIGHT']
                    print("DEEP duration: " + str(self.SLEEP_DURATION['DEEP']))
                    
                    self.earlyIncreaseStopping = 0
                    self.heartbeats = []
    
    def on_stage_rem(self, cycle_time_elapsed, restart_time, current_heartbeat):
        # TO DO: we have to check the breathing rate is decreasing
        print("A trecut" + str(cycle_time_elapsed.seconds // 60))
        self.heartbeats.append(current_heartbeat)
        stage_time =  cycle_time_elapsed.seconds // 60 - self.SLEEP_DURATION['DEEP'] - self.SLEEP_DURATION['LIGHT'] 
        if stage_time > 10 and len(self.heartbeats) - 2 >= 0 and current_heartbeat >= self.heartbeats[len(self.heartbeats) - 2]:
            self.earlyDropStopping += 1
            if self.earlyDropStopping == self.rem_patience:
                response = self.session.post(f"http://127.0.0.1:5000/config/sleep_stage?stage={SLEEP_STAGES['LIGHT']}")
                if response.status_code  == 200:
                        print("We succesfully changed the stage!")
                self.init_sleep_cycle(restart_time)
                self.earlyDropStopping = 0
                self.heartbeats = []

    def handle_connection(self, client: mqtt_client):
        def on_message(client, userdata, msg):
            if msg.topic == TOPIC['START_TO_SLEEP']:
                self.start_hour = datetime.strptime(json.loads(msg.payload)['time'], "%H:%M:%S")
                self.init_sleep_cycle(self.start_hour)
                
            if msg.topic == TOPIC['HEARTRATE']:
                # we get the time elapsed and hearbeat as the next decision of changing stages depends on them
                current_time = json.loads(msg.payload)['time']
                current_heartbeat = json.loads(msg.payload)['heartrate']
                
                hours, minutes = datetime_to_pair(current_time, self.start_hour)
                total_time_elapsed = timedelta(hours = hours, minutes = minutes)
                hours, minutes = datetime_to_pair(current_time, self.start_cycle_time)
                cycle_time_elapsed = timedelta(hours = hours, minutes = minutes)
               
                
                print("Time slept: " + str(total_time_elapsed) + " Stage: " + self.stage)
                
                # we call a handler based on the current stage
                if self.stage == SLEEP_STAGES['LIGHT']:
                   self.on_stage_light(minutes, current_heartbeat)
                elif self.stage == SLEEP_STAGES['DEEP']:
                   self.on_stage_deep(cycle_time_elapsed, current_heartbeat)
                else:
                   self.on_stage_rem(cycle_time_elapsed, datetime.strptime(current_time, "%H:%M:%S"), current_heartbeat)
                
        client.subscribe(TOPIC['START_TO_SLEEP'])
        client.subscribe(TOPIC['HEARTRATE'])
        client.on_message = on_message

    def run(self):
        self.session.post(f"http://127.0.0.1:5000/auth/register?username={self.user}&password={self.password}")
        self.session.post(f"http://127.0.0.1:5000/auth/login?username={self.user}&password={self.password}")
        client = self.connect_mqtt()
        self.handle_connection(client)
        client.loop_forever()

if __name__ == '__main__':
    try:
        sleep_stages_manager = SleepStagesManager()
        sleep_stages_manager.run()
    except KeyboardInterrupt:
        print('interrupted')
        sys.exit(0)
