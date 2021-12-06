import pytest
from flask import json

from SmartSleep.db import get_db


def test_current_config_empty(client, auth):
    auth.login()
    response = client.get("http://127.0.0.1:5000/config/")
    assert response.status_code == 200

    rDict = json.loads(response.data)
    assert "Configuration successfully retrieved" in rDict['status']
    for inner_dict in rDict['data'].values():
        for value in inner_dict.values():
            assert value == "Not set"


def test_current_config_after_insert(client, auth):
    auth.login()

    sent_value = 24
    # Insert value into DB
    response = client.post(f"/config/temp?temperature={sent_value}")
    assert response.status_code == 200

    # Get config
    response = client.get("http://127.0.0.1:5000/config/")
    assert response.status_code == 200
    rDict = json.loads(response.data)

    assert "Configuration successfully retrieved" in rDict['status']
    for inner_dict in rDict['data'].items():
        print(inner_dict)
        if "temperature" == inner_dict[0]:
            assert inner_dict[1]['value'] == sent_value
        else:
            assert inner_dict[1]['value'] == "Not set"


# Test endpoints can be accessed
@pytest.mark.parametrize("path", ("/temp", "/waking_mode", "/pillow_angle", "/wake_up_hour"))
def test_get(client, auth, path):
    auth.login()
    response = client.get("config" + path)
    assert response.status_code == 200


@pytest.mark.parametrize(
    ("path", "table_name", "arg_name", "value"),
    (
            ("/temp", "temperature", "temperature", 23.4),
            ("/waking_mode", "waking_mode", "waking_mode", "L"),
            ("/pillow_angle", "pillow_angle", "pillow_angle", 54),
            ("/wake_up_hour", "wake_up_hour", "wake_up_hour", "8:23")
    ),
)
def test_set(client, auth, app, path, table_name, arg_name, value):
    auth.login()
    response = client.post(f"/config{path}?{arg_name}={value}")
    rDict = json.loads(response.data)
    assert f'{arg_name} successfully set' in rDict['status']
    assert rDict['data']['value'] == value

    # Check that the value was inserted correctly
    with app.app_context():
        db = get_db()
        db_value = db.execute(f"SELECT * FROM {table_name}").fetchone()
        assert db_value['value'] == value


@pytest.mark.parametrize(
    ("path", "table_name"),
    (
            ("/temp", "temperature"),
            ("/waking_mode", "waking_mode"),
            ("/pillow_angle", "pillow_angle"),
            ("/wake_up_hour", "wake_up_hour")
    ),
)
def test_delete(client, auth, app, path, table_name):
    auth.login()
    response = client.delete(f"config" + path)
    # Check that response was successful
    assert response.status_code == 200
    with app.app_context():
        db = get_db()
        value = db.execute(f"SELECT * FROM {table_name}").fetchone()
        assert value is None


@pytest.mark.parametrize("path", ("/", "/temp", "/waking_mode", "/pillow_angle", "/wake_up_hour"))
def test_login_required(client, path):
    response = client.get("/config" + path)
    assert response.status_code == 403
