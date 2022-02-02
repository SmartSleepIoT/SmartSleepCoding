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
        # convert hours to minutes
        times[i] = times[i] * 60

    return times


def get_nr_snores_interval(start_time, end_time):
    all_snores = requests.get('http://127.0.0.1:5000/sleep/all-snores')

    if all_snores.status_code != 200:
        print('Couldn\'t get snores')
        return 0

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

    snores = [0]
    timestamps = [start_time]

    start_time = datetime.strptime(start_time, '%a, %d %b %Y %H:%M:%S %Z')
    end_time = datetime.strptime(end_time, '%a, %d %b %Y %H:%M:%S %Z')

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
        timestamps.append(str_end_timestamp)

        start_timestamp = end_timestamp
        end_timestamp += timedelta(minutes=time_interval)

    return snores, timestamps


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
    snores, timestamps = get_list_snores_small_interval(night[0], night[1])
    return snores, timestamps


def get_heartrate_mean_for_night(i):
    def filter_night(element):
        # element = tuple of 2 elements, (heartrate, night_id)
        return True if night_id == element[1] else False

    all_sleep_intervals = requests.get('http://127.0.0.1:5000/sleep/all-sleep-intervals')
    all_heartrates = requests.get('http://127.0.0.1:5000/sleep/all-heartrates')

    if all_sleep_intervals.status_code != 200:
        print('Error at getting sleep intervals:', all_sleep_intervals.text)
        return 0
    if all_heartrates.status_code != 200:
        print('Error at getting heartrates:', all_heartrates.text)
        return 0

    sleep_data = all_sleep_intervals.json()['status']
    heartrate_data = all_heartrates.json()['status']

    if i >= len(sleep_data) or i < 0:
        return 0

    night = sleep_data[i]
    night_id = night[2]

    # filter the heartrate data
    # so we only have heartrates in the given night
    filtered_heartrate_data = list(filter(
        filter_night,
        heartrate_data
    ))

    hrates = [x for (x, y, z) in filtered_heartrate_data]
    if hrates:
        average = mean(hrates)
    else:
        average = 0

    return average


def get_list_heartrates():
    heartrates = []
    for i in range(get_nr_nights()):
        heartrates.append(get_heartrate_mean_for_night(i))

    return heartrates


