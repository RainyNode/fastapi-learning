
from celery import Celery

celery_app = Celery(
    "fastapi_learning",
    broker="redis://127.0.0.1:6379/0",
    backend="redis://127.0.0.1:6379/1",
    include=["fastapi_learning.tasks"],
)

celery_app.conf.update(
    task_track_started=True,
    result_expires=3600,
)
