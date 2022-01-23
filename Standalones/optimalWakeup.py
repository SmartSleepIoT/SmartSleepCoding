import random
import json
from datetime import datetime
import requests
from paho.mqtt import client as mqtt_client
import sys
from SmartSleep.configuration import start_to_sleep
from constants import sleep_needed

broker = 'broker.emqx.io'
port = 1883
# generate client ID with pub prefix randomly
client_id = f'python-mqtt-{random.randint(0, 100)}'
username = 'emqx'
password = 'public'
start = 0
end = 0
scores = []
decrease_limit = 3

def connect_mqtt() -> mqtt_client:
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client(client_id)
    client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client


def handleConnection(client: mqtt_client):
    def on_message(client, userdata, msg):
        global start, end, db
        if msg.topic == "SmartSleep/Heartrate":
            resting_heartrate = 75
            age = 20
            heartrate = json.loads(msg.payload)['heartrate']
            hour = json.loads(msg.payload)['time'].split()
            if start and end and start <= hour <= end:
                scores.append(0)
                # we want to wake up the user when she is in a light stage of sleep
                # heartrate decreases with 20% - 30% (based on the resting heartrate)
                #if heartrate <= 80/100 * resting_heartrate:
                    # we need to get the time slept   
        elif msg.topic == "SmartSleep/OptimalWakeup":
            print(f"Received `{json.loads(msg.payload)}` from `{msg.topic}` topic")
            start_hour = datetime.strptime(json.loads(msg.payload)['start'],"%H:%M")
            end_hour = datetime.strptime(json.loads(msg.payload)['end'],"%H:%M")
            start_to_sleep = json.loads(msg.payload)['start_to_sleep'].split()[1]
            sleep_start_hour =  datetime.strptime(start_to_sleep,"%H:%M")
            print("Start to sleep: " + sleep_start_hour + " " + start_hour + " " + end_hour)
            
    client.subscribe("SmartSleep/Heartrate")
    client.subscribe("SmartSleep/OptimalWakeup")
    client.on_message = on_message

def run():
    client = connect_mqtt()
    handleConnection(client)
    client.loop_forever()

if __name__ == '__main__':
    try:
        run()
    except KeyboardInterrupt:
        print('interrupted')
        sys.exit(0)
