from fastapi import APIRouter, HTTPException, Path, Request, status
from fastapi.params import Cookie, Depends
from pydantic import BaseModel, Field
from starlette.responses import RedirectResponse

from todo_app.dependencies import db_dependency, templates
from todo_app.models import Todos
from todo_app.routers.auth import get_current_user
from todo_app.routers.users import user_dependency

router = APIRouter(
    prefix="/todos",
    tags=["todos"],
)


class TodoRequest(BaseModel):
    """Schema for creating or updating a todo item."""

    title: str = Field(min_length=3)
    description: str = Field(min_length=3, max_length=100)
    priority: int = Field(gt=0, lt=6)
    complete: bool


def redirect_to_login():
    """Redirect the user to the login page and delete the access token cookie."""
    redirect_response = RedirectResponse(
        url="/auth/login-page", status_code=status.HTTP_302_FOUND
    )
    redirect_response.delete_cookie(key="access_token")
    return redirect_response


### Pages ###
async def get_current_user_or_redirect(access_token: str = Cookie(None)):
    """Retrieve the current user or redirect to the login page if the user is not authenticated."""
    if access_token is None:
        return redirect_to_login()
    try:
        user = await get_current_user(access_token)
        return user
    except HTTPException:
        return redirect_to_login()


@router.get("/todo-page")
async def render_todo_page(
    request: Request,
    db: db_dependency,
    user: dict = Depends(get_current_user_or_redirect),
):
    """Render the todo page for the authenticated user."""
    try:
        todos = db.query(Todos).filter(Todos.owner_id == user.get("id")).all()
        return templates.TemplateResponse(
            "todo.html", {"request": request, "todos": todos, "user": user}
        )
    except:
        return redirect_to_login()


@router.get("/add-todo-page")
async def render_add_todo_page(
    request: Request, user: dict = Depends(get_current_user_or_redirect)
):
    """Render the add-todo page for the authenticated user."""
    try:
        return templates.TemplateResponse(
            "add-todo.html", {"request": request, "user": user}
        )
    except:
        return redirect_to_login()


@router.get("/edit-todo-page/{todo_id}")
async def render_edit_todo_page(
    request: Request,
    todo_id: int,
    db: db_dependency,
    user: dict = Depends(get_current_user_or_redirect),
):
    """Render the edit-todo page for the authenticated user."""
    try:
        todo = db.query(Todos).filter(Todos.id == todo_id).first()
        return templates.TemplateResponse(
            "edit-todo.html", {"request": request, "todo": todo, "user": user}
        )
    except:
        return redirect_to_login()


### Endpoints ###
@router.get("/", status_code=status.HTTP_200_OK)
async def read_all(user: user_dependency, db: db_dependency):
    """Retrieve all todo items for the authenticated user."""
    return db.query(Todos).filter(Todos.owner_id == user.get("id")).all()


@router.get("/todo/{todo_id}", status_code=status.HTTP_200_OK)
async def read_todo(
    user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)
):
    """Retrieve a specific todo item by ID for the authenticated user."""
    todo_model = (
        db.query(Todos)
        .filter(Todos.id == todo_id)
        .filter(Todos.owner_id == user.get("id"))
        .first()
    )
    if todo_model is not None:
        return todo_model
    raise HTTPException(status_code=404, detail="Todo not found.")


@router.post("/todo", status_code=status.HTTP_201_CREATED)
async def create_todo(
    user: user_dependency, db: db_dependency, todo_request: TodoRequest
):
    """Create a new todo item for the authenticated user."""
    todo_model = Todos(**todo_request.model_dump(), owner_id=user.get("id"))
    db.add(todo_model)
    db.commit()


@router.put("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(
    user: user_dependency,
    db: db_dependency,
    todo_request: TodoRequest,
    todo_id: int = Path(gt=0),
):
    """Update an existing todo item for the authenticated user."""
    todo_model = (
        db.query(Todos)
        .filter(Todos.id == todo_id)
        .filter(Todos.owner_id == user.get("id"))
        .first()
    )
    if todo_model is None:
        raise HTTPException(status_code=404, detail="Todo not found.")
    todo_model.title = todo_request.title
    todo_model.description = todo_request.description
    todo_model.priority = todo_request.priority
    todo_model.complete = todo_request.complete
    db.add(todo_model)
    db.commit()


@router.delete("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(
    user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)
):
    """Delete a specific todo item by ID for the authenticated user."""
    todo_model = (
        db.query(Todos)
        .filter(Todos.id == todo_id, Todos.owner_id == user.get("id"))
        .first()
    )
    if todo_model is None:
        raise HTTPException(status_code=404, detail="Todo not found.")
    db.delete(todo_model)
    db.commit()
