import json

from flask import Blueprint, jsonify
from flask import flash
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
import requests
from werkzeug.exceptions import abort
from datetime import datetime

from SmartSleep.auth import login_required
from SmartSleep.db import get_db
from SmartSleep.wakeUpUser import WakeUpScheduler
from SmartSleep.validation import time_validation, boolean_validation
from SmartSleep import pubMQTT

bp = Blueprint("config", __name__, url_prefix="/config")


@bp.route("/", methods=["GET"])
@login_required
def current_config():
    """Show set temperature, waking mode, wake hour"""
    db = get_db()
    temp = db.execute('SELECT value'
                      ' FROM temperature'
                      ' ORDER BY timestamp DESC').fetchone()
    waking_mode = db.execute(
        "SELECT VALUE"
        " FROM waking_mode"
        " ORDER BY timestamp DESC"
    ).fetchone()
    wake_up_hour = db.execute(
        "SELECT VALUE"
        " FROM wake_up_hour"
        " ORDER BY timestamp DESC"
    ).fetchone()
    if temp is None:
        temp = {"value": "Not set"}
    if waking_mode is None:
        waking_mode = {"value": "Not set"}
    if wake_up_hour is None:
        wake_up_hour = {"value": "Not set"}
    return jsonify({
        'status': 'Configuration successfully retrieved',
        'data': {
            'temperature': dict(temp),
            'waking_mode': dict(waking_mode),
            'wake_up_hour': dict(wake_up_hour)
        }
    }), 200


@bp.route("/temp", methods=["GET", "POST", "DELETE"])
@login_required
def temp():
    """Get / Set / Delete temp"""
    table_name = "temperature"
    arg_name = "temperature"
    if request.method == "POST":
        value = request.args.get(arg_name)
        db = get_db()

        if not value:
            return jsonify({'status': f"{arg_name} is required"}), 403
        try:
            db.execute(
                f"INSERT INTO {table_name} (value) VALUES (?)",
                (value,)
            )
            db.commit()
        except Exception as e:
            return jsonify({'status': f"Operation failed: {e}"}), 403
        committed_value = db.execute('SELECT *'
                                     f' FROM {table_name}'
                                     ' ORDER BY timestamp DESC').fetchone()
        return jsonify({
            'status': f'{arg_name} successfully set',
            'data': {
                'id': committed_value['id'],
                'value': committed_value['value'],
                'timestamp': committed_value['timestamp']
            }
        }), 200
    if request.method == "GET":
        current_value = get_db().execute('SELECT *'
                                         f' FROM {table_name}'
                                         ' ORDER BY timestamp DESC').fetchone()
        if current_value is None:
            return jsonify({'status': f'No {arg_name} ever set'}), 200
        return jsonify({
            'status': f'{arg_name} successfully retrieved',
            'data': {
                'id': current_value['id'],
                'value': current_value['value'],
                'timestamp': current_value['timestamp']
            }
        }), 200
    if request.method == "DELETE":
        db = get_db()
        db.execute(f'DELETE FROM {table_name}')
        db.commit()
        return jsonify({'status': f'All values successfully deleted'}), 200

@bp.route("/sleep_stage", methods=["POST"])
@login_required
def set_sleep_stage():
    """Set sleep stage"""
    arg_name = "stage"
    if request.method == "POST":
        value = request.args.get(arg_name)
        #if not value:
         #   return jsonify({'status': f"{arg_name} is required"}), 403
        return jsonify({
            'status': f'{arg_name} successfully retrieved'
        }), 200
    #     try:
    #         db.execute(
    #             f"INSERT INTO {table_name} (value) VALUES (?)",
    #             (value,)
    #         )
    #         db.commit()
    #     except Exception as e:
    #         return jsonify({'status': f"Operation failed: {e}"}), 403
    #     committed_value = db.execute('SELECT *'
    #                                  f' FROM {table_name}'
    #                                  ' ORDER BY timestamp DESC').fetchone()
    #     return jsonify({
    #         'status': f'{arg_name} successfully set',
    #         'data': {
    #             'id': committed_value['id'],
    #             'value': committed_value['value'],
    #             'timestamp': committed_value['timestamp']
    #         }
    #     }), 200
    # if request.method == "GET":
    #     current_value = get_db().execute('SELECT *'
    #                                      f' FROM {table_name}'
    #                                      ' ORDER BY timestamp DESC').fetchone()
    #     if current_value is None:
    #         return jsonify({'status': f'No {arg_name} ever set'}), 200
    #     return jsonify({
    #         'status': f'{arg_name} successfully retrieved',
    #         'data': {
    #             'id': current_value['id'],
    #             'value': current_value['value'],
    #             'timestamp': current_value['timestamp']
    #         }
    #     }), 200

