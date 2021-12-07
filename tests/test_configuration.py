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
@pytest.mark.parametrize("path", ("/temp", "/waking_mode", "/pillow_angle", "/wake_up_hour", "/start_to_sleep", "/time_slept"))
def test_get(client, auth, path):  # tests SET
    auth.login()
    response = client.get("config" + path)
    assert response.status_code == 200


@pytest.mark.parametrize(
    ("path", "table_name", "arg_name", "value"),
    (
            ("/temp", "temperature", "temperature", 23.4),
            ("/temp", "temperature", "temperature", 23),
            ("/temp", "temperature", "temperature", -1),
            ("/temp", "temperature", "temperature", -1.54),

            ("/waking_mode", "waking_mode", "waking_mode", "L"),
            ("/waking_mode", "waking_mode", "waking_mode", "V"),
            ("/waking_mode", "waking_mode", "waking_mode", "S"),
            ("/waking_mode", "waking_mode", "waking_mode", "LVS"),
            ("/waking_mode", "waking_mode", "waking_mode", "LV"),
            ("/waking_mode", "waking_mode", "waking_mode", "LS"),
            ("/waking_mode", "waking_mode", "waking_mode", "VS"),

            ("/pillow_angle", "pillow_angle", "pillow_angle", 54),
            ("/pillow_angle", "pillow_angle", "pillow_angle", 30.5),
            ("/pillow_angle", "pillow_angle", "pillow_angle", 10),
            ("/pillow_angle", "pillow_angle", "pillow_angle", 0),

            ("/wake_up_hour", "wake_up_hour", "wake_up_hour", "8:23"),
            ("/wake_up_hour", "wake_up_hour", "wake_up_hour", "08:23"),
            ("/wake_up_hour", "wake_up_hour", "wake_up_hour", "15:00"),
            ("/wake_up_hour", "wake_up_hour", "wake_up_hour", "23:59"),

            ("/start_to_sleep", "start_to_sleep", "sleep_now", "True"),
            ("/start_to_sleep", "start_to_sleep", "sleep_now", "False"),
            ("/start_to_sleep", "start_to_sleep", "sleep_now", "true"),
            ("/start_to_sleep", "start_to_sleep", "sleep_now", "false"),
            ("/start_to_sleep", "start_to_sleep", "sleep_now", 1),
            ("/start_to_sleep", "start_to_sleep", "sleep_now", 0),

            ("/time_slept", "time_slept", "time", "10:20"),
            ("/time_slept", "time_slept", "time", "01:00"),
            ("/time_slept", "time_slept", "time", "0:35")
    ),
)
def test_set(client, auth, app, path, table_name, arg_name, value):  # tests POST with correct values
    auth.login()
    response = client.post(f"/config{path}?{arg_name}={value}")
    rDict = json.loads(response.data)
    assert f'{arg_name} successfully set' in rDict['status']
    if table_name == "time_slept":
        h = value.split(":")[0]
        min = value.split(":")[1]
        assert rDict['data']['hours slept'] == int(h)
        assert rDict['data']['minutes slept'] == int(min)
    elif table_name == "start_to_sleep":
        val = str(value)
        if val.lower() in ["true", "1"]:
            assert rDict['data']['value'] == 1
        else:
            assert rDict['data']['value'] == 0
    else:
        assert rDict['data']['value'] == value

    # Check that the value was inserted correctly
    with app.app_context():
        db = get_db()
        db_value = db.execute(f"SELECT * FROM {table_name}").fetchone()
        if path == "/start_to_sleep":
            val = str(value)
            if val.lower() in ["true", "1"]:
                assert db_value['value'] == 1
            else:
                assert db_value['value'] == 0

        elif path == "/time_slept":
            h = value.split(":")[0]
            min = value.split(":")[1]
            assert db_value['hours'] == int(h)
            assert db_value['minutes'] == int(min)

        else:
            assert db_value['value'] == value


@pytest.mark.parametrize(
    ("path", "table_name", "arg_name"),
    (
            ("/temp", "temperature", "temperature"),
            ("/start_to_sleep", "start_to_sleep", "sleep_now"),
            ("/wake_up_hour", "wake_up_hour", "wake_up_hour"),
            ("/waking_mode", "waking_mode", "waking_mode"),
            ("/pillow_angle", "pillow_angle", "pillow_angle"),
            ("/time_slept", "time_slept", "time")
    ),
)
def test_set_required_param(client, auth, path, table_name, arg_name):  # tests POST with missing required params
    auth.login()
    response = client.post(f"/config{path}?{arg_name}=")
    assert response.status_code == 403
    rDict = json.loads(response.data)
    assert f'{arg_name} is required' in rDict['status']


@pytest.mark.parametrize(
    ("path", "table_name"),
    (
            ("/temp", "temperature"),
            ("/waking_mode", "waking_mode"),
            ("/pillow_angle", "pillow_angle"),
            ("/wake_up_hour", "wake_up_hour"),
            ("/start_to_sleep", "start_to_sleep"),
            ("/time_slept", "time_slept"),
            ("/pillow_angle", "pillow_angle"),

    ),
)
def test_delete(client, auth, app, path, table_name):  # tests DELETE
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
