import pytest
from flask import g
from flask import session
from flask import json
from SmartSleep.db import get_db


def test_register(client, app):
    # test that reistration works
    username = "Radu3"
    password = "123456A"
    response = client.post(f"/auth/register?username={username}&password={password}")
    assert response.status_code == 200

    # test that the user was inserted into the database
    with app.app_context():
        assert (
                get_db().execute(f"SELECT * FROM user WHERE username = '{username}'").fetchone()
                is not None
        )


@pytest.mark.parametrize(
    ("username", "password", "message"),
    (
            ("test1", "1a", "Password too small, must be at least 6 characters long"),
            ("test2", "1234567", "Password must contain at least one upper letter"),
            ("test3", "Atestaaaa", "Password must contain at least one digit"),
    ),
)
def test_register_password_validation(client, username, password, message):
    response = client.post(
        f"/auth/register?username={username}&password={password}"
    )
    assert message in json.loads(response.data)['status']


@pytest.mark.parametrize(
    ("username", "password", "message"),
    (
            ("", "", "Username is required."),
            ("a", "", "Password is required."),
            ("Radu", "12341241241A", "User Radu is already registered."),
    ),
)
def test_register_duplicated_user(client, username, password, message):
    response = client.post(f"/auth/register?username={username}&password={password}")
    assert message in json.loads(response.data)['status']


def test_login(client, auth):
    auth.login()
    # login request set the user_id in the session
    # check that the user is loaded from the session
    with client:
        client.get('/auth/login')
        assert session["user_id"] == 2
        assert g.user["username"] == "Radu"


@pytest.mark.parametrize(
    ("username", "password", "message"),
    (("Radu2", "test",  "Incorrect username."), ("Radu", "12341241241A", "Incorrect password.")),
)
def test_login_validate_input(auth, username, password, message):
    response = auth.login(username, password)
    assert message in json.loads(response.data)['status']


# def test_logout_endpoint(client,auth,subscriber: mqtt_client):
#     def on_message(client, userdata, expectedMsg, msg):
#         assert expectedMsg == msg.payload
#         try:
#             print(f"Received `{json.loads(msg.payload)}` from `{msg.topic}` topic")
#         except:
#             print(f"Received `{msg.payload}` from `{msg.topic}` topic")
#
#     auth.login()
#     subscriber.subscribe("SmartSleep/#")
#     subscriber.on_message = on_message(expectedMsg= "Ana")
#     client.get('/auth/logout')


def test_logout(client, auth):
    auth.login()

    with client:
        auth.logout()
        assert "user_id" not in session