@bp.route("/current_temp", methods=["POST"])
@login_required
def current_temp():
    """Get / Set sounds in Db record by sound sensor"""
    table_name = "temperatures_recorded"
    arg_name = "sensor"

    if request.method == "POST":
        value = request.args.get(arg_name)
        db = get_db()

        if not value:
            return jsonify({'status': f"{arg_name} is required"}), 403
        try:
            if value != "0" and not float(value):
                return jsonify({'status': "wrong value for a C temperature expected a float number"}), 422
        except ValueError:
            return jsonify({'status': "Wrong angle format, must be float number "}), 422

        try:
            db.execute(
                f"INSERT INTO {table_name} (value) VALUES (?)",
                (value,)
            )
            db.commit()
        except Exception as e:
            return jsonify({'status': f"Operation failed: {e}"}), 403
        committed_value = db.execute('SELECT *'
                                     f' FROM {table_name}'
                                     ' ORDER BY timestamp DESC').fetchone()

        msg = {'C': f"{value}"}
        pubMQTT.publish(json.dumps(msg), "SmartSleep/TemperatureSensor")

        return jsonify({
            'status': f'{arg_name} successfully set',
            'data': {
                'id': committed_value['id'],
                'value': committed_value['value'],
                'timestamp': committed_value['timestamp']
            }
        }), 200


@bp.route("/waking_mode", methods=["GET", "POST", "DELETE"])
@login_required
def waking_mode():
    """Get / Set waking_mode"""
    table_name = "waking_mode"
    arg_name = "waking_mode"
    if request.method == "POST":
        value = request.args.get(arg_name)
        db = get_db()
        waking_modes = ['L', 'V', 'S', 'LVS', 'LV', 'LS', 'VS']
        if not value:
            return jsonify({'status': f"{arg_name} is required"}), 403
        if value not in waking_modes:
            return jsonify({'status': f"{arg_name} must be one of the following {waking_modes}"}), 422
        try:
            db.execute(
                f"INSERT INTO {table_name} (value) VALUES (?)",
                (value,)
            )
            db.commit()
        except Exception as e:
            return jsonify({'status': f"Operation failed: {e}"}), 403
        committed_value = db.execute('SELECT *'
                                     f' FROM {table_name}'
                                     ' ORDER BY timestamp DESC').fetchone()

        return jsonify({
            'status': f'{arg_name} successfully set',
            'data': {
                'id': committed_value['id'],
                'value': committed_value['value'],
                'timestamp': committed_value['timestamp']
            }
        }), 200
    if request.method == "GET":
        current_value = get_db().execute('SELECT *'
                                         f' FROM {table_name}'
                                         ' ORDER BY timestamp DESC').fetchone()
        if current_value is None:
            return jsonify({'status': f'No {arg_name} ever set'}), 200
        return jsonify({
            'status': f'{arg_name} successfully retrieved',
            'data': {
                'id': current_value['id'],
                'value': current_value['value'],
                'timestamp': current_value['timestamp']
            }
        }), 200
    if request.method == "DELETE":
        db = get_db()
        db.execute(f'DELETE FROM {table_name}')
        db.commit()
        return jsonify({'status': f'All values successfully deleted'}), 200

