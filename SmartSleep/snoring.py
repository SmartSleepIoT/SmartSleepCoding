import json

from flask import Blueprint, jsonify
from SmartSleep.configuration import post_pillow_angle
from SmartSleep.db import get_db
from SmartSleep import pubMQTT

bp = Blueprint("snoring", __name__, url_prefix="/snoring")


@bp.route("/pillow-angle", methods=["GET"])
def liftPillow():
    # see if user is sleeping
    db = get_db()
    sleep = db.execute('SELECT value'
                       ' FROM start_to_sleep'
                       ' ORDER BY timestamp DESC').fetchone()

    if sleep is None or sleep is False:
        msg = {'status': "user is not sleeping"}
        return jsonify(msg), 404

    # get current angle + 10
    angle = 10
    current_angle = db.execute('SELECT value'
                               ' FROM pillow_angle'
                               ' ORDER BY timestamp DESC').fetchone()
    if current_angle is not None:
        angle = float(current_angle['value']) + 10

    # Try to lift up the pillow
    msg = {'status': f"Lifting up pillow position to {angle}"}
    pubMQTT.publish(json.dumps(msg), "SmartSleep/SoundSensor")
    post_pillow_angle(angle)

    # Pillow lifted, broadcast msg to the topic
    msg = {'status': f"Lifted up pillow position to {angle}"}
    pubMQTT.publish(json.dumps(msg), "SmartSleep/SoundSensor")

    return jsonify(msg), 200
