import pytest
from flask import json

from SmartSleep.db import get_db


def test_current_config_empty(client, auth):
    auth.login()
    response = client.get("http://127.0.0.1:5000/config/")
    assert response.status_code == 200

    r_dict = json.loads(response.data)
    assert "Configuration successfully retrieved" in r_dict['status']
    for inner_dict in r_dict['data'].values():
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
    r_dict = json.loads(response.data)

    assert "Configuration successfully retrieved" in r_dict['status']
    for inner_dict in r_dict['data'].items():
        print(inner_dict)
        if "temperature" == inner_dict[0]:
            assert inner_dict[1]['value'] == sent_value
        else:
            assert inner_dict[1]['value'] == "Not set"


# Test endpoints can be accessed
@pytest.mark.parametrize(
    "path",
    ("/temp",
     "/waking_mode",
     "/pillow_angle",
     "/wake_up_hour",
     "/start_to_sleep",
     "/time_slept")
)
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
    with app.app_context():
        db = get_db()
        auth.login()
        inserted = False

        # get the last inserted value, if exists
        # used for start_to_sleep
        # 1. user cannot wake up if he didn't sleep
        # 2. user cannot set the same value 2 times consecutively
        db_value = db.execute('SELECT *'
                              f' FROM {table_name}'
                              ' ORDER BY timestamp DESC').fetchone()

        response = client.post(f"/config{path}?{arg_name}={value}")
        r_dict = json.loads(response.data)

        if table_name == "time_slept":
            h = value.split(":")[0]
            mins = value.split(":")[1]
            assert r_dict['data']['hours slept'] == int(h)
            assert r_dict['data']['minutes slept'] == int(mins)
        elif table_name == "start_to_sleep":
            # if the very first insert is False/0 (user wakes up)
            if db_value is None and str(value).lower() in ['0', 'false']:
                assert "Operation failed: Cannot wake up if you didn't sleep before" == r_dict['status']
            # if the very first insert is True/1 (user goes to sleep)
            elif db_value is None:
                assert f'{arg_name} successfully set' in r_dict['status']
            # if the user sets a new sleep state
            else:
                # cannot set the same value as the previous one
                if db_value['value'] == value:
                    assert "Operation failed: Already set this value" == r_dict['status']
                else:
                    assert f'{arg_name} successfully set' in r_dict['status']
                    inserted = True
        else:
            assert r_dict['data']['value'] == value

        # Check that the value was inserted correctly
        if inserted:
            db_value = db.execute(f"SELECT * FROM {table_name}").fetchone()
            if path == "/start_to_sleep":
                val = str(value)
                if val.lower() in ["true", "1"]:
                    assert db_value['value'] == 1
                else:
                    assert db_value['value'] == 0

            elif path == "/time_slept":
                h = value.split(":")[0]
                mins = value.split(":")[1]
                assert db_value['hours'] == int(h)
                assert db_value['minutes'] == int(mins)

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
            ("/time_slept", "time_slept", "time"),
            ("/sound", "sounds_recorded", "sensor")
    ),
)
def test_set_required_param(client, auth, path, table_name, arg_name):  # tests POST with missing required params
    auth.login()
    response = client.post(f"/config{path}?{arg_name}=")
    assert response.status_code == 403
    r_dict = json.loads(response.data)
    assert f'{arg_name} is required' in r_dict['status']


@pytest.mark.parametrize(
    ("path", "table_name", "arg_name", "value"),
    (
            ("/waking_mode", "waking_mode", "waking_mode", "X"),
            ("/waking_mode", "waking_mode", "waking_mode", "VM"),
     )
)
# tests POST with wrong values for waking_mode
def test_set_waking_mode_validations(client, auth, path, table_name, arg_name, value):
    auth.login()
    response = client.post(f"/config{path}?{arg_name}={value}")
    assert response.status_code == 422
    r_dict = json.loads(response.data)
    assert f"{arg_name} must be one of the following ['L', 'V', 'S', 'LVS', 'LV', 'LS', 'VS']" in r_dict['status']


@pytest.mark.parametrize(
    ("path", "table_name", "arg_name", "value"),
    (
            ("/pillow_angle", "pillow_angle", "pillow_angle", False),
            ("/pillow_angle", "pillow_angle", "pillow_angle", "ana"),
            ("/pillow_angle", "pillow_angle", "pillow_angle", [0, 1, 2]),
            ("/sound", "sounds_recorded", "sensor", False),
            ("/sound", "sounds_recorded", "sensor", "ana"),
            ("/sound", "sounds_recorded", "sensor", [0, 1, 2]),
    )
)
# tests POST with wrong values for pillow_angle and sound
def test_set_float_validations(client, auth, path, table_name, arg_name, value):
    auth.login()
    response = client.post(f"/config{path}?{arg_name}={value}")
    assert response.status_code == 422
    r_dict = json.loads(response.data)
    assert "Wrong angle format, must be float number " in r_dict['status']


@pytest.mark.parametrize(
    ("path", "table_name", "arg_name", "value"),
    (
            ("/wake_up_hour", "wake_up_hour", "wake_up_hour", "24:00"),
            ("/wake_up_hour", "wake_up_hour", "wake_up_hour", 10),
            ("/wake_up_hour", "wake_up_hour", "wake_up_hour", "10"),
            ("/wake_up_hour", "wake_up_hour", "wake_up_hour", "12:63"),
            ("/time_slept", "time_slept", "time", "24:00"),
            ("/time_slept", "time_slept", "time", 10),
            ("/time_slept", "time_slept", "time", "10"),
            ("/time_slept", "time_slept", "time", "12:63"),
    )
)
# tests POST with wrong values for waking hour/ time slept
def test_set_time_validations(client, auth, path, table_name, arg_name, value):
    auth.login()
    response = client.post(f"/config{path}?{arg_name}={value}")
    assert response.status_code == 422
    r_dict = json.loads(response.data)

    if value == "24:00":
        assert "Incorrect hour format, hour must be between 0-23" in r_dict['status']
    elif value == 10 or value == "10":
        assert "Incorrect time format try hour:min" in r_dict["status"]
    elif value == "12:61":
        assert "Incorrect min format, hour minutes be between 00-59" in r_dict["status"]


@pytest.mark.parametrize(
    ("path", "table_name", "arg_name", "value"),
    (
            ("/start_to_sleep", "start_to_sleep", "sleep_now", 10),
            ("/start_to_sleep", "start_to_sleep", "sleep_now", "ana"),
            ("/start_to_sleep", "start_to_sleep", "sleep_now", "da"),
    )
)
# tests POST with wrong values for start to sleep
def test_set_start_to_sleep_validations(client, auth, path, table_name, arg_name, value):
    auth.login()
    response = client.post(f"/config{path}?{arg_name}={value}")
    assert response.status_code == 422
    r_dict = json.loads(response.data)
    assert "wrong value must be one of: true, false, 0, 1" in r_dict['status']


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
