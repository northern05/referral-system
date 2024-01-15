import os

from crontab import CronTab
from config import Config

cron = CronTab(user="root")


def setup():
    cwd = os.getcwd()
    print("Setup cron")
    job = cron.new(command=f"/usr/local/bin/python3 {cwd}/scripts/points_poll.py")
    job.minute.every(Config.EVERY_MINUTES)
    print("Created cron job")
    cron.write()
    return "OK"
