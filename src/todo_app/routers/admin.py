from fastapi import APIRouter, HTTPException, Path, status

from todo_app.dependencies import db_dependency
from todo_app.models import Todos
from todo_app.routers.users import user_dependency

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
)


@router.get("/todo", status_code=status.HTTP_200_OK)
async def read_all(user: user_dependency, db: db_dependency):
    """Retrieve all todo items. Only accessible by admin users."""
    if user is None or user.get("user_role") != "admin":
        raise HTTPException(status_code=401, detail="Authentication failed")
    return db.query(Todos).all()


@router.delete("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(
    user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)
):
    """Delete a specific todo item by ID. Only accessible by admin users."""
    if user is None or user.get("user_role") != "admin":
        raise HTTPException(status_code=401, detail="Authentication failed")
    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    db.delete(todo_model)
    db.commit()
