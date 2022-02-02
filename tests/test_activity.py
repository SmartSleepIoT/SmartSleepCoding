import flask
import pytest
from flask import json
from SmartSleep.validation import deep_datetime_validation
from SmartSleep.db import get_db


@pytest.mark.parametrize(
    ("heartrate", "time"),
    (
            ("", "23:20:04"),
            ("67", ""),
            ("79", "23:20:04"),
            ("abc", "23:20:04"),
            (-12, "23:20:04"),
            (70, "23:20:04"),
    )
)
def test_set_heartrate(client, auth, heartrate, time):
    auth.login()

    response = client.post(f'activity/heartrate?heartrate={heartrate}&time={time}')
    r_dict = json.loads(response.data)

    if not heartrate:
        assert response.status_code == 403
        assert "heartrate is required." in r_dict['status']
    elif not time:
        assert response.status_code == 403
        assert "time is required." in r_dict['status']
    else:
        client.post("http://127.0.0.1:5000/config/start_to_sleep?sleep_now=True")
        response = client.post(f'activity/heartrate?heartrate={heartrate}&time={time}')
        r_dict = json.loads(response.data)
        if str(heartrate).isnumeric() and int(heartrate) > 0:
            assert response.status_code == 200
            assert "Heartrate successfully recorded" in r_dict['status']
        else:
            assert "Heartrate must be a positive integer number" in r_dict['status']


@pytest.mark.parametrize(
    ("stage", "time"),
    (
            ("", "20:00:00"),
            ("REM", ""),
            ("LIGHT", "2021-01-02 00:34:00"),
            ("DEEP", "23:20"),
            (-12, "2021-12-12 23:20:04")
    )
)
def test_set_sleep_stage(client, auth, stage, time):
    auth.login()
    client.post("http://127.0.0.1:5000/config/start_to_sleep?sleep_now=True")
    response = client.post(f'activity/sleep_stage?stage={stage}&time={time}')
    r_dict = json.loads(response.data)
    if not stage:
        assert response.status_code == 403
        assert "stage is required" in r_dict['status']
    elif not time:
        assert response.status_code == 403
        assert "time is required" in r_dict['status']
    else:
        posssible_values=['LIGHT', 'DEEP', 'REM']
        is_valid, msg = deep_datetime_validation(time)
        if stage in posssible_values:
            if is_valid:
                assert response.status_code == 200
                assert "stage successfully set" in r_dict['status']
            else:
                assert response.status_code == 422
                assert msg in r_dict['status']
        else:
            assert response.status_code == 403

def test_get_sleep_stage(client, auth):
    auth.login()
    response = client.get('/activity/sleep_stage')
    assert response.status_code == 200