@bp.route("/temperature_system_level", methods=["GET", "POST"])
@login_required
def temperature_system_level():
    table_name = "temperature_system_levels"
    arg_name = "temperature_system_level"
    if request.method == "GET":
        current_value = get_db().execute('SELECT *'
                                         f' FROM {table_name}'
                                         ' ORDER BY timestamp DESC').fetchone()
        if current_value is None:
            return jsonify({'status': f'The temperature system is currently turned off'}), 200
        return jsonify({
            'status': f'{arg_name} successfully retrieved',
            'data': {
                'id': current_value['id'],
                'value': current_value['value'],
                'timestamp': current_value['timestamp']
            }
        }), 200
    elif request.method == "POST":
        value = request.args.get(arg_name)
        db = get_db()
        possible_values = [-6, -5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 6]
        if not value:
            return jsonify({'status': f"{arg_name} is required"}), 403
        if int(value) not in possible_values:
            return jsonify({'status': f"{arg_name} must be one of the following {possible_values}"}), 422
        try:
            value = int(value)
            db.execute(
                f"INSERT INTO {table_name} (value) VALUES (?)",
                (value,)
            )
            db.commit()
        except Exception as e:
            return jsonify({'status': f"Operation failed: {e}"}), 403
        committed_value = db.execute('SELECT *'
                                     f' FROM {table_name}'
                                     ' ORDER BY timestamp DESC').fetchone()

        return jsonify({
            'status': f'{arg_name} successfully set',
            'data': {
                'id': committed_value['id'],
                'value': committed_value['value'],
                'timestamp': committed_value['timestamp']
            }
        }), 200

@bp.route("/apnea", methods=["GET", "POST"])
@login_required
def apnea():
    table_name = "apnea"
    arg_name = "apnea"
    if request.method == "GET":
        current_value = get_db().execute('SELECT *'
                                         f' FROM {table_name}'
                                         ' ORDER BY timestamp DESC').fetchone()
        if current_value is None:
            return jsonify({'status': f'The user has not been tested for apnea.'}), 200
        return jsonify({
            'status': f'{arg_name} successfully retrieved',
            'data': {
                'id': current_value['id'],
                'value': current_value['value'],
                'timestamp': current_value['timestamp']
            }
        }), 200
    elif request.method == "POST":
        value = request.args.get(arg_name)
        db = get_db()
        possible_values = ["none", "mild", "moderate", "severe"]
        if not value:
            return jsonify({'status': f"{arg_name} is required"}), 403
        if value not in possible_values:
            return jsonify({'status': f"{arg_name} must be one of the following {possible_values}"}), 422
        try:
            db.execute(
                f"INSERT INTO {table_name} (value) VALUES (?)",
                (value,)
            )
            db.commit()
        except Exception as e:
            return jsonify({'status': f"Operation failed: {e}"}), 403
        committed_value = db.execute('SELECT *'
                                     f' FROM {table_name}'
                                     ' ORDER BY timestamp DESC').fetchone()

        return jsonify({
            'status': f'{arg_name} successfully set',
            'data': {
                'id': committed_value['id'],
                'value': committed_value['value'],
                'timestamp': committed_value['timestamp']
            }
        }), 200


def post_pillow_angle(value):
    arg_name = "pillow_angle"
    table_name = "pillow_angle"
    if not value:
        return jsonify({'status': f"{arg_name} is required"}), 403
    try:
        if value != "0" and not float(value):
            return jsonify({'status': "Wrong angle format, must be float number "}), 422
    except ValueError:
        return jsonify({'status': "Wrong angle format, must be float number "}), 422



    db = get_db()

    try:
        db.execute(
            f"INSERT INTO {table_name} (value) VALUES (?)",
            (value,)
        )
        db.commit()
    except Exception as e:
        return jsonify({'status': f"Operation failed: {e}"}), 403
    committed_value = db.execute('SELECT *'
                                 f' FROM {table_name}'
                                 ' ORDER BY timestamp DESC').fetchone()
    return jsonify({
        'status': f'{arg_name} successfully set',
        'data': {
            'id': committed_value['id'],
            'value': committed_value['value'],
            'timestamp': committed_value['timestamp']
        }
    }), 200

def post_temperature_system_level(value):
    arg_name = "temperature_system_level"
    table_name = "temperature_system_levels"
    possible_values = [-6, -5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 6]
    if not value:
        return jsonify({'status': f"{arg_name} is required"}), 403
    try:
        if value != "0" and int(value) not in possible_values:
            return jsonify({'status': f"Wrong angle format, must be an int number in {possible_values}"}), 422
    except ValueError:
        return jsonify({'status': "Wrong angle format, must be int number "}), 422

    value = int(value)
    db = get_db()

    try:
        db.execute(
            f"INSERT INTO {table_name} (value) VALUES (?)",
            (value,)
        )
        db.commit()
    except Exception as e:
        return jsonify({'status': f"Operation failed: {e}"}), 403
    committed_value = db.execute('SELECT *'
                                 f' FROM {table_name}'
                                 ' ORDER BY timestamp DESC').fetchone()
    return jsonify({
        'status': f'{arg_name} successfully set',
        'data': {
            'id': committed_value['id'],
            'value': committed_value['value'],
            'timestamp': committed_value['timestamp']
        }
    }), 200


