from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.jobstores.mongodb import MongoDBJobStore
from pymongo import MongoClient
from pymongo.errors import OperationFailure
import time

app = Flask(__name__)

client = MongoClient("", tlsAllowInvalidCertificates=True)
db = client["test"]
collection = db["schedules"]

def my_scheduled_job(job_id):
    print(f"Executing job {job_id}", flush=True)

def update_schedules(scheduler):
    jobs = collection.find({"status": "pending"})
    for job in jobs:
        job_id = job.get("job_id")
        cron_expression =  job.get("cron_expression")
        if cron_expression:
            cron_parts = cron_expression.split()
            if len(cron_parts) == 5:
                print("Adding job", job_id, "with cron", cron_expression)
                scheduler.add_job(
                    my_scheduled_job,
                    "cron",
                    id=job_id,
                    args=[job_id],
                    replace_existing=True,
                    minute=cron_parts[0],
                    hour=cron_parts[1],
                    day=cron_parts[2],
                    month=cron_parts[3],
                    day_of_week=cron_parts[4]
                )
                collection.update_one({"job_id": job_id}, {"$set": {"status": "scheduled"}})
                print("Job added")

jobstores = {
    "default": MongoDBJobStore(database="test", collection="cron-schedules", client=client)
}

executors = {
    "default": ThreadPoolExecutor(20)
}

scheduler = BackgroundScheduler(jobstores=jobstores, executors=executors)
scheduler.start()

update_schedules(scheduler)


try: 
    while True:
        pass
except KeyboardInterrupt:
    scheduler.shutdown()