from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.exc import IntegrityError
from sqlmodel import select

from fastapi_learning.auth import get_current_user
from fastapi_learning.database import DbSession, create_db_and_tables
from fastapi_learning.models import (
    Todo,
    TodoCreate,
    TodoUpdate,
    Token,
    User,
    UserCreate,
    UserPublic,
)
from fastapi_learning.security import (
    create_access_token,
    hash_password,
    verify_password,
)
from fastapi_learning.tasks import send_welcome_email

import logging

from kombu.exceptions import OperationalError

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

CurrentUser = Annotated[
    User,
    Depends(get_current_user),
]
app = FastAPI(lifespan=lifespan)


@app.get("/")
def home():
    return {"message": "Todo API is running"}


@app.post("/todos", response_model=Todo, status_code=201)
def create_todo(
    todo: TodoCreate,
    current_user: CurrentUser,
    session: DbSession,
):
    db_todo = Todo.model_validate(todo)
    db_todo.user_id = current_user.id

    session.add(db_todo)
    session.commit()
    session.refresh(db_todo)

    return db_todo

@app.get("/todos", response_model=list[Todo])
def get_todos(
    current_user: CurrentUser,
    session: DbSession,
):
    todos = session.exec(
        select(Todo).where(
            Todo.user_id == current_user.id
        )
    ).all()

    return todos

@app.get("/todos/{id}", response_model=Todo)
def get_todo(
    id: int,
    current_user: CurrentUser,
    session: DbSession,
):
    todo = session.exec(
        select(Todo).where(
            Todo.id == id,
            Todo.user_id == current_user.id,
        )
    ).first()

    if todo is None:
        raise HTTPException(
            status_code=404,
            detail="Todo not found",
        )

    return todo

@app.put("/todos/{id}", response_model=Todo)
def update_todo(
    id: int,
    data: TodoUpdate,
    current_user: CurrentUser,
    session: DbSession,
):
    todo = session.exec(
        select(Todo).where(
            Todo.id == id,
            Todo.user_id == current_user.id,
        )
    ).first()

    if todo is None:
        raise HTTPException(
            status_code=404,
            detail="Todo not found",
        )

    todo.title = data.title
    todo.completed = data.completed

    session.add(todo)
    session.commit()
    session.refresh(todo)

    return todo

@app.delete("/todos/{id}", status_code=204)
def delete_todo(
    id: int,
    current_user: CurrentUser,
    session: DbSession,
):
    todo = session.exec(
        select(Todo).where(
            Todo.id == id,
            Todo.user_id == current_user.id,
        )
    ).first()

    if todo is None:
        raise HTTPException(
            status_code=404,
            detail="Todo not found",
        )

    session.delete(todo)
    session.commit()


@app.post("/register", response_model=UserPublic, status_code=201)
def register(
    data: UserCreate,
    session: DbSession,
):
    existing_user = session.exec(
        select(User).where(User.username == data.username)
    ).first()

    if existing_user is not None:
        raise HTTPException(
            status_code=409,
            detail="Username already exists",
        )

    user = User(
        username=data.username,
        hashed_password=hash_password(data.password),
        email=str(data.email),
    )

    session.add(user)

    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=409,
            detail="Username already exists",
        )

    session.refresh(user)

    # 数据库提交成功后，再发布欢迎邮件任务
    try:
        send_welcome_email.apply_async(
            args=[user.email],
            retry=False,
        )
    except OperationalError:
        logging.exception(
            "Welcome email task publication failed for user_id=%s",
            user.id,
        )

    return user


@app.post("/login", response_model=Token)
def login(
    session: DbSession,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
):
    user = session.exec(
        select(User).where(User.username == form_data.username)
    ).first()

    if user is None or not verify_password(
            form_data.password,
            user.hashed_password,
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password",
        )

    token = create_access_token(user.id)

    return Token(
        access_token=token,
        token_type="bearer",
    )

@app.get("/users/me", response_model=UserPublic)
def read_current_user(
    current_user: Annotated[User, Depends(get_current_user)],
):
    return current_user


@app.post("/practice/welcome-email", status_code=202)
def practice_welcome_email(
    current_user: CurrentUser,
):
    result = send_welcome_email.delay(
        "demo@example.com"
    )

    return {
        "message": "欢迎邮件任务已提交",
        "task_id": result.id,
    }