def post(value):
    arg_name = "pillow_angle"
    table_name = "pillow_angle"
    if not value:
        return jsonify({'status': f"{arg_name} is required"}), 403
    try:
        if value != "0" and not float(value):
            return jsonify({'status': "Wrong angle format, must be float number "}), 422
    except ValueError:
        return jsonify({'status': "Wrong angle format, must be float number "}), 422



    db = get_db()

    try:
        db.execute(
            f"INSERT INTO {table_name} (value) VALUES (?)",
            (value,)
        )
        db.commit()
    except Exception as e:
        return jsonify({'status': f"Operation failed: {e}"}), 403
    committed_value = db.execute('SELECT *'
                                 f' FROM {table_name}'
                                 ' ORDER BY timestamp DESC').fetchone()
    return jsonify({
        'status': f'{arg_name} successfully set',
        'data': {
            'id': committed_value['id'],
            'value': committed_value['value'],
            'timestamp': committed_value['timestamp']
        }
    }), 200


@bp.route("/pillow_angle", methods=["GET", "POST", "DELETE"])
@login_required
def pillow_angle():
    """Get / Set / Delete pillow angle"""
    table_name = "pillow_angle"
    arg_name = "pillow_angle"
    if request.method == "POST":
        value = request.args.get(arg_name)
        return post_pillow_angle(value)
    if request.method == "GET":
        current_value = get_db().execute('SELECT *'
                                         f' FROM {table_name}'
                                         ' ORDER BY timestamp DESC').fetchone()
        if current_value is None:
            return jsonify({'status': f'No {arg_name} ever set'}), 200
        return jsonify({
            'status': f'{arg_name} successfully retrieved',
            'data': {
                'id': current_value['id'],
                'value': current_value['value'],
                'timestamp': current_value['timestamp']
            }
        }), 200
    if request.method == "DELETE":
        db = get_db()
        db.execute(f'DELETE FROM {table_name}')
        db.commit()
        return jsonify({'status': f'All values successfully deleted'}), 200


@bp.route("/wake_up_interval", methods=["POST"])
def waking_interval():
    """
    Set wake up interval
    """
    start = request.args.get('interval_start')
    end = request.args.get('interval_end')
    if not start:
        return jsonify({'status': "interval_start is required"}), 403
    if not end:
        return jsonify({'status': "interval_end is required"}), 403
    start_time, msg = time_validation(start)
    if not start_time:
                return jsonify({'status': f"{msg}"}), 422
    end_time, msg = time_validation(end)
    if not end_time:
                return jsonify({'status': f"{msg}"}), 422
    
    wake_up_user = WakeUpScheduler()
    db = get_db()
    start_to_sleep = db.execute(' SELECT *'
                                ' FROM start_to_sleep'
                                ' ORDER BY timestamp DESC').fetchone()
    
    wake_up_user.schedule_wake_up([start, end], 'LS', str(start_to_sleep['timestamp']), optimal = True)
    return jsonify({
            'status': f'wake up interval successfully set',
        }), 200

