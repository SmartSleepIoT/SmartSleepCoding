import random
import json
from datetime import datetime

import requests
from paho.mqtt import client as mqtt_client
import sys


broker = 'broker.emqx.io'
port = 1883
# generate client ID with pub prefix randomly
client_id = f'python-mqtt-{random.randint(0, 100)}'
username = 'emqx'
password = 'public'

breathing_stops_intervals = []
normal_breathing_intervals = []
apnea = None
currently_not_breathing = False
recording_started = None
last_normal_breathing_time = None


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


def check_if_user_has_apenea(current_time):
    global recording_started, currently_not_breathing, breathing_stops_intervals, normal_breathing_intervals, apnea, last_normal_breathing_time
    time_recorded = datetime.strptime(current_time, "%H:%M:%S") - datetime.strptime(recording_started, "%H:%M:%S")
    time_recorded = time_recorded.total_seconds()

    # we test this in 1 hour intervals
    if 3600 <= time_recorded <= 3700:
        breathing_stops = len(breathing_stops_intervals)
        if currently_not_breathing:
            breathing_stops += 1

        normal_breathing = len(normal_breathing_intervals)
        if not currently_not_breathing:
            normal_breathing += 1

        if normal_breathing >= breathing_stops:
            session = requests.Session()

            username = "Radu3"
            password = "123456A"
            response = session.post(f"http://127.0.0.1:5000/auth/register?username={username}&password={password}")
            response = session.post(f"http://127.0.0.1:5000/auth/login?username={username}&password={password}")
            if 5 <= breathing_stops <= 14:
                print("*mild apnea*")
                apnea = "mild"
                r = session.post("http://127.0.0.1:5000/config/apnea?apnea=mild")
            elif 15 <= breathing_stops <= 30 :
                print("*moderate apnea*")
                r = session.post("http://127.0.0.1:5000/config/apnea?apnea=moderate")
            elif breathing_stops >= 30:
                print("*severe apnea*")
                r = session.post("http://127.0.0.1:5000/config/apnea?apnea=severe")
            else:
                print("*no apnea*")
                r = session.post("http://127.0.0.1:5000/config/apnea?apnea=none")

            breathing_stops_intervals = []
            normal_breathing_intervals = []
            apnea = None
            currently_not_breathing = False
            recording_started = None
            last_normal_breathing_time = None


def subscribe2(client: mqtt_client):
    def on_message(client, userdata, msg):
        global recording_started, currently_not_breathing, breathing_stops_intervals, last_normal_breathing_time
        print(f"Received `{json.loads(msg.payload)}` from `{msg.topic}` topic")
        if "db" in json.loads(msg.payload):
            db_sensor_value = json.loads(msg.payload)["db"]
            now = datetime.now()
            current_time = now.strftime("%H:%M:%S")
            if 0 <= float(db_sensor_value) <= 3:
                currently_not_breathing = True
            # normal breathing is about 10db
            elif 8 <= float(db_sensor_value) <= 65:
                if currently_not_breathing == True:
                    time_not_breathing = datetime.strptime(current_time, "%H:%M:%S") - datetime.strptime(last_normal_breathing_time,
                                                                                                    "%H:%M:%S")
                    time_not_breathing = time_not_breathing.total_seconds()
                    # people who have apnea stop breathing for 10 to 30 seconds at a time
                    if 10 <= time_not_breathing <= 30:
                        breathing_stops_intervals.append([last_normal_breathing_time, current_time])
                        print(f"user stopped breathing for {time_not_breathing}, nr of breathing stops {len(breathing_stops_intervals)}")

                currently_not_breathing = False
                last_normal_breathing_time = current_time

            if recording_started is None:
                recording_started = current_time
            else:
                check_if_user_has_apenea(current_time)


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
