from flask import (
    Blueprint, request, jsonify
)
from SmartSleep.auth import login_required

from db import get_db

bp = Blueprint('activity', __name__, url_prefix="/activity")

@bp.route('/heartrate', methods=['POST'])
@login_required
def set_heartrate():
    """
    Set/record the heartrate received by the heartrate sensor
    """
    heartrate = request.args.get('heartrate')
    time = request.args.get('time')
    error = None

    if not heartrate:
        return jsonify({'status': 'heartrate is required.'}), 403
    if not time:
        return jsonify({'status': 'time is required.'}), 403
    db = get_db()
    try:
        current_sleep = db.execute(
        'SELECT *'
        ' FROM start_to_sleep'
        ' ORDER BY id DESC'
        ).fetchone()['id']
        
        db.execute(
            'INSERT INTO heartrate (heartrate, sleep, time) '
            ' VALUES (?, ?, ?)',
            (heartrate,current_sleep, time)
        )
        db.commit()
    except Exception as e:
        return jsonify({'status': f"Operation failed: {e}"}), 403
    
    commited_value = db.execute(
        'SELECT *'
        ' FROM heartrate'
        ' ORDER BY id DESC'
    ).fetchone()
    return jsonify({
        'status': 'Heartrate succesfully recorded',
        'data': {
            'id': commited_value['id'],
            'heartrate': commited_value['heartrate'],
            'time': commited_value['time']
         }}), 200