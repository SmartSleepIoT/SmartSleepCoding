from flask import Blueprint, jsonify
from flask import flash
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from werkzeug.exceptions import abort

from SmartSleep.auth import login_required
from SmartSleep.db import get_db

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
        temp = "Not set"
    if waking_mode is None:
        waking_mode = "Not set"
    if wake_up_hour is None:
        wake_up_hour = "Not set"
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
    """Get / Set waking_mode"""
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
            return jsonify({'status': f"{arg_name} must be one of the following {waking_modes}"}), 403
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


@bp.route("/wake_up_hour", methods=["GET", "POST", "DELETE"])
@login_required
def waking_hour():
    """Get / Set wake_up_hour"""
    table_name = "wake_up_hour"
    arg_name = "wake_up_hour"
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