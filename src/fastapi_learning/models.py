from sqlmodel import SQLModel, Field


class Todo(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str
    completed: bool = False


class TodoCreate(SQLModel):
    title: str
    completed: bool = False

class TodoUpdate(SQLModel):
    title: str
    completed: bool

