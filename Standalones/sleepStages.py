import random
import json
from datetime import datetime, timedelta
import requests
from paho.mqtt import client as mqtt_client
import sys
from SmartSleep.configuration import start_to_sleep
from util.constants import SLEEP_STAGES, TOPIC
from util.functions import datetime_to_pair

class SleepStagesManager:
    broker = 'broker.emqx.io'
    port = 1883
    # generate client ID with pub prefix randomly
    client_id = f'python-mqtt-{random.randint(0, 100)}'
    username = 'emqx'
    password = 'public'
    patience = 3
    nr_of_cycles = 0
    start_record_time = 0
    time_slept = 0
    
    def init_sleep_cycle(self, time):
        self.nr_of_cycles += 1 
        self.stage = SLEEP_STAGES['NREM1']
        self.SLEEP_DURATION = {
            'NREM1': 0,
            'NREM2': 20,
            'NREM3': 0,
            'REM': 0
        }
        self.heartbeats = []
        self.earlyDropStopping = 0
        self.earlyIncreaseStopping = 0
        self.start_record_time = time

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


    def on_stage_NREM1(self, minutes, current_heartbeat):
        self.heartbeats.append(current_heartbeat)
        if minutes > 5 and len(self.heartbeats) - 1 and current_heartbeat < self.heartbeats[len(self.heartbeats) - 2]:
            self.earlyDropStopping += 1
            
            if self.earlyDropStopping == self.patience:
                response = requests.post(f"http://127.0.0.1:5000/config/sleep_stage?stage={SLEEP_STAGES['NREM2']}")
                if response.status_code  == 200:
                        print("We succesfully changed the stage!")
                self.SLEEP_DURATION['NREM1'] = minutes
                self.stage = SLEEP_STAGES['NREM2']
                self.earlyDropStopping = 0
                self.heartbeats = []
         
    def on_stage_NREM2(self, time_elapsed):
        if time_elapsed.seconds // 60 - self.SLEEP_DURATION['NREM1'] == 20:
            response = requests.post(f"http://127.0.0.1:5000/config/sleep_stage?stage={SLEEP_STAGES['NREM3']}")
            if response.status_code  == 200:
                    print("We succesfully changed the stage!")
            self.stage = SLEEP_STAGES['NREM3']
            
    def on_stage_NREM3(self, time_elapsed, current_hearbeat):
        if time_elapsed.seconds // 60 > 80:
            self.heartbeats.append(current_hearbeat)
            if len(self.heartbeats) - 1 and self.heartbeats[len(self.heartbeats) - 2] < current_hearbeat:
                self.earlyIncreaseStopping += 1
                if self.earlyIncreaseStopping == self.patience:
                    # TO DO: we also have to check the breathing rate is increasing
                    response = requests.post(f"http://127.0.0.1:5000/config/sleep_stage?stage={SLEEP_STAGES['NREM3']}")
                    if response.status_code  == 200:
                        print("We succesfully changed the stage!")
                    self.stage = SLEEP_STAGES['REM']
                    self.SLEEP_DURATION['NREM3'] = time_elapsed.seconds // 60 - self.SLEEP_DURATION['NREM2']
                    print("NREM3 duration: " + str(self.SLEEP_DURATION['NREM3']))
                    self.earlyIncreaseStopping = 0
                    self.heartbeats = []
    
    def on_stage_REM(self, time_elapsed, restart_time):
        # TO DO: we have to check the breathing rate is decreasing
        print("A trecut" + str(time_elapsed.seconds // 60))
        if time_elapsed.seconds // 60 - self.SLEEP_DURATION['NREM3'] - self.SLEEP_DURATION['NREM2'] - self.SLEEP_DURATION['NREM1'] > 10:
            response = requests.post(f"http://127.0.0.1:5000/config/sleep_stage?stage={SLEEP_STAGES['NREM3']}")
            if response.status_code  == 200:
                    print("We succesfully changed the stage!")
            self.init_sleep_cycle(restart_time)

    def handle_connection(self, client: mqtt_client):
        def on_message(client, userdata, msg):
            if not self.start_record_time: 
                # The condition should be msg.topic == TOPIC['START_TO_SLEEP']: 
                # Workaround until #52 is solved
                self.init_sleep_cycle(datetime.strptime(json.loads(msg.payload)['time'], "%H:%M:%S"))
                
            if msg.topic == TOPIC['HEARTRATE']:
                # we get the time elapsed and hearbeat as the next decision of changing stages depends on them
                hours, minutes = datetime_to_pair(json.loads(msg.payload)['time'], self.start_record_time)
                time_elapsed = timedelta(hours = hours, minutes = minutes)
                current_heartbeat = json.loads(msg.payload)['heartrate']
                
                print("Time slept: " + str(time_elapsed) + " Stage: " + self.stage)
                
                # we call a handler based on the current stage
                if self.stage == SLEEP_STAGES['NREM1']:
                   self.on_stage_NREM1(minutes, current_heartbeat)
                elif self.stage == SLEEP_STAGES['NREM2']:
                   self.on_stage_NREM2(time_elapsed)
                elif self.stage == SLEEP_STAGES['NREM3']:
                   self.on_stage_NREM3(time_elapsed, current_heartbeat)
                else:
                   self.on_stage_REM(time_elapsed, datetime.strptime(json.loads(msg.payload)['time'], "%H:%M:%S"))
                
        # Keep this commented until #52 is solved - theoretically solved
        client.subscribe(TOPIC['START_TO_SLEEP'])
        client.subscribe(TOPIC['HEARTRATE'])
        client.on_message = on_message

    def run(self):
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
