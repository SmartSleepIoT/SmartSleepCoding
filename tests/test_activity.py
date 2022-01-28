import flask
import pytest
from flask import json

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
