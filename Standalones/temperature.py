import random
import json
from datetime import datetime
from SmartSleep.db import get_db

import requests
from paho.mqtt import client as mqtt_client
import sys


broker = 'broker.emqx.io'
port = 1883
# generate client ID with pub prefix randomly
client_id = f'python-mqtt-{random.randint(0, 100)}'
username = 'emqx'
password = 'public'


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
        if "C" in json.loads(msg.payload):
            print(f"Received `{json.loads(msg.payload)}` from `{msg.topic}` topic")
            current_temperature = int(json.loads(msg.payload)['C'])

            session = requests.Session()

            username = "Radu3"
            password = "123456A"
            response = session.post(f"http://127.0.0.1:5000/auth/register?username={username}&password={password}")
            response = session.post(f"http://127.0.0.1:5000/auth/login?username={username}&password={password}")
            response = session.get(f"http://127.0.0.1:5000/config/temp")

            desired_temperature = int(response.json()['data']['value'])

            if current_temperature > desired_temperature:
                r = requests.get("http://127.0.0.1:5000/temperature/cool-temperature")
            elif current_temperature < desired_temperature:
                r = requests.get("http://127.0.0.1:5000/temperature/warm-temperature")



    client.subscribe("SmartSleep/TemperatureSensor")
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
