import requests
from datetime import datetime
from datetime import timedelta
from statistics import mean

time_interval = 2   # minutes


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


def get_nr_snores_interval(start_time, end_time):
    all_snores = requests.get('http://127.0.0.1:5000/sleep/all-snores')

    if all_snores.status_code != 200:
        print('Couldn\'t get snores')
        return -1

    start_time = datetime.strptime(start_time, '%a, %d %b %Y %H:%M:%S %Z')
    end_time = datetime.strptime(end_time, '%a, %d %b %Y %H:%M:%S %Z')

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
        snores.append(get_nr_snores_interval(sleep_intervals[i][0],
                                             sleep_intervals[i][1]))

    return snores


def get_list_snores_small_interval(start_time, end_time):
    global time_interval
    start_time = datetime.strptime(start_time, '%a, %d %b %Y %H:%M:%S %Z')
    end_time = datetime.strptime(end_time, '%a, %d %b %Y %H:%M:%S %Z')

    snores = [0]

    # get the nr of snores between moment X - time_interval and moment X
    start_timestamp = start_time
    end_timestamp = start_time + timedelta(minutes=time_interval)

    while start_timestamp <= end_time:
        str_start_timestamp = start_timestamp.strftime('%a, %d %b %Y %H:%M:%S %Z')
        str_end_timestamp = end_timestamp.strftime('%a, %d %b %Y %H:%M:%S %Z')

        # add the GMT if it doesnt exist
        if str_start_timestamp.find("GMT") == -1:
            str_start_timestamp += " GMT"
        if str_end_timestamp.find("GMT") == -1:
            str_end_timestamp += " GMT"

        snore = get_nr_snores_interval(str_start_timestamp, str_end_timestamp)
        snores.append(snore)

        start_timestamp = end_timestamp
        end_timestamp += timedelta(minutes=time_interval)

    return snores


def get_list_snore_for_night(i):
    all_sleep_intervals = requests.get('http://127.0.0.1:5000/sleep/all-sleep-intervals')

    if all_sleep_intervals.status_code != 200:
        print('Error:', all_sleep_intervals.text)
        return []

    data = all_sleep_intervals.json()['status']
    if i >= len(data) or i < 0:
        print('Error: night index not found')
        return []

    night = data[i]
    snores = get_list_snores_small_interval(night[0], night[1])
    return snores


def get_heartrate_mean_for_night(i):
    def filter_night(element):
        # element = tuple of 2 elements, (heartrate, night_id)
        return True if night_id == element[1] else False

    all_sleep_intervals = requests.get('http://127.0.0.1:5000/sleep/all-sleep-intervals')
    all_heartrates = requests.get('http://127.0.0.1:5000/sleep/all-heartrates')

    if all_sleep_intervals.status_code != 200:
        print('Error at getting sleep intervals:', all_sleep_intervals.text)
        return -1
    if all_heartrates.status_code != 200:
        print('Error at getting heartrates:', all_heartrates.text)
        return -1

    sleep_data = all_sleep_intervals.json()['status']
    heartrate_data = all_heartrates.json()['status']

    if i >= len(sleep_data) or i < 0:
        return -1

    night = sleep_data[i]
    night_id = night[2]

    # filter the heartrate data
    # so we only have heartrates in the given night
    filtered_heartrate_data = list(filter(
        filter_night,
        heartrate_data
    ))

    hrates = [x for (x, y) in filtered_heartrate_data]
    if hrates:
        average = mean(hrates)
    else:
        average = -1

    return average


def get_list_heartrates():
    heartrates = []
    for i in range(get_nr_nights()):
        heartrates.append(get_heartrate_mean_for_night(i))

    return heartrates


def apnea_score(apnea_type):
    if apnea_type == 'mild':
        return 2
    if apnea_type == 'moderate':
        return 5
    if apnea_type == 'severe':
        return 11
    return 0


def get_apnea_interval(start_time, end_time):
    def filter_apnea(element):      # element = (apnea_value, timestamp)
        return True if start_time <= element[1] <= end_time else False

    all_apneas = requests.get('http://127.0.0.1:5000/sleep/all-apneas')

    if all_apneas.status_code != 200:
        print('Couldn\'t get apneas:', all_apneas.text)
        return []

    start_time = datetime.strptime(start_time, '%a, %d %b %Y %H:%M:%S %Z')
    end_time = datetime.strptime(end_time, '%a, %d %b %Y %H:%M:%S %Z')

    data = all_apneas.json()['status']
    apnea_dates = [(value, datetime.strptime(timestamp, '%a, %d %b %Y %H:%M:%S %Z')) for (value, timestamp) in data]

    apnea_filtered = list(filter(filter_apnea, apnea_dates))
    apnea_statuses = [value for (value, timestamp) in apnea_filtered]
    return apnea_statuses


def get_apnea_list():
    all_sleep_intervals = requests.get('http://127.0.0.1:5000/sleep/all-sleep-intervals')

    if all_sleep_intervals.status_code != 200:
        print('Error:', all_sleep_intervals.text)
        return []

    all_sleep_intervals = all_sleep_intervals.json()['status']
    apneas = []
    for i in range(get_nr_nights()):
        apneas.append(get_apnea_interval(
            all_sleep_intervals[i][0],
            all_sleep_intervals[i][1]
        ))

    return apneas


def get_list_apnea_scores():
    apneas = get_apnea_list()

    apnea_scores = []
    for i in range(get_nr_nights()):
        apnea_scores.append(0)
        for j in range(len(apneas[i])):
            apnea_scores[i] += apnea_score(apneas[i][j])

    return apnea_scores


print('-------------- PARAMETER INFORMATION FOR ONE NIGHT, SPLIT INTO SMALL INTERVALS --------------')
print('SNORES')
print(get_list_snore_for_night(2))

print('HEARTRATE')

print('APNEA')


print('-------------- PARAMETER INFORMATION FOR EACH NIGHT, MULTIPLE NIGHTS --------------')

print('TIMES SLEPT')
times_slept_list = get_list_time_slept()
print(times_slept_list)

print('SNORES')
snores_list = get_list_snores()
print(snores_list)

print('HEARTRATES')
heartrates_list = get_list_heartrates()
print(heartrates_list)

print('APNEA')
apnea_list = get_list_apnea_scores()
print(apnea_list)
