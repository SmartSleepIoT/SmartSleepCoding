import requests
from datetime import datetime


def get_nr_nights():
    nights = requests.get('http://127.0.0.1:5000/sleep/all-time-slept')
    nights = nights.json()
    nights = nights['status']
    return len(nights)


def get_nr_hours_slept_night(i):
    all_time_slept = requests.get('http://127.0.0.1:5000/sleep/all-time-slept')

    if all_time_slept.status_code != 200:
        print('Couldn\'t get hours slept')
        return -1

    data = all_time_slept.json()['status']
    if i >= len(data) or i < 0:
        return -1

    time_slept = data[i]

    hours = time_slept[0]
    minutes = time_slept[1]

    total_time_slept = (hours * 60 + minutes) / 60
    total_time_slept = round(total_time_slept, 2)

    return total_time_slept


def get_list_time_slept():
    all_time_slept = requests.get('http://127.0.0.1:5000/sleep/all-time-slept')

    if all_time_slept.status_code != 200:
        print('Error:', all_time_slept.text)
        return []

    times = all_time_slept.json()['status']
    for i in range(get_nr_nights()):
        times[i] = get_nr_hours_slept_night(i)

    return times


def get_nr_snores_night(start_time, end_time):
    all_snores = requests.get('http://127.0.0.1:5000/sleep/all-snores')

    if all_snores.status_code != 200:
        print('Couldn\'t get snores')
        return -1

    data = all_snores.json()['status']
    dates = [datetime.strptime(snore[1], '%a, %d %b %Y %H:%M:%S %Z') for snore in data]
    in_between_dates = []
    for d in dates:
        if start_time <= d <= end_time:
            in_between_dates.append(d)

    snores = len(in_between_dates)
    return snores


def get_list_snores():
    all_sleep_intervals = requests.get('http://127.0.0.1:5000/sleep/all-sleep-intervals')

    if all_sleep_intervals.status_code != 200:
        print('Error:', all_sleep_intervals.text)
        return []

    snores = []
    sleep_intervals = all_sleep_intervals.json()['status']
    for i in range(get_nr_nights()):
        snores.append(get_nr_snores_night(datetime.strptime(sleep_intervals[i][0], '%a, %d %b %Y %H:%M:%S %Z'),
                                          datetime.strptime(sleep_intervals[i][1], '%a, %d %b %Y %H:%M:%S %Z')))

    return snores


times_slept_list = get_list_time_slept()
print(times_slept_list)

snores_list = get_list_snores()
print(snores_list)
