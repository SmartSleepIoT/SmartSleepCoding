import json

from flask import Blueprint, jsonify
from SmartSleep.configuration import post_temperature_system_level
from SmartSleep.db import get_db
from SmartSleep import pubMQTT

bp = Blueprint("temperature", __name__, url_prefix="/temperature")


@bp.route("/warm-temperature", methods=["GET"])
def warmTemperature():
    # see if user is sleeping
    db = get_db()
    sleep = db.execute('SELECT value'
                       ' FROM start_to_sleep'
                       ' ORDER BY timestamp DESC').fetchone()

    if sleep is None or sleep is False:
        msg = {'status': "user is not sleeping"}
        return jsonify(msg), 404

    current_temperature_level = db.execute('SELECT value'
                                           ' FROM temperature_system_levels'
                                           ' ORDER BY timestamp DESC').fetchone()
    if current_temperature_level is None:
        new_temperature_level = 1
    else:
        new_temperature_level = float(current_temperature_level['value']) + 1

    if new_temperature_level <= 6:
        msg = {'status': f"Setting the temperature system level to {new_temperature_level}"}
        pubMQTT.publish(json.dumps(msg), "SmartSleep/TemperatureSensor")
        post_temperature_system_level(new_temperature_level)

        msg = {'status': f"New temperature system level set to {new_temperature_level}"}
        pubMQTT.publish(json.dumps(msg), "SmartSleep/TemperatureSensor")

        return jsonify(msg), 200


@bp.route("/cool-temperature", methods=["GET"])
def coolTemperature():
    # see if user is sleeping
    db = get_db()
    sleep = db.execute('SELECT value'
                       ' FROM start_to_sleep'
                       ' ORDER BY timestamp DESC').fetchone()

    if sleep is None or sleep is False:
        msg = {'status': "user is not sleeping"}
        return jsonify(msg), 404

    current_temperature_level = db.execute('SELECT value'
                                           ' FROM temperature_system_levels'
                                           ' ORDER BY timestamp DESC').fetchone()
    if current_temperature_level is None:
        new_temperature_level = -1
    else:
        new_temperature_level = float(current_temperature_level['value']) - 1

    if new_temperature_level >= -6:
        msg = {'status': f"Setting the temperature system level to {new_temperature_level}"}
        pubMQTT.publish(json.dumps(msg), "SmartSleep/TemperatureSensor")
        post_temperature_system_level(new_temperature_level)

        msg = {'status': f"New temperature system level set to {new_temperature_level}"}
        pubMQTT.publish(json.dumps(msg), "SmartSleep/TemperatureSensor")

        return jsonify(msg), 200
