from sqlmodel import SQLModel, Field
from pydantic import EmailStr

class Todo(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str
    completed: bool = False
    user_id: int | None = Field(
        default=None,
        foreign_key="user.id"
    )


class TodoCreate(SQLModel):
    title: str
    completed: bool = False

class TodoUpdate(SQLModel):
    title: str
    completed: bool

class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    hashed_password: str
    email: str | None = Field(default=None)

class UserCreate(SQLModel):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=8, max_length=128)
    email: EmailStr


class UserPublic(SQLModel):
    id: int
    username: str

class UserLogin(SQLModel):
    username: str
    password: str


class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"