import json
import time


def test_all(client, auth):
    auth.login()

    paths = [
        'sleep/all-time-slept',
        'sleep/all-snores',
        'sleep/all-sleep-intervals',
        'sleep/all-heartrates',
        'sleep/all-apneas'
    ]

    client.post('config/start_to_sleep?sleep_now=True')
    time.sleep(2)
    client.post('config/start_to_sleep?sleep_now=False')
    client.post('config/time_slept?time=5:23')
    time.sleep(2)
    client.post('config/start_to_sleep?sleep_now=True')
    client.post('activity/heartrate?heartrate=67&time=23:23:23')
    client.post('config/snoring?snore_now=True')
    client.post('config/apnea?apnea=severe')

    for i in range(len(paths)):
        path = paths[i]

        response = client.get(path)
        r_dict = json.loads(response.data)

        if "Operation failed" in r_dict['status']:
            assert response.status_code == 403
        else:
            assert response.status_code == 200
