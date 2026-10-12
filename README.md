# FastAPI Learning — Todo API

基于 FastAPI、SQLModel、SQLite 和 uv 开发的简单 Todo REST API 项目。

## 技术栈

- Python（版本以 `.python-version` 为准）
- FastAPI
- SQLModel
- SQLite
- pytest + httpx
- uv

## 目录结构

```text
fastapi-learning/
├── src/
│   └── fastapi_learning/
│       ├── __init__.py
│       ├── main.py
│       ├── models.py
│       └── database.py
├── tests/
│   └── test_todos.py
├── pyproject.toml
├── uv.lock
└── README.md
```

## 环境准备

安装 uv 后进入项目根目录：

```bash
uv sync --locked
```

## 启动项目

```bash
uv run uvicorn fastapi_learning.main:app --reload
```

访问：

- API：http://127.0.0.1:8000
- Swagger：http://127.0.0.1:8000/docs
- OpenAPI：http://127.0.0.1:8000/openapi.json

首次启动将自动创建 SQLite 数据表。

## API 接口

| 方法 | 路径 | 功能 |
|---|---|---|
| POST | `/todos` | 创建待办 |
| GET | `/todos` | 查询所有待办 |
| GET | `/todos/{id}` | 根据 ID 查询 |
| PUT | `/todos/{id}` | 更新待办 |
| DELETE | `/todos/{id}` | 删除待办 |

创建待办示例：

```json
{
  "title": "学习 FastAPI",
  "completed": false
}
```

## 运行测试

```bash
uv run python -m pytest -q
```

项目包含五个 CRUD 基础测试，测试使用独立的 SQLite 内存数据库。

## 项目说明

本项目用于学习 Python Web 后端基础，包括路由、请求体校验、ORM、SQLite 持久化、HTTP 状态码与自动化测试。

当前不包含登录认证、分页、前端和生产环境部署。
