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

def subscribe2(client: mqtt_client, app):
    def on_message(client, userdata, msg):
        print(f"Received `{json.loads(msg.payload)}` from `{msg.topic}` topic")

        with app.app_context():
            db = get_db()
        temp = db.execute('SELECT value'
                          ' FROM temperature'
                          ' ORDER BY timestamp DESC').fetchone()
        print(temp)




    client.subscribe("SmartSleep/TemperatureSensor")
    client.on_message = on_message


def run(app):
    client = connect_mqtt()
    subscribe2(client, app)
    client.loop_forever()


if __name__ == '__main__':
    try:
        run(app)
    except KeyboardInterrupt:
        print('interrupted')
        sys.exit(0)
