
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, Session, create_engine

from fastapi_learning.main import app
from fastapi_learning.models import Todo
from fastapi_learning import main


# 1. 使用独立的内存数据库
test_engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)


# 2. 创建测试数据库中的表
SQLModel.metadata.create_all(test_engine)

# 让 API 使用测试数据库
main.engine = test_engine

client = TestClient(app)


# 3. 每个测试使用不同的数据记录

def test_create_todo():
    response = client.post(
        "/todos",
        json={"title": "测试创建", "completed": False},
    )

    assert response.status_code == 201
    assert response.json()["title"] == "测试创建"
    assert response.json()["id"] is not None


def test_get_todos():
    response = client.get("/todos")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_todo():
    with Session(test_engine) as session:
        todo = Todo(title="测试单条查询")
        session.add(todo)
        session.commit()
        session.refresh(todo)
        todo_id = todo.id

    response = client.get(f"/todos/{todo_id}")

    assert response.status_code == 200
    assert response.json()["title"] == "测试单条查询"


def test_update_todo():
    with Session(test_engine) as session:
        todo = Todo(title="更新前")
        session.add(todo)
        session.commit()
        session.refresh(todo)
        todo_id = todo.id

    response = client.put(
        f"/todos/{todo_id}",
        json={"title": "更新后", "completed": True},
    )

    assert response.status_code == 200
    assert response.json()["title"] == "更新后"
    assert response.json()["completed"] is True


def test_delete_todo():
    with Session(test_engine) as session:
        todo = Todo(title="等待删除")
        session.add(todo)
        session.commit()
        session.refresh(todo)
        todo_id = todo.id

    response = client.delete(f"/todos/{todo_id}")

    assert response.status_code == 204

    check = client.get(f"/todos/{todo_id}")
    assert check.status_code == 404
