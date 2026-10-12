from sqlmodel import SQLModel, create_engine, Session
from fastapi_learning.models import Todo

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