import functools

from flask import Blueprint, jsonify, url_for
from flask import g
from flask import request
from flask import session
from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash
from werkzeug.utils import redirect

from SmartSleep.db import get_db

bp = Blueprint("auth", __name__, url_prefix="/auth")


def login_required(view):
    """View decorator that redirects anonymous users to the login page."""

    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return jsonify({'status': "User is not authenticated"}), 403

        return view(**kwargs)

    return wrapped_view


@bp.before_app_request
def load_logged_in_user():
    """If a user id is stored in the session, load the user object from
    the database into ``g.user``."""
    user_id = session.get("user_id")

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute("SELECT * FROM user WHERE id = ?", (user_id,)).fetchone()


@bp.route("/register", methods=["GET", "POST"])
def register():
    """Register a new user.

    Validates that the username is not already taken. Hashes the
    password for security.
    """
    if request.method == "POST":
        username = request.args.get("username")
        password = request.args.get("password")
        db = get_db()

        if not username:
            return jsonify({'status': "Username is required"}), 403
        elif not password:
            return jsonify({'status': "Password is required"}), 403

        try:
            db.execute(
                "INSERT INTO user (username, password) VALUES (?, ?)",
                (username, generate_password_hash(password)))
            db.commit()
        except db.IntegrityError:
            # The username was already taken, which caused the
            # commit to fail. Show a validation error.
            return jsonify({'status': f"User {username} is already registered."}), 403
        # Success, go to the login page.
        return jsonify({'status': "User registered successfully"}), 200


@bp.route("/login", methods=["POST"])
def login():
    """Log in a registered user by adding the user id to the session."""
    username = request.args.get("username")
    password = request.args.get("password")
    db = get_db()
    error = None
    user = db.execute(
        "SELECT * FROM user WHERE username = ?", (username,)
    ).fetchone()

    if user is None:
        error = "Incorrect username."
    elif not check_password_hash(user["password"], password):
        error = "Incorrect password."

    if error is None:
        # Store the user id in a new session and return to the index
        session.clear()
        session["user_id"] = user["id"]
        return jsonify({'status': "User logged in successfully"}), 200

    return jsonify({'status': error}), 403


@bp.route("/logout")
def logout():
    """Clear the current session, including the stored user id."""
    session.clear()
    return jsonify({'status': "User logged out successfully"}), 200
