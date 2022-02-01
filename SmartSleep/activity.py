import json
from flask import (
    Blueprint, request, jsonify
)
from SmartSleep.auth import login_required
from SmartSleep import pubMQTT

from SmartSleep.db import get_db
from util.functions import set_hour_and_minute

bp = Blueprint('activity', __name__, url_prefix="/activity")


@bp.route('/heartrate', methods=['POST'])
@login_required
def set_heartrate():
    """
    Set/record the heartrate received by the heartrate sensor
    """
    heartrate = request.args.get('heartrate')
    time = request.args.get('time')
    if not heartrate:
        return jsonify({'status': 'heartrate is required.'}), 403
    if not time:
        return jsonify({'status': 'time is required.'}), 403

    db = get_db()

    try:
        heartrate = int(heartrate)
        if heartrate <= 0:
            raise ValueError

        current_sleep = db.execute(
            'SELECT *'
            ' FROM start_to_sleep'
            ' ORDER BY id DESC'
        ).fetchone()['id']

        if time:
            db.execute(
                'INSERT INTO heartrate (heartrate, sleep, time) '
                ' VALUES (?, ?, ?)',
                (heartrate, current_sleep, set_hour_and_minute(time)))
        else:
            db.execute(
                'INSERT INTO heartrate (heartrate, sleep) '
                'VALUES (?, ?)',
                (heartrate, current_sleep)
            )
        db.commit()
    except ValueError as e:
        return jsonify({'status': "Heartrate must be a positive integer number"}), 403
    except Exception as e:
        return jsonify({'status': f"Operation failed: {e}"}), 403

    commited_value = db.execute(
        'SELECT *'
        ' FROM heartrate'
        ' ORDER BY id DESC'
    ).fetchone()

    msg = {'heartrate': commited_value['heartrate'],
           'time': str(commited_value['time'])}
    pubMQTT.publish(json.dumps(msg), "SmartSleep/Heartrate")

    return jsonify({
        'status': 'Heartrate successfully recorded',
        'data': {
            'id': commited_value['id'],
            'heartrate': commited_value['heartrate'],
            'time': commited_value['time']
        }}), 200


@bp.route("/sleep_stage", methods=["POST"])
@login_required
def set_sleep_stage():
    """Set sleep stage"""
    db = get_db()
    stage_arg = "stage"
    time_arg = "time"
    table_name = "sleep_stage"

    stage = request.args.get(stage_arg)
    if not stage:
        return jsonify({'status': f"{stage_arg} is required"}), 403
    time = request.args.get(time_arg)
    try:
        current_sleep = db.execute(
            'SELECT *'
            ' FROM start_to_sleep'
            ' ORDER BY id DESC'
        ).fetchone()['id']

        db.execute(
            f"INSERT INTO {table_name} (stage, sleep, time) VALUES (?, ?, ?)",
            (stage, current_sleep, time)
        )
        db.commit()
    except Exception as e:
        return jsonify({'status': f"Operation failed: {e}"}), 403
    committed_value = db.execute('SELECT *'
                                 f' FROM {table_name}'
                                 ' ORDER BY time DESC').fetchone()
    return jsonify({
        'status': f'{stage_arg} successfully set',
        'data': {
            'stage': committed_value['stage'],
            'sleep': committed_value['sleep'],
            'time': committed_value['time']
        }
    }), 200


@bp.route("/sleep_stage", methods=["GET"])
@login_required
def get_sleep_stage():
    """
    Get current sleep stage
    """
    arg_name = "stage"
    table_name = "sleep_stage"
    current_value = get_db().execute('SELECT *'
                                     f' FROM {table_name}'
                                     ' ORDER BY time DESC').fetchone()
    if current_value is None:
        return jsonify({'status': f'No {arg_name} ever set'}), 200

    print(jsonify({
        'status': f'{arg_name} successfully retrieved',
        'data': {
            'stage': current_value['stage'],
            'sleep': current_value['sleep'],
            'time': str(current_value['time'])
        }}))
    return jsonify({
        'status': f'{arg_name} successfully retrieved',
        'data': {
            'stage': current_value['stage'],
            'sleep': current_value['sleep'],
            'time': str(current_value['time'])
        }
    }), 200
