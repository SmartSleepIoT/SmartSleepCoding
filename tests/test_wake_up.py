import time
from datetime import datetime, timedelta

import paho.mqtt.client as paho
from flask import json


msg_nr = 0
messages = [""]
broker = 'broker.emqx.io'
port = 1883


def update_contor():
    global msg_nr
    msg_nr += 1


def on_message(client, userdata, message):
    received = json.loads(message.payload)
    assert messages[msg_nr] == received["message"]
    update_contor()


def test_snoring(client, auth):
    global msg_nr
    msg_nr = 0
    global messages
    messages = ["Wake up the user", "User slept for 0 hours and 1 minutes"]

    client_mqtt = paho.Client("client-test-wake-up")
    client_mqtt.on_message = on_message
    client_mqtt.connect(broker)
    client_mqtt.loop_start()
    client_mqtt.subscribe("SmartSleep/WakeUp")
    auth.login()
    now = datetime.now()
    after_one_min = now + timedelta(minutes=1)
    wake_up_time = datetime.strftime(after_one_min, "%H:%M")
    response = client.post(f"/config/wake_up_hour?wake_up_hour={wake_up_time}")
    assert response.status_code == 200

    time.sleep(6)
    client_mqtt.disconnect()
    client_mqtt.loop_stop()
