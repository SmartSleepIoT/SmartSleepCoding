import requests
from SmartSleep.db import get_db
from flask import jsonify, Blueprint

bp = Blueprint("sleepQuality", __name__, url_prefix="/sleep")


@bp.route('/all-time-slept', methods=("GET",))
def get_all_time_slept():
    db = get_db()

    try:
        all_time_slept = db.execute('SELECT *'
                                    ' FROM time_slept'
                                    ' ORDER BY timestamp').fetchall()
        for i in range(len(all_time_slept)):
            all_time_slept[i] = (
                all_time_slept[i]['hours'],
                all_time_slept[i]['minutes'],
                all_time_slept[i]['timestamp']
            )

        return jsonify({'status': all_time_slept}), 200
    except Exception as e:
        return jsonify({'status': f"Operation failed: {e}"}), 403


@bp.route('/all-snores', methods=("GET",))
def get_all_snores():
    db = get_db()

    try:
        all_snores = db.execute('SELECT *'
                                ' FROM snore'
                                ' WHERE value = 1'
                                ' ORDER BY timestamp').fetchall()
        for i in range(len(all_snores)):
            all_snores[i] = (
                all_snores[i]['value'],
                all_snores[i]['timestamp']
            )

        return jsonify({'status': all_snores}), 200
    except Exception as e:
        return jsonify({'status': f"Operation failed: {e}"}), 403


@bp.route('/all-sleep-intervals', methods=("GET",))
def get_sleep_intervals():
    db = get_db()
    intervals = []

    try:
        all_time_slept = db.execute('SELECT *'
                                    ' FROM start_to_sleep'
                                    ' ORDER BY timestamp').fetchall()
        max_i = len(all_time_slept)
        if max_i % 2 != 0:
            max_i = max_i - 1

        for i in range(0, max_i, 2):
            intervals.append((all_time_slept[i]['timestamp'], all_time_slept[i + 1]['timestamp']))

        return jsonify({'status': intervals}), 200

    except Exception as e:
        return jsonify({'status': f"Operation failed: {e}"}), 403
