from apscheduler.schedulers.background import BackgroundScheduler
from .jops import schedule, monitor

def my_scheduled_job():
    scheduler = BackgroundScheduler()

    # Schedule the jobs
    scheduler.add_job(schedule, 'interval', minutes=30, id='schedule_job')
    scheduler.add_job(monitor, 'interval', minutes=4, id='monitor_job')

    scheduler.start()
