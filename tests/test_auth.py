
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, Session, create_engine

from fastapi_learning.main import app
from fastapi_learning.database import get_session


# 1. 独立内存数据库
test_engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)


def get_test_session():
    with Session(test_engine) as session:
        yield session


# 2. 创建测试表，替换数据库依赖
SQLModel.metadata.create_all(test_engine)
app.dependency_overrides[get_session] = get_test_session

client = TestClient(app)


def register(username, password="Password123!"):
    return client.post(
        "/register",
        json={"username": username, "password": password},
    )


def login(username, password="Password123!"):
    response = client.post(
        "/login",
        json={"username": username, "password": password},
    )
    return response


def auth_headers(token):
    return {"Authorization": f"Bearer {token}"}


def test_register():
    response = register("user_register")
    assert response.status_code == 201
    assert response.json()["username"] == "user_register"
    assert "hashed_password" not in response.json()


def test_duplicate_register():
    register("user_duplicate")
    response = register("user_duplicate")
    assert response.status_code == 409


def test_login():
    register("user_login")
    response = login("user_login")
    assert response.status_code == 200
    assert response.json()["access_token"]


def test_wrong_password():
    register("user_wrong")
    response = login("user_wrong", "WrongPassword!")
    assert response.status_code == 401


def test_unauthorized():
    response = client.get("/todos")
    assert response.status_code == 401


def test_current_user():
    register("user_me")
    token = login("user_me").json()["access_token"]

    response = client.get(
        "/users/me",
        headers=auth_headers(token),
    )

    assert response.status_code == 200
    assert response.json()["username"] == "user_me"


def test_user_isolation():
    # 创建两个用户
    register("alice_test")
    register("bob_test")

    alice_token = login("alice_test").json()["access_token"]
    bob_token = login("bob_test").json()["access_token"]

    # Alice 创建自己的 Todo
    created = client.post(
        "/todos",
        json={"title": "Alice Private Todo"},
        headers=auth_headers(alice_token),
    )

    assert created.status_code == 201
    todo_id = created.json()["id"]

    # Alice 可以访问
    own = client.get(
        f"/todos/{todo_id}",
        headers=auth_headers(alice_token),
    )
    assert own.status_code == 200

    # Bob 无权读取
    denied = client.get(
        f"/todos/{todo_id}",
        headers=auth_headers(bob_token),
    )
    assert denied.status_code == 404

    # Bob 无权修改
    denied_update = client.put(
        f"/todos/{todo_id}",
        json={"title": "Hacked", "completed": True},
        headers=auth_headers(bob_token),
    )
    assert denied_update.status_code == 404

    # Bob 无权删除
    denied_delete = client.delete(
        f"/todos/{todo_id}",
        headers=auth_headers(bob_token),
    )
    assert denied_delete.status_code == 404

    # Alice 的 Todo 仍然存在
    still_exists = client.get(
        f"/todos/{todo_id}",
        headers=auth_headers(alice_token),
    )
    assert still_exists.status_code == 200
    assert still_exists.json()["title"] == "Alice Private Todo"
