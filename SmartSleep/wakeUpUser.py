import apscheduler
import json

from apscheduler.schedulers.background import BackgroundScheduler
from SmartSleep import pubMQTT


class WakeUpScheduler:
    hours = "00"
    minutes = "00"
    waking_mode = "LS"
    scheduler = BackgroundScheduler()

    def setter(self, hours, minutes, mode):
        self.hours = hours
        self.minutes = minutes
        self.waking_mode = mode

    def wake_up(self):
        msg = {'message': "Wake up the user",
               'waking up mode': self.waking_mode,
               'time': f"{self.hours}:{self.minutes}"}, 200
        pubMQTT.publish(json.dumps(msg), "SmartSleep/WakeUp")

    def schedule_wake_up(self, h, min, mode):
        try:
            self.setter(h, min, mode)
            self.scheduler.add_job(func=self.wake_up, trigger="cron", hour=h, minute=min, id='wake_up_user')
            self.scheduler.start()
        except (apscheduler.schedulers.SchedulerAlreadyRunningError, apscheduler.jobstores.base.ConflictingIdError):
            self.setter(h, min, mode)
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