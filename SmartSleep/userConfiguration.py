from flask import Blueprint, jsonify
from flask import request
from flask import session

from SmartSleep.auth import login_required
from SmartSleep.db import get_db

bp = Blueprint("userConfig", __name__, url_prefix="/user")


@bp.route("/age", methods=["GET", "POST"])
@login_required
def config_age():
    db = get_db()
    table_name = "user"
    arg_name = "age"
    user_id = session.get("user_id")

    if request.method == "GET":
        try:
            current_value = db.execute('SELECT username, age'
                                       f' FROM {table_name}'
                                       f' WHERE id = {user_id}').fetchone()

            if not current_value['age']:
                raise Exception(f'{arg_name} not set')

            return jsonify({
                'status': f'{arg_name} successfully retrieved',
                'data': {
                    'userid': user_id,
                    'username': current_value['username'],
                    'age': current_value['age']
                }
            }), 200
        except Exception as e:
            return jsonify({
                'status': f'Operation failed: {e}'
            }), 403

    if request.method == "POST":
        try:
            value = request.args.get(arg_name)

            if not value:
                raise Exception(f'{arg_name} is required')

            value = int(value)

            if value < 1 or value > 100:
                raise Exception(f'{arg_name} must be between 1 and 100')

            db.execute(f'UPDATE {table_name}'
                       f' SET {arg_name} = {value}'
                       f' WHERE id = {user_id}')
            db.commit()

            return jsonify({
                'status': f'{arg_name} successfully set',
                'data': {
                    'userid': user_id,
                    'age': value
                }
            }), 200
        except ValueError:
            return jsonify({
                'status': f'{arg_name} must be a positive integer number'
            }), 403
        except Exception as e:
            return jsonify({
                'status': f'Operation failed: {e}'
            }), 403
