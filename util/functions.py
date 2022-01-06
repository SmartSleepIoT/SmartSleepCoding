from datetime import datetime

def datetime_to_pair(time, start_time):
    current_time = datetime.strptime(time,"%H:%M:%S")
    time_diff_in_seconds = (current_time - start_time).seconds
    hours = time_diff_in_seconds//3600
    minutes = (time_diff_in_seconds//60)%60
    return hours, minutes