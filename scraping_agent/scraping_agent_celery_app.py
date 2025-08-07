from celery import Celery
from kombu import Queue

celery_app = Celery(
    "scrapingagent",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0"
)

celery_app.conf.task_queues = [
    Queue("scrape_high"),
    Queue("scrape_medium"),
    Queue("scrape_low"),
]

celery_app.conf.task_default_queue = "scrape_medium"

import celery_worker.tasks
