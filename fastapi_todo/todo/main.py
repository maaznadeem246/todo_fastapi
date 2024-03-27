from typing import Annotated, Optional
from fastapi import FastAPI, Depends
from todo import settings
from contextlib import asynccontextmanager
from sqlmodel import Field, Session, SQLModel, create_engine, select



class Todo(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    content:str = Field(index=True)

print(settings.DATABASE_URL)
connection_string = str(settings.DATABASE_URL).replace(
    'postgresql','postgresql+psycopg'
)


engine = create_engine(
    connection_string,
    # connect_args={"sslmode":"require"}, pool_recycle=300
)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

@asynccontextmanager
async def lifespan(app:FastAPI):
    print("Creating Tables")
    create_db_and_tables()
    yield

app = FastAPI(
        lifespan=lifespan, 
        title="Hello World API with DB",
        version="0.0.1",
        servers=[
            {
                "url":"http://127.0.0.1:8000",
                "description":"Development Server"
            }
        ])

def getSession():
    with Session(engine) as session:
        yield session


@app.get('/')
def read_root():
    return {"Hello":"wolrd"}

@app.post('/todos/',response_model=Todo)
def create_todo(todo:Todo,session:Annotated[Session,Depends(getSession)]):
    session.add(todo)
    session.commit()
    session.refresh()
    return todo

@app.get("/todo/",response_model=list[Todo])
def read_todos(session:Annotated[Session,Depends(getSession)]):
    todos = session.exec(select(Todo)).all()
    return todos

