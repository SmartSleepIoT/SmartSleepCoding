import random
import json
from datetime import datetime, timedelta
import requests
from paho.mqtt import client as mqtt_client
import sys
from util.constants import MIN_STAGE_DURATION, SLEEP_STAGES, TOPIC
from util.functions import str_to_datetime

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
    session = requests.Session()
    user = "admin"
    password = "1234Admin"
    sleepInitialized = False
    start_hour = 0
    REM_INCREASE_FACTOR = 6
    
    """
    Initialize sleep
    """
    def init_sleep(self):
        self.sleepInitialized = True
        self.time_slept = 0
        self.rem_number = 0
        self.total_time_elapsed = timedelta(0)
        self.init_sleep_cycle()
    
    """
    Initialize sleep cycle
    """
    def init_sleep_cycle(self):
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
        self.start_cycle_time = self.start_hour + self.total_time_elapsed
        self.cycle_time_elapsed = timedelta(0)

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


    def on_stage_light(self,current_heartbeat):
        self.heartbeats.append(current_heartbeat)
        stage_time = self.cycle_time_elapsed.seconds // 60
        if stage_time > MIN_STAGE_DURATION['LIGHT'] and len(self.heartbeats) - 1 and current_heartbeat <= self.heartbeats[len(self.heartbeats) - 2]:
            self.earlyDropStopping += 1
            
            if self.earlyDropStopping == self.patience:
                current_time = self.start_hour + self.total_time_elapsed
                response = self.session.post(f"http://127.0.0.1:5000/activity/sleep_stage?stage={SLEEP_STAGES['DEEP']}&time={str(current_time)}")
                if response.status_code  == 200:
                        print("We succesfully changed the stage!")
                self.SLEEP_DURATION['LIGHT'] = stage_time
                self.stage = SLEEP_STAGES['DEEP']
                self.earlyDropStopping = 0
                self.heartbeats = []
                    
    def on_stage_deep(self, current_hearbeat):
        stage_time = self.cycle_time_elapsed.seconds // 60 - self.SLEEP_DURATION['LIGHT']
        if stage_time > MIN_STAGE_DURATION['DEEP']:
            self.heartbeats.append(current_hearbeat)
            if len(self.heartbeats) - 1 and self.heartbeats[len(self.heartbeats) - 2] < current_hearbeat:
                self.earlyIncreaseStopping += 1
                if self.earlyIncreaseStopping == self.patience:
                    # TO DO: we also have to check the breathing rate is increasing
                    self.stage = SLEEP_STAGES['REM']
                    current_time = self.start_hour + self.total_time_elapsed
                    response = self.session.post(f"http://127.0.0.1:5000/activity/sleep_stage?stage={SLEEP_STAGES['REM']}&time={str(current_time)}")
                    if response.status_code  == 200:
                        print("We succesfully changed the stage!")
                   
                    self.SLEEP_DURATION['DEEP'] = stage_time
                    print("DEEP duration: " + str(self.SLEEP_DURATION['DEEP']))
                    
                    self.earlyIncreaseStopping = 0
                    self.heartbeats = []
    
    def on_stage_rem(self, current_heartbeat):
        # TO DO: we have to check the breathing rate is decreasing
        self.heartbeats.append(current_heartbeat)
        stage_time =  self.cycle_time_elapsed.seconds // 60 - self.SLEEP_DURATION['DEEP'] - self.SLEEP_DURATION['LIGHT'] 
        if stage_time > MIN_STAGE_DURATION['REM'] + self.rem_number * self.REM_INCREASE_FACTOR and len(self.heartbeats) - 2 >= 0  \
            and current_heartbeat >= self.heartbeats[len(self.heartbeats) - 2]:
                
            self.earlyDropStopping += 1
            print("Early dropping increased!")
            if self.earlyDropStopping == self.rem_patience:
                current_time = self.start_hour + self.total_time_elapsed
                response = self.session.post(f"http://127.0.0.1:5000/activity/sleep_stage?stage={SLEEP_STAGES['LIGHT']}&time={str(current_time)}")
                if response.status_code  == 200:
                        print("We succesfully changed the stage!")
                self.init_sleep_cycle()
                self.rem_number += 1
                self.earlyDropStopping = 0
                self.heartbeats = []

    def handle_connection(self, client: mqtt_client):
        def on_message(client, userdata, msg):
            if msg.topic == TOPIC['HEARTRATE'] and not self.sleepInitialized:
                current_time = json.loads(msg.payload)['time']
                self.start_hour = str_to_datetime(json.loads(msg.payload)['time'])
                self.init_sleep()
                response = self.session.post(f"http://127.0.0.1:5000/activity/sleep_stage?stage={SLEEP_STAGES['LIGHT']}&time={str(current_time)}")
                if response.status_code  == 200:
                        print("We succesfully set the initial stage!")
    
            if msg.topic == TOPIC['HEARTRATE'] and self.sleepInitialized:
                # we get the time elapsed and hearbeat as the next decision of changing stages depends on them
                current_time = str_to_datetime(json.loads(msg.payload)['time'])
                current_heartbeat = json.loads(msg.payload)['heartrate']    
                self.total_time_elapsed = current_time - self.start_hour
                self.cycle_time_elapsed = current_time - self.start_cycle_time
                
                print("Time slept: " + str(self.total_time_elapsed) + " Stage: " + self.stage) 
                # we call a handler based on the current stage
                if self.stage == SLEEP_STAGES['LIGHT']:
                   self.on_stage_light(current_heartbeat)
                elif self.stage == SLEEP_STAGES['DEEP']:
                   self.on_stage_deep(current_heartbeat)
                elif self.stage == SLEEP_STAGES['REM']:
                   self.on_stage_rem(current_heartbeat)
                
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
