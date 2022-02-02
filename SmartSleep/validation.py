

def time_validation(time):
    if ":" not in time:
        return False, "Incorrect time format try hour:min"
    hour = time.split(":")[0]
    min = time.split(":")[1]
    if int(hour) not in range(0, 24):
        return False, "Incorrect hour format, hour must be between 0-23"
    if int(min) not in range(0, 60):
        return False, "Incorrect min format, minutes must be between 00-59"
    return True, ""

def deep_time_validation(time):
    if not isinstance(time, str) or time.count(":") !=2:
        return False, "Incorrect time format try hour:min:seconds"
    hour, min, seconds = time.split(":")
    if int(hour) not in range(0, 24):
        return False, "Incorrect hour format, hour must be between 0-23"
    if int(min) not in range(0, 60):
        return False, "Incorrect min format, minutes must be between 00-59"
    if int(seconds) not in range(0, 60):
        return False, "Incorrect seconds format, seconds must be between 00-59"
    return True, ""
    
def date_validation(date):
    if not isinstance(date, str) or date.count("-") !=2:
        return False, "Incorrect time format try yyyy-mm-dd"
    year, month, day = date.split("-")
    if int(year) not in range(1970, 2023):
        return False, "Incorrect year format, year must be between 1970 and 2022"
    if int(month) not in range(0, 13):
        return False, "Incorrect month format, month must be between 00 and 12"
    if int(day) not in range(0, 32):
        return False, "Incorrect day format, day must be between 00-31"
    return True, ""
    
def deep_datetime_validation(datetime):
    if " " not in datetime:
        return False, "Incorrect datetime format try yyyy-mm-dd hour:min:seconds"
    date, time = datetime.split()
    valid_date, msg = date_validation(date)
    if not valid_date:
        return valid_date, msg
    return deep_time_validation(time)

def password_validation(password):
    if len(password) < 6:
        return False, "Password too small, must be at least 6 characters long"
    if not any(c.isupper() for c in password):
        return False, "Password must contain at least one upper letter"
    if not any(c.isdigit() for c in password):
        return False, "Password must contain at least one digit"

    return True, ""


def boolean_validation(val):
    if val.lower() in ['true', '1']:
        return True, "true"
    if val.lower() in ['0', 'false']:
        return True, "false"
    return False, "wrong value must be one of: true, false, 0, 1"
