import subprocess
import os

from apscheduler.schedulers.background import (
    BackgroundScheduler
)

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

UPDATE_SCRIPT = os.path.join(
    BASE_DIR,
    "scripts",
    "update_jobs.py"
)

def run_job_update():

    print("Running scheduled update...")

    subprocess.run([
        "python",
        UPDATE_SCRIPT
    ])


scheduler = BackgroundScheduler()

scheduler.add_job(

    run_job_update,

    "interval",

    hours=24

)

scheduler.start()

print("Scheduler started...")