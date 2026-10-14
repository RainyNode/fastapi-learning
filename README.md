# FastAPI Todo API + Celery 欢迎邮件

## 项目简介

基于 FastAPI、SQLModel、SQLite、Redis 和 Celery 实现的用户注册、JWT 登录、Todo 管理与欢迎邮件后台任务系统。

用户成功注册后，FastAPI 将用户写入 SQLite，并向 Redis 发布欢迎邮件任务；独立的 Celery Worker 负责调用 SMTP 邮件服务，注册接口不等待邮件发送完成。

## 技术栈

- Python 3.12
- FastAPI：HTTP API
- SQLModel + SQLite：数据库
- JWT：用户认证
- Redis：Celery Broker 与 Result Backend
- Celery：后台任务
- SMTP：网易 163 邮件发送
- uv：依赖与项目环境管理

## 本地启动

以下命令从项目根目录执行。

1. 安装依赖：`uv sync`
2. 根据 `.env.example` 创建本地 `.env` 并填写自己的配置
3. 确保 Redis 服务正常运行：`redis-cli ping`
4. 启动 Worker：`uv run celery -A fastapi_learning.celery_app:celery_app worker --loglevel=info`
5. 启动 FastAPI：`uv run uvicorn fastapi_learning.main:app --reload --host 127.0.0.1 --port 8000`
6. 打开 `http://127.0.0.1:8000/docs`

## 核心接口

- `POST /register`：注册用户，提交欢迎邮件任务
- `POST /login`：登录并获得 JWT
- `GET /users/me`：查询当前登录用户
- `/todos`：Todo 管理接口

## 后台邮件流程

1. FastAPI 验证注册信息
2. SQLite 提交用户记录
3. FastAPI 向 Redis 发布 Celery 任务
4. Worker 获取任务并连接 SMTP 服务器
5. SMTP 服务器接受邮件提交
6. Celery 保存任务执行结果

## 注意事项

- 邮件发送失败不应撤销已经成功提交的注册记录
- 注册成功不等于邮件送达
- SMTP 授权码和 JWT 密钥仅保存在本地
- 已有 SQLite 数据库需要进行对应的表结构迁移，不能通过直接删库替代
- Result Backend 结果可能过期
- 有限重试与严格防重复发送能力仍需进一步验证和完善

## 已知限制

这是学习项目，不作为生产级邮件系统使用。尚未完整实现事务性 Outbox、可靠去重、邮件验证、持久进程管理等功能。
