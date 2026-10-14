import os
import time

from fastapi_learning.celery_app import celery_app
from fastapi_learning.email_service import send_email

@celery_app.task
def say_hello(name: str):
    print(
        f"任务开始：name={name}，worker PID={os.getpid()}",
        flush=True,
    )

    time.sleep(5)

    print(
        f"任务完成：你好，{name}",
        flush=True,
    )

@celery_app.task
def send_welcome_email(email: str):
    print(f"开始发送欢迎邮件：{email}", flush=True)

    send_email(email)

    print(f"SMTP 邮件提交成功：{email}", flush=True)


@celery_app.task(bind=True, max_retries=2)
def practice_retry(self):
    attempt = self.request.retries + 1

    print(
        f"当前第 {attempt} 次执行",
        flush=True,
    )

    if self.request.retries == 0:
        print("模拟临时网络故障", flush=True)

        raise self.retry(
            exc=ConnectionError("模拟网络中断"),
            countdown=3,
        )

    print("任务执行成功", flush=True)
    return "SUCCESS"



