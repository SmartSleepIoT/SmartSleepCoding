import time

import pytest
from flask import g
from flask import session
import paho.mqtt.client as paho
from SmartSleep.db import get_db
from flask import json
import runpy


msg_nr = 0
messages = [""]
broker = 'broker.emqx.io'
port = 1883


def update_contor():
    global msg_nr
    msg_nr += 1


def on_message(client, userdata, message):
    received = json.loads(message.payload)
    if "status" in received:
        assert received['status'] == messages[msg_nr]
        update_contor()
    elif "db" in received:
        assert received["db"] == messages[msg_nr]
        update_contor()

def send_data_to_sensor(client, auth):
    client_mqtt = paho.Client("client-test-breathing")
    client_mqtt.on_message = on_message
    client_mqtt.connect(broker)
    client_mqtt.loop_start()
    client_mqtt.subscribe("SmartSleep/SoundSensor")
    auth.login()
    response = client.post(f"/config/start_to_sleep?sleep_now={True}")
    assert response.status_code == 200


    sound_sensor = open("sound_sensor.txt")
    x = float(sound_sensor.readline())
    i = 0
    while i < 3600:
        response = client.post("/config/sound?sensor=" + str(x))
        assert response.status_code == 200
        time.sleep(1)
        x = float(sound_sensor.readline())
        print(x)
        i+=1

    client_mqtt.disconnect()
    client_mqtt.loop_stop()


def test_breathing(client, auth):
    global msg_nr
    msg_nr = 0

    runpy.run_path(
        '../Standalones/breathing.py')  # TO DO: remove this when script to load standalones when  app starts is made
    time.sleep(2)

    send_data_to_sensor(client, auth)

