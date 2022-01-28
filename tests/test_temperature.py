from flask import json


def test_warm_cool_temperature(client, auth):
    auth.login()

    response = client.get('temperature/warm-temperature')
    r_dict = json.loads(response.data)
    assert response.status_code == 404
    assert "user is not sleeping" in r_dict['status']

    response = client.get('temperature/cool-temperature')
    r_dict = json.loads(response.data)
    assert response.status_code == 404
    assert "user is not sleeping" in r_dict['status']

    # now set sleep_now
    client.post("config/start_to_sleep?sleep_now=True")

    response = client.get('temperature/warm-temperature')
    r_dict = json.loads(response.data)
    assert response.status_code == 200
    assert "New temperature system level set" in r_dict['status']

    response = client.get('temperature/cool-temperature')
    r_dict = json.loads(response.data)
    assert response.status_code == 200
    assert "New temperature system level set" in r_dict['status']