def get_heartrate_interval(start_time, end_time):
    def filter_heartrates(element):      # element = (heartrate, timestamp)
        return True if start_time <= element[1] <= end_time else False

    all_heartrates = requests.get('http://127.0.0.1:5000/sleep/all-heartrates')

    if all_heartrates.status_code != 200:
        print('Error at getting heartrates:', all_heartrates.text)
        return 0

    start_time = datetime.strptime(start_time, '%a, %d %b %Y %H:%M:%S %Z')
    end_time = datetime.strptime(end_time, '%a, %d %b %Y %H:%M:%S %Z')

    data = all_heartrates.json()['status']
    heartrates = [(value, datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S'))
                  for (value, sleep_id, timestamp) in data]

    heartrates_filtered = list(filter(filter_heartrates, heartrates))
    heartrates = [value for (value, timestamp) in heartrates_filtered]
    return heartrates


def get_list_heartrates_mean_small_interval(start_time, end_time):
    global time_interval
    start_time = datetime.strptime(start_time, '%a, %d %b %Y %H:%M:%S %Z')
    end_time = datetime.strptime(end_time, '%a, %d %b %Y %H:%M:%S %Z')

    # heartrate == 0   means unknown heartrate
    heartrates = [0]

    # get the heartrates between moment X - time_interval and moment X
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

        heartrate_values = get_heartrate_interval(str_start_timestamp, str_end_timestamp)
        average_heartrate = 0
        if heartrate_values:
            average_heartrate = mean(heartrate_values)

        heartrates.append(average_heartrate)

        start_timestamp = end_timestamp
        end_timestamp += timedelta(minutes=time_interval)

    return heartrates


def get_list_heartrates_mean_for_night(i):
    all_sleep_intervals = requests.get('http://127.0.0.1:5000/sleep/all-sleep-intervals')

    if all_sleep_intervals.status_code != 200:
        print('Error:', all_sleep_intervals.text)
        return []

    data = all_sleep_intervals.json()['status']
    if i >= len(data) or i < 0:
        print('Error: night index not found')
        return []

    night = data[i]
    heartrates = get_list_heartrates_mean_small_interval(night[0], night[1])
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
        apnea_scores.append([0, len(apneas[i])])
        for j in range(len(apneas[i])):
            apnea_scores[i][0] += apnea_score(apneas[i][j])

    return apnea_scores


def get_apnea_score_for_list(lst):
    score = 0
    for apnea in lst:
        score += apnea_score(apnea)

    return score


def get_list_apnea_scores_small_interval(start_time, end_time):
    global time_interval
    start_time = datetime.strptime(start_time, '%a, %d %b %Y %H:%M:%S %Z')
    end_time = datetime.strptime(end_time, '%a, %d %b %Y %H:%M:%S %Z')

    apnea_scores = [[0, 1]]

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

        apneas = get_apnea_interval(str_start_timestamp, str_end_timestamp)
        score = get_apnea_score_for_list(apneas)
        if len(apneas) == 0:
            apnea_scores.append([score, 1])
        else:
            apnea_scores.append([score, len(apneas)])

        start_timestamp = end_timestamp
        end_timestamp += timedelta(minutes=time_interval)

    return apnea_scores


def get_list_apnea_score_for_night(i):
    all_sleep_intervals = requests.get('http://127.0.0.1:5000/sleep/all-sleep-intervals')

    if all_sleep_intervals.status_code != 200:
        print('Error:', all_sleep_intervals.text)
        return []

    data = all_sleep_intervals.json()['status']
    if i >= len(data) or i < 0:
        print('Error: night index not found')
        return []

    night = data[i]
    apneas = get_list_apnea_scores_small_interval(night[0], night[1])
    return apneas


def get_apnea_score_for_night(i):
    apnea_lst = get_list_apnea_score_for_night(i)
    apnea_lst = [x for (x, _) in apnea_lst]
    return sum(apnea_lst)


def apnea_score_normalized(score):
    param_scr = 51 / 3
    # intervals:
    # 0 - 1
    # 1 - 3.5
    # 3.5 - 8
    # 8 - inf

    if 0 <= score <= 1:
        # no apnea
        return param_scr, 'none'
    elif 1 < score <= 3.5:
        # mild apnea
        return 2 * param_scr / 3, 'mild'
    elif 3.5 < score <= 8:
        # moderate apnea
        return param_scr / 3, 'moderate'
    elif 8 < score:
        # severe apnea
        return 0, 'severe'


# sleep quality score for a specified night
def sleepQualityScore(i):
    # get nr of hours slept
    nr_hours_slept = get_nr_hours_slept_night(i)

    # get nr of snores
    snores = get_list_snores()
    if snores:
        nr_snores = snores[i]
    else:
        nr_snores = 0

    # get average heartrate
    avg_heartrate = get_heartrate_mean_for_night(i)

    # get apnea score
    apnea_scr = get_apnea_score_for_night(i)

    # sleep quality ->  a number between 0 and 100 (0 = bad quality, 100 = best quality)
    # time slept -> lowers the sleep quality if its not between 7.5 and 8.5
    # severe apnea  -> lowers the sleep quality
    # heartrate  -> lowers the sleep quality if bigger than 76
    # snores     -> lower the sleep quality if bigger than 10

    sleepQuality = 0

    # sleep contribution
    sleep_score = 49
    if nr_hours_slept < 7.5:
        score = nr_hours_slept * sleep_score / 7.5
    elif nr_hours_slept > 8.5:
        score = 8.5 * sleep_score / nr_hours_slept
    else:
        score = sleep_score
    sleepQuality += score
    print('Time slept score:', score)

    # other params contribution
    param_score = 51 / 3

    # apnea contribution
    apnea_episodes = get_apnea_list()
    if apnea_episodes:
        nr_apnea_episodes = len(apnea_episodes[i])
    else:
        nr_apnea_episodes = 0

    avg_apnea_score = apnea_scr / nr_apnea_episodes
    score, apnea_type = apnea_score_normalized(avg_apnea_score)
    sleepQuality += score
    print('Apnea score:', score, apnea_type)

    # heartrate contribution
    if avg_heartrate < 55:
        score = avg_heartrate * param_score / 55
    elif avg_heartrate > 75:
        score = 75 * param_score / avg_heartrate
    else:
        score = param_score
    sleepQuality += score
    print('Heartrate score:', score)

    # snoring contribution
    max_snores = 10
    if nr_snores <= max_snores:
        score = param_score
    else:
        score = max([0, param_score - (5 / 100 * nr_snores)])
    sleepQuality += score
    print('Snoring score:', score)

    print()

    return sleepQuality


def sleepQualityEachNight():
    sleep_quality_scores = []
    for i in range(get_nr_nights()):
        score = sleepQualityScore(i)
        sleep_quality_scores.append(score)

    return sleep_quality_scores
