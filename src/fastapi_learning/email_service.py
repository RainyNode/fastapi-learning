
import os
import ssl
import smtplib

from email.message import EmailMessage
from pathlib import Path

from dotenv import load_dotenv


# 定位项目根目录中的 .env
PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")


def send_email(to_email: str):
    host = os.environ["SMTP_HOST"]
    port = int(os.environ["SMTP_PORT"])
    username = os.environ["SMTP_USER"]
    password = os.environ["SMTP_PASSWORD"]
    sender = os.environ["SMTP_FROM"]

    # 确认 SMTP 邮件地址可以使用 ASCII 编码
    sender.encode("ascii")
    to_email.encode("ascii")

    # 创建邮件
    message = EmailMessage()
    message["From"] = sender
    message["To"] = to_email
    message["Subject"] = "欢迎注册 Todo API"

    message.set_content(
        "欢迎注册 Todo API！\n"
        "你的账号已经创建成功。"
    )

    # 建立 SSL 加密连接
    context = ssl.create_default_context()

    with smtplib.SMTP_SSL(
        host,
        port,
        context=context,
        timeout=10,
    ) as smtp:

        # 使用授权码登录
        smtp.login(username, password)

        # 向 SMTP 服务器提交邮件
        smtp.send_message(message)

