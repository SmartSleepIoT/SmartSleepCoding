from SmartSleep.db import get_db
from flask import jsonify, Blueprint
from datetime import datetime
from datetime import timedelta

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
            intervals.append(
                (all_time_slept[i]['timestamp'],
                 all_time_slept[i + 1]['timestamp'],
                 all_time_slept[i]['id'])
            )

        return jsonify({'status': intervals}), 200

    except Exception as e:
        return jsonify({'status': f"Operation failed: {e}"}), 403


@bp.route('/all-heartrates', methods=("GET",))
def get_heartrates():
    db = get_db()
    heartrates = []

    try:
        all_heartrates = db.execute('SELECT *'
                                    ' FROM heartrate'
                                    ' ORDER BY sleep, time').fetchall()

        for i in range(len(all_heartrates)):
            start_sleep_time = db.execute(f"SELECT timestamp"
                                          " FROM start_to_sleep"
                                          " WHERE id = ?", (all_heartrates[i]['sleep'],)
                                          ).fetchone()

            heartrate_time = datetime.strptime(all_heartrates[i]['time'], '%M:%S:%y')

            timestamp = start_sleep_time['timestamp'] + timedelta(minutes=heartrate_time.minute, seconds=heartrate_time.second)

            heartrates.append(
                (all_heartrates[i]['heartrate'],
                 all_heartrates[i]['sleep'],
                 timestamp
                 ),
            )

        return jsonify({'status': heartrates}), 200

    except Exception as e:
        return jsonify({'status': f'Operation failed: {e}'}), 403


@bp.route('/all-apneas', methods=("GET",))
def get_apneas():
    db = get_db()
    apneas = []

    try:
        all_apneas = db.execute('SELECT *'
                                ' FROM apnea'
                                ' ORDER BY timestamp').fetchall()

        for i in range(len(all_apneas)):
            apneas.append(
                (all_apneas[i]['value'],
                 all_apneas[i]['timestamp'])
            )

        return jsonify({'status': apneas}), 200

    except Exception as e:
        return jsonify({'status': f'Operation failed: {e}'}), 403
