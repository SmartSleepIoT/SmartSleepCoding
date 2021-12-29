from datetime import datetime

import apscheduler
import json

import requests
from apscheduler.schedulers.background import BackgroundScheduler
from SmartSleep import pubMQTT


class WakeUpScheduler:
    hours = "00"
    minutes = "00"
    waking_mode = "LS"
    scheduler = BackgroundScheduler({'apscheduler.timezone': 'Europe/Bucharest'})

    def setter(self, hours, minutes, mode, started_to_sleep_time):
        self.hours = hours
        self.minutes = minutes
        self.waking_mode = mode
        self.started_to_sleep = started_to_sleep_time

    def set_time_slept(self):
        current_time = f"{self.hours}:{self.minutes}"
        time_slept = datetime.strptime(current_time, "%H:%M") - datetime.strptime(self.started_to_sleep, "%H:%M")
        total_sec = time_slept.total_seconds()
        h = int(total_sec // 3600)
        min = int((total_sec % 3600) // 60)
        r = requests.post(f"http://127.0.0.1:5000/config/time_slept?time={h}:{min}")
        if r.status_code == 200:
            msg = {'message': f"User slept for {h} hours and {min} minutes"}, 200
            pubMQTT.publish(json.dumps(msg), "SmartSleep/WakeUp")


    def wake_up(self):
        msg = {'message': "Wake up the user",
               'waking up mode': self.waking_mode,
               'time': f"{self.hours}:{self.minutes}"}, 200
        pubMQTT.publish(json.dumps(msg), "SmartSleep/WakeUp")
        self.set_time_slept()

    def schedule_wake_up(self, interval, mode, started_to_sleep_time, optimal = False):
        try:
            if optimal: 
                start, end = interval
                msg = {'start': start,
                       'end': end, 
                       'start_to_sleep': started_to_sleep_time}
                pubMQTT.publish(json.dumps(msg), "SmartSleep/OptimalWakeup")
            else:
                (h, min) = interval[0]
                self.setter(h, min, mode, started_to_sleep_time)
                self.scheduler.add_job(func=self.wake_up, trigger="cron", hour=h, minute=min, id='wake_up_user')
                self.scheduler.start()
        except (apscheduler.schedulers.SchedulerAlreadyRunningError, apscheduler.jobstores.base.ConflictingIdError):
            if not optimal: 
                self.setter(h, min, mode, started_to_sleep_time)
                self.scheduler.reschedule_job(trigger="cron", hour=h, minute=min, job_id='wake_up_user')
                msg = {'message': "Enabling wake up mode"}, 200
                pubMQTT.publish(json.dumps(msg), "SmartSleep/WakeUp")
                
    def delete_wake_up_schedule(self):
        try:
            self.scheduler.remove_job('wake_up_user')
            msg = {'message': "Disabling wake up mode"}, 200
            pubMQTT.publish(json.dumps(msg), "SmartSleep/WakeUp")
        except apscheduler.jobstores.base.JobLookupError:
            msg = {'message': "Nothing to disable"}, 200
            pubMQTT.publish(json.dumps(msg), "SmartSleep/WakeUp")