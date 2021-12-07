def time_validation(time):
    if ":" not in time:
        return False, "Incorrect time format try hour:min"
    hour = time.split(":")[0]
    min = time.split(":")[1]
    if int(hour) not in range(0, 24):
        return False, "Incorrect hour format, hour must be between 0-23"
    if int(min) not in range(0, 60):
        return False, "Incorrect min format, hour minutes be between 00-59"

    return True, ""


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
