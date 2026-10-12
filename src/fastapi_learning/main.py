from contextlib import asynccontextmanager
from http.client import HTTPException

from fastapi import FastAPI,HTTPException
from sqlmodel import Session, select

from fastapi_learning.database import create_db_and_tables, engine
from fastapi_learning.models import Todo, TodoCreate, TodoUpdate


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/")
def home():
    return {"message": "Todo API is running"}


@app.post("/todos", response_model=Todo, status_code=201)
def create_todo(todo: TodoCreate):
    db_todo = Todo.model_validate(todo)

    with Session(engine) as session:
        session.add(db_todo)
        session.commit()
        session.refresh(db_todo)

    return db_todo

@app.get("/todos", response_model=list[Todo])
def get_todos():
    with Session(engine) as session:
        todos = session.exec(select(Todo)).all()

    return todos

@app.get("/todos/{id}", response_model=Todo)
def get_todo(id: int):
    with Session(engine) as session:
        todo = session.get(Todo, id)

        if todo is None:
            raise HTTPException(
                status_code=404,
                detail="Todo not found"
            )

        return todo

@app.put("/todos/{id}", response_model=Todo)
def update_todo(id: int, data: TodoUpdate):
    with Session(engine) as session:
        todo = session.get(Todo, id)

        if todo is None:
            raise HTTPException(
                status_code=404,
                detail="Todo not found"
            )

        todo.title = data.title
        todo.completed = data.completed

        session.add(todo)
        session.commit()
        session.refresh(todo)

        return todo

@app.delete("/todos/{id}", status_code=204)
def delete_todo(id: int):
    with Session(engine) as session:
        todo = session.get(Todo, id)

        if todo is None:
            raise HTTPException(
                status_code=404,
                detail="Todo not found"
            )

        session.delete(todo)
        session.commit()

