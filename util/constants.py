
"""
A dictionary for enumering all stages of sleep
"""
SLEEP_STAGES = {
    'LIGHT': 'LIGHT',
    'DEEP': 'DEEP',
    'REM': 'REM'
}

"""
A dictionary for setting the mimimum known duration for the sleep stages
"""
MIN_STAGE_DURATION = {
    'LIGHT': 15,
    'DEEP': 30,
    'REM': 8
}

"""
Topics we are subscribing/publishing to
"""
TOPIC = {
    'START_TO_SLEEP' : "SmartSleep/StartSleeping",
    'HEARTRATE': "SmartSleep/Heartrate"
}

"""
A dictionary having the following format:
    age: [minimum hours of sleep, maximum hours of sleep]
"""
SLEEP_NEEDED = {
    '3': (10, 14),
    '5': (10, 13),
    '12': (9, 12),
    '18': (8, 10),
    '60': (7, 9),
    '100': (7, 8)
}