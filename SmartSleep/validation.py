def wake_up_time_validation(time):
    if ":" not in time:
        return False, "incorrect time format try hour:min"
    hour = time.split(":")[0]
    min = time.split(":")[1]
    if int(hour) not in range(0, 24):
        return False, "incorrect hour format, hour must be between 0-23"
    if int(min) not in range(0, 60):
        return False, "incorrect min format, hour minutes be between 00-61"

    return True, ""
