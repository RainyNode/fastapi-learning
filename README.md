# FastAPI Learning — JWT Todo API

一个基于 FastAPI、SQLModel、SQLite 和 JWT 的多用户待办事项管理后端。

本项目使用 uv 管理 Python 环境和依赖，实现用户注册、登录、身份认证和用户间 Todo 数据隔离。

## 1. 技术栈

- Python 3.12
- FastAPI
- SQLModel
- SQLite
- PyJWT
- pwdlib + Argon2
- pytest + httpx
- uv

## 2. 项目结构

```text
fastapi-learning/
├── src/fastapi_learning/
│   ├── __init__.py
│   ├── main.py
│   ├── models.py
│   ├── database.py
│   ├── security.py
│   └── auth.py
├── tests/
│   ├── test_todos.py
│   └── test_auth.py
├── .env.example
├── pyproject.toml
├── uv.lock
└── README.md
```

## 3. 环境准备

安装 uv 后进入项目根目录。

安装依赖：

```bash
uv sync --locked
```

配置本地环境变量：

```bash
cp .env.example .env
```

Windows PowerShell 可使用：

```powershell
Copy-Item .env.example .env
```

使用 Python 生成随机密钥：

```bash
uv run python -c "import secrets; print(secrets.token_urlsafe(32))"
```

将生成的密钥填入 `.env` 中的 `JWT_SECRET_KEY`。

不要将真实密钥提交到 Git。

## 4. 启动服务

```bash
uv run uvicorn fastapi_learning.main:app --reload
```

Swagger API 文档：

http://127.0.0.1:8000/docs

OpenAPI 描述：

http://127.0.0.1:8000/openapi.json

首次启动时，应用会创建缺失的 SQLite 数据表。

## 5. API 接口

| 方法 | 地址 | 功能 | 认证 |
|---|---|---|---|
| POST | /register | 注册 | 否 |
| POST | /login | 登录 | 否 |
| GET | /users/me | 当前用户 | 是 |
| POST | /todos | 创建待办 | 是 |
| GET | /todos | 查询自己的待办 | 是 |
| GET | /todos/{id} | 查询指定待办 | 是 |
| PUT | /todos/{id} | 更新待办 | 是 |
| DELETE | /todos/{id} | 删除待办 | 是 |

## 6. 使用流程

首先调用 `/register` 注册用户：

```json
{
  "username": "alice",
  "password": "MyPassword123!"
}
```

随后调用 `/login`：

```json
{
  "username": "alice",
  "password": "MyPassword123!"
}
```

登录成功后，服务器返回 JWT：

```json
{
  "access_token": "<JWT>",
  "token_type": "bearer"
}
```

访问受保护接口时，请在 HTTP 请求头中添加：

```http
Authorization: Bearer <JWT>
```

例如创建 Todo：

```json
{
  "title": "学习 FastAPI",
  "completed": false
}
```

服务器自动将该 Todo 绑定到当前登录用户。

## 7. 自动化测试

运行当前认证与隔离测试：

```bash
uv run python -m pytest tests/test_auth.py -q
```

当前包含七个基础测试函数，覆盖注册、重复用户名、登录、错误密码、未认证访问、当前用户以及跨用户资源访问。

测试使用独立的 SQLite 内存数据库。

原 `tests/test_todos.py` 属于项目 1 的 CRUD 测试，尚未适配新增的 JWT 认证。

## 8. 当前安全机制

- Argon2 密码哈希
- JWT 签名与过期时间验证
- 用户存在性检查
- Todo.user_id 所有权约束
- 跨用户读取、修改与删除拦截
- 开发数据库与认证测试数据库隔离

## 9. 已知限制

当前为教学项目，不应直接部署到公网生产环境。

尚未实现：

- 登录与注册限流
- JWT 主动撤销和刷新令牌
- 账户禁用及密码重置
- 数据库迁移
- 完整测试生命周期隔离
- 生产环境 TLS、部署与审计日志

本项目主要用于学习后端认证、授权和数据持久化的核心流程。
