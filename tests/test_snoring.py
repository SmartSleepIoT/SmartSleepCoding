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


def test_snoring(client, auth):
    global msg_nr
    msg_nr = 0
    global messages
    messages = ['45.05', '45.05', '45.05', '45.05', 'Lifting up pillow position to 10',
                'Lifted up pillow position to 10', '46.00']

    time.sleep(2)

    client_mqtt = paho.Client("client-test-snoring")
    client_mqtt.on_message = on_message
    client_mqtt.connect(broker)
    client_mqtt.loop_start()
    client_mqtt.subscribe("SmartSleep/SoundSensor")
    auth.login()
    response = client.post(f"/config/start_to_sleep?sleep_now={True}")
    assert response.status_code == 200
    response = client.post("/config/sound?sensor=45.05")
    assert response.status_code == 200
    time.sleep(1.5)
    response = client.post("/config/sound?sensor=45.05")
    assert response.status_code == 200
    time.sleep(1.5)
    response = client.post("/config/sound?sensor=45.05")
    assert response.status_code == 200
    time.sleep(1.5)
    response = client.post("/config/sound?sensor=45.05")
    assert response.status_code == 200
    time.sleep(5)
    response = client.post("/config/sound?sensor=46.00")
    assert response.status_code == 200
    time.sleep(1.5)

    client_mqtt.disconnect()
    client_mqtt.loop_stop()


def test_snoring_user_not_sleeping(client, auth):
    global msg_nr
    msg_nr = 0
    global messages
    messages = ['45.05', '45.05', '45.05', '45.05', '46.00']

    time.sleep(2)

    client_mqtt = paho.Client("client-test-snoring")
    client_mqtt.on_message = on_message
    client_mqtt.connect(broker)
    client_mqtt.loop_start()
    client_mqtt.subscribe("SmartSleep/SoundSensor")
    auth.login()
    response = client.post(f"/config/start_to_sleep?sleep_now={False}")
    assert response.status_code == 200
    response = client.post("/config/sound?sensor=45.05")
    assert response.status_code == 200
    time.sleep(1.5)
    response = client.post("/config/sound?sensor=45.05")
    assert response.status_code == 200
    time.sleep(1.5)
    response = client.post("/config/sound?sensor=45.05")
    assert response.status_code == 200
    time.sleep(1.5)
    response = client.post("/config/sound?sensor=45.05")
    assert response.status_code == 200
    time.sleep(5)
    response = client.post("/config/sound?sensor=46.00")
    assert response.status_code == 200
    time.sleep(1.5)

    client_mqtt.disconnect()
    client_mqtt.loop_stop()