@bp.route("/wake_up_hour", methods=["GET", "POST", "DELETE"])
def waking_hour():
    """Get / Set wake_up_hour"""
    table_name = "wake_up_hour"
    arg_name = "wake_up_hour"
    wake_up_user = WakeUpScheduler()
    if request.method == "POST":
        value = request.args.get(arg_name)
        db = get_db()

        if not value:
            return jsonify({'status': f"{arg_name} is required"}), 403
        else:
            val, msg = time_validation(value)
            if not val:
                return jsonify({'status': f"{msg}"}), 422

        try:
            db.execute(
                f"INSERT INTO {table_name} (value) VALUES (?)",
                (value,)
            )
            db.commit()
        except Exception as e:
            return jsonify({'status': f"Operation failed: {e}"}), 403
        committed_value = db.execute('SELECT *'
                                     f' FROM {table_name}'
                                     ' ORDER BY timestamp DESC').fetchone()

        # schedule wake up
        # get he mode from db if not mode is set use default mode LS
        mode = get_db().execute("SELECT value FROM waking_mode ORDER BY TIMESTAMP").fetchone()
        if mode is None:
            mode = 'LS'

        time = value.split(":")
        now = datetime.now()
        current_time = now.strftime("%H:%M")
        wake_up_user.schedule_wake_up([(time[0], time[1])], mode, current_time)
        # schedule_wake_up(time[0], time[1], mode)

        return jsonify({
            'status': f'{arg_name} successfully set',
            'data': {
                'id': committed_value['id'],
                'value': committed_value['value'],
                'timestamp': committed_value['timestamp']
            }
        }), 200
    if request.method == "GET":
        current_value = get_db().execute('SELECT *'
                                         f' FROM {table_name}'
                                         ' ORDER BY timestamp DESC').fetchone()
        if current_value is None:
            return jsonify({'status': f'No {arg_name} ever set'}), 200
        return jsonify({
            'status': f'{arg_name} successfully retrieved',
            'data': {
                'id': current_value['id'],
                'value': current_value['value'],
                'timestamp': current_value['timestamp']
            }
        }), 200
    if request.method == "DELETE":
        db = get_db()
        db.execute(f'DELETE FROM {table_name}')
        db.commit()
        # delete scheduled wake up
        wake_up_user.delete_wake_up_schedule()

        return jsonify({'status': f'All values successfully deleted'}), 200


@bp.route("/start_to_sleep", methods=["GET", "POST", "DELETE"])
@login_required
def start_to_sleep():
    """Get / Set start_to_sleep"""
    table_name = "start_to_sleep"
    arg_name = "sleep_now"
    time_arg_name = "time"

    if request.method == "POST":
        value = request.args.get(arg_name)
        time = request.args.get(time_arg_name)
        db = get_db()

        if not value:
            return jsonify({'status': f"{arg_name} is required"}), 403
        else:
            val, msg = boolean_validation(value)
            if not val:
                return jsonify({'status': f"{msg}"}), 422

            elif msg == "true":
                value = 1
            else:
                value = 0

        try:
            db.execute(
                f"INSERT INTO {table_name} (value) VALUES (?)",
                (value,)
            )
            db.commit()
        except Exception as e:
            return jsonify({'status': f"Operation failed: {e}"}), 403
        committed_value = db.execute('SELECT *'
                                     f' FROM {table_name}'
                                     ' ORDER BY timestamp DESC').fetchone()
        
        msg = {'time': time}
        pubMQTT.publish(json.dumps(msg), "SmartSleep/StartSleeping")

        return jsonify({
            'status': f'{arg_name} successfully set',
            'data': {
                'id': committed_value['id'],
                'value': committed_value['value'],
                'timestamp': committed_value['timestamp']
            }
        }), 200

    if request.method == "GET":
        current_value = get_db().execute('SELECT *'
                                         f' FROM {table_name}'
                                         ' ORDER BY timestamp DESC').fetchone()
        if current_value is None:
            return jsonify({'status': f'No {arg_name} ever set'}), 200
        return jsonify({
            'status': f'{arg_name} successfully retrieved',
            'data': {
                'id': current_value['id'],
                'value': current_value['value'],
                'timestamp': current_value['timestamp']
            }
        }), 200
    if request.method == "DELETE":
        db = get_db()
        db.execute(f'DELETE FROM {table_name}')
        db.commit()
        return jsonify({'status': f'All values successfully deleted'}), 200

@bp.route("/sound", methods=["POST"])
@login_required
def sound():
    """Get / Set sounds in Db record by sound sensor"""
    table_name = "sounds_recorded"
    arg_name = "sensor"

    if request.method == "POST":
        value = request.args.get(arg_name)
        db = get_db()

        if not value:
            return jsonify({'status': f"{arg_name} is required"}), 403
        try:
            if value != "0" and not float(value):
                return jsonify({'status': "wrong value for a db sound expected a float number"}), 422
        except ValueError:
            return jsonify({'status': "Wrong angle format, must be float number "}), 422

        try:
            db.execute(
                f"INSERT INTO {table_name} (value) VALUES (?)",
                (value,)
            )
            db.commit()
        except Exception as e:
            return jsonify({'status': f"Operation failed: {e}"}), 403
        committed_value = db.execute('SELECT *'
                                     f' FROM {table_name}'
                                     ' ORDER BY timestamp DESC').fetchone()

        msg = {'db': f"{value}"}
        pubMQTT.publish(json.dumps(msg), "SmartSleep/SoundSensor")

        return jsonify({
            'status': f'{arg_name} successfully set',
            'data': {
                'id': committed_value['id'],
                'value': committed_value['value'],
                'timestamp': committed_value['timestamp']
            }
        }), 200


@bp.route("/time_slept", methods=["GET", "POST", "DELETE"])
def hours_slept():
    """Get / Set / Delete hours_slept"""
    table_name = "time_slept"
    arg_name = "time"
    if request.method == "POST":
        value = request.args.get(arg_name)
        return post_hours_slept(value)

    if request.method == "GET":
        current_value = get_db().execute('SELECT *'
                                         f' FROM {table_name}'
                                         ' ORDER BY timestamp DESC').fetchone()
        if current_value is None:
            return jsonify({'status': f'No {arg_name} ever set'}), 200
        return jsonify({
            'status': f'{arg_name} successfully retrieved',
            'data': {
                'id': current_value['id'],
                'hours slept': current_value['hours'],
                'minutes slept': current_value['minutes'],
                'timestamp': current_value['timestamp']
            }
        }), 200

    if request.method == "DELETE":
        db = get_db()
        db.execute(f'DELETE FROM {table_name}')
        db.commit()
        return jsonify({'status': f'All values successfully deleted'}), 200


def post_hours_slept(value):
    arg_name = "time"
    table_name = "time_slept"
    if not value:
        return jsonify({'status': f"{arg_name} is required"}), 403

    val, msg = time_validation(value)
    if not val:
        return jsonify({'status': f"{msg}"}), 422

    db = get_db()
    hours = int(value.split(":")[0])
    minutes = int(value.split(":")[1])

    try:
        db.execute(
            f"INSERT INTO {table_name} (hours, minutes) VALUES (?, ?)",
            (hours, minutes)
        )
        db.commit()
    except Exception as e:
        return jsonify({'status': f"Operation failed: {e}"}), 403
    committed_value = db.execute('SELECT *'
                                 f' FROM {table_name}'
                                 ' ORDER BY timestamp DESC').fetchone()
    return jsonify({
        'status': f'{arg_name} successfully set',
        'data': {
            'id': committed_value['id'],
            'hours slept': committed_value['hours'],
            'minutes slept': committed_value['minutes'],
            'timestamp': committed_value['timestamp']
        }
    }), 200


def get_post(id, check_author=True):
    """Get a post and its author by id.

    Checks that the id exists and optionally that the current user is
    the author.

    :param id: id of post to get
    :param check_author: require the current user to be the author
    :return: the post with author information
    :raise 404: if a post with the given id doesn't exist
    :raise 403: if the current user isn't the author
    """
    post = (
        get_db()
            .execute(
            "SELECT p.id, title, body, created, author_id, username"
            " FROM post p JOIN user u ON p.author_id = u.id"
            " WHERE p.id = ?",
            (id,),
        )
            .fetchone()
    )

    if post is None:
        abort(404, f"Post id {id} doesn't exist.")

    if check_author and post["author_id"] != g.user["id"]:
        abort(403)

    return post


@bp.route("/create", methods=("GET", "POST"))
@login_required
def create():
    """Create a new post for the current user."""
    if request.method == "POST":
        title = request.form["title"]
        body = request.form["body"]
        error = None

        if not title:
            error = "Title is required."

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                "INSERT INTO post (title, body, author_id) VALUES (?, ?, ?)",
                (title, body, g.user["id"]),
            )
            db.commit()
            return redirect(url_for("blog.index"))

    return render_template("blog/create.html")


@bp.route("/<int:id>/update", methods=("GET", "POST"))
@login_required
def update(id):
    """Update a post if the current user is the author."""
    post = get_post(id)

    if request.method == "POST":
        title = request.form["title"]
        body = request.form["body"]
        error = None

        if not title:
            error = "Title is required."

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                "UPDATE post SET title = ?, body = ? WHERE id = ?", (title, body, id)
            )
            db.commit()
            return redirect(url_for("blog.index"))

    return render_template("blog/update.html", post=post)


@bp.route("/<int:id>/delete", methods=("POST",))
@login_required
def delete(id):
    """Delete a post.

    Ensures that the post exists and that the logged in user is the
    author of the post.
    """
    get_post(id)
    db = get_db()
    db.execute("DELETE FROM post WHERE id = ?", (id,))
    db.commit()
    return redirect(url_for("blog.index"))
