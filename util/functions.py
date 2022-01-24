from datetime import datetime

def set_hour_and_minute(time):
    now = datetime.now()
    current_time = datetime.strptime(time, "%H:%M:%S")
    current_date = now.replace(hour = current_time.hour, minute = current_time.minute)
    return current_date.strftime("%Y-%m-%d %H:%M:%S")

def str_to_datetime(str_time):
    return datetime.strptime(str_time, '%Y-%m-%d %H:%M:%S')
