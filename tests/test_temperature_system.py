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


def test_cooling_system(client, auth):
    global msg_nr
    msg_nr = 0
    global messages
    messages = ['16',
                "Setting the temperature system level to 1.0", "New temperature system level set to 1.0",
                '16',
                "Setting the temperature system level to 2.0", "New temperature system level set to 2.0",
                '16',
                "Setting the temperature system level to 3.0", "New temperature system level set to 3.0",
                '16',
                "Setting the temperature system level to 4.0", "New temperature system level set to 4.0",
                '19',
                "Setting the temperature system level to 3.0", "New temperature system level set to 3.0",
                '16',
                "Setting the temperature system level to 4.0", "New temperature system level set to 4.0",
                "18"
                ]

    time.sleep(2)

    client_mqtt = paho.Client("client-test-snoring")
    client_mqtt.on_message = on_message
    client_mqtt.connect(broker)
    client_mqtt.loop_start()
    client_mqtt.subscribe("SmartSleep/SoundSensor")
    auth.login()

    response = client.post(f"/config/start_to_sleep?sleep_now={True}")
    assert response.status_code == 200

    response = client.post("/config/temp?temperature=18")
    assert response.status_code == 200
    time.sleep(1.5)

    response = client.post("/config/current_temp?sensor=16")
    assert response.status_code == 200
    time.sleep(1.5)

    response = client.post("/config/current_temp?sensor=16")
    assert response.status_code == 200
    time.sleep(1.5)

    response = client.post("/config/current_temp?sensor=16")
    assert response.status_code == 200
    time.sleep(1.5)

    response = client.post("/config/current_temp?sensor=16")
    assert response.status_code == 200
    time.sleep(1.5)

    response = client.post("/config/current_temp?sensor=19")
    assert response.status_code == 200
    time.sleep(1.5)

    response = client.post("/config/current_temp?sensor=16")
    assert response.status_code == 200
    time.sleep(1.5)

    response = client.post("/config/current_temp?sensor=18")
    assert response.status_code == 200
    time.sleep(1.5)

