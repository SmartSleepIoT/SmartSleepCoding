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


def test_breathing(client, auth):
    global msg_nr
    msg_nr = 0

    runpy.run_path(
        '../Standalones/breathing.py')  # TO DO: remove this when script to load standalones when  app starts is made

