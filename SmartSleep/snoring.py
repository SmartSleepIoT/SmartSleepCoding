import random
import json
from datetime import datetime

import requests
from paho.mqtt import client as mqtt_client
import sys

from SmartSleep.configuration import liftPillow

broker = 'broker.emqx.io'
port = 1883
topic = "SmartSleepMQTT"
topic2 = "SmartSleep/WakeUp"
topic3 = "SmartSleep/SoundSensor"
# generate client ID with pub prefix randomly
client_id = f'python-mqtt-{random.randint(0, 100)}'
username = 'emqx'
password = 'public'

snoringSounds = []
lastTime = None
snoring = False

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


def subscribe2(client: mqtt_client):
    def on_message(client, userdata, msg):
        global snoringSounds, lastTime, snoring
        print(f"Received `{json.loads(msg.payload)}` from `{msg.topic}` topic")
        if "db" in  json.loads(msg.payload):
            db_sensor_value = json.loads(msg.payload)["db"]
            if 40 <= float(db_sensor_value) <= 61:
                snoringSounds.append(json.loads(msg.payload))
                now = datetime.now()
                current_time = now.strftime("%H:%M:%S")
                if lastTime is None:
                    lastTime = current_time
                else:
                    # verify if it is snoring
                    time_between_sounds = datetime.strptime(current_time, "%H:%M:%S") - datetime.strptime(lastTime, "%H:%M:%S")
                    seconds = time_between_sounds.total_seconds()
                    # print(lastTime, current_time, len(snoringSounds))
                    if 3 <= seconds <= 10:
                        lastTime = current_time
                        if len(snoringSounds) >= 4:
                            print("*user snores*")
                            snoring = True
                            requests.get("http://127.0.0.1:5000/snoring/pillow-angle")
                            snoring = False
                            lastTime = None
                            snoringSounds = []
                    else:
                        snoring = False


    client.subscribe("SmartSleep/SoundSensor")
    client.on_message = on_message


def run():
    client = connect_mqtt()
    subscribe2(client)
    client.loop_forever()


if __name__ == '__main__':
    try:
        run()
    except KeyboardInterrupt:
        print('interrupted')
        sys.exit(0)
