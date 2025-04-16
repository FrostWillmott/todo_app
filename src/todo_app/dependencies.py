from typing import Annotated

from fastapi.params import Depends
from sqlalchemy.orm import Session
from starlette.templating import Jinja2Templates

from todo_app.database import SessionLocal


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]

templates = Jinja2Templates(directory="src/todo_app/templates")
