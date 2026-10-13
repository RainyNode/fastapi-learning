from typing import Annotated

from fastapi import Depends
from sqlmodel import SQLModel, Session, create_engine

from fastapi_learning.models import Todo, User

# 数据库连接地址
DATABASE_URL = "sqlite:///todo.db"

# 创建数据库引擎
engine = create_engine(
    DATABASE_URL,
    echo=True
)

# 创建数据库表
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


# FastAPI 依赖：为每个请求提供一个独立的 Session，请求结束后自动关闭
def get_session():
    with Session(engine) as session:
        yield session


DbSession = Annotated[Session, Depends(get_session)]
