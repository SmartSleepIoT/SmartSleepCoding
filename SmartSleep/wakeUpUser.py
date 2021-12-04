import apscheduler
from flask.cli import with_appcontext

from SmartSleep.db import get_db
import time
import atexit
import json

from apscheduler.schedulers.background import BackgroundScheduler
from SmartSleep import pubMQTT
from SmartSleep import app

scheduler = BackgroundScheduler()


def wake_up(hours, seconds, mode):
        msg = {'message': "Wake up the user",
               'waking up mode': mode,
               'time': f"{hours}:{seconds}"}, 200

        pubMQTT.publish(json.dumps(msg), "SmartSleep/WakeUp")


def schedule_wake_up(h, min, mode):
        try:
            scheduler.add_job(func=wake_up, args=[h, min, mode], trigger="cron", hour=h, minute=min, id='wake_up_user')
            scheduler.start()
        except apscheduler.schedulers.SchedulerAlreadyRunningError:
            scheduler.reschedule_job(func=wake_up, args=[h, min, mode], trigger="cron", hour=h, minute=min, id='wake_up_user')
        msg = {'message': "Enabling wake up mode"}, 200
        pubMQTT.publish(json.dumps(msg), "SmartSleep/WakeUp")


def delete_wake_up_schedule():
    try:
        scheduler.remove_job('wake_up_user')
        msg = {'message': "Disabling wake up mode"}, 200
        pubMQTT.publish(json.dumps(msg), "SmartSleep/WakeUp")
    except apscheduler.jobstores.base.JobLookupError:
        msg = {'message': "Nothing to disable"}, 200
        pubMQTT.publish(json.dumps(msg), "SmartSleep/WakeUp")

