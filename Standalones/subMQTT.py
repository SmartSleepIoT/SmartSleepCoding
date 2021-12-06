import random
import json
import sys
from paho.mqtt import client as mqtt_client

"""
Test app listening to all SmartSleep topics
"""
broker = 'broker.emqx.io'
port = 1883
topic = "SmartSleep/#" # '#' is a special character, meaning all topics starting with SmartSleep will be covered
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


def subscribe(client: mqtt_client):
    def on_message(client, userdata, msg):
        try: print(f"Received `{json.loads(msg.payload)}` from `{msg.topic}` topic")
        except json.JSONDecodeError: print(f"Received `{msg.payload}` from `{msg.topic}` topic")

    client.subscribe(topic)
    client.on_message = on_message


def run():
    client = connect_mqtt()
    subscribe(client)
    client.loop_forever()


if __name__ == '__main__':
    try:
        run()
    except KeyboardInterrupt:
        print('interrupted')
        sys.exit(0)
