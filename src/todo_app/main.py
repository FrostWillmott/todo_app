from fastapi import FastAPI, Request, status
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from todo_app.database import Base, engine
from todo_app.routers import admin, auth, todos, users

app = FastAPI()

Base.metadata.create_all(bind=engine)


app.mount(
    "/static", StaticFiles(directory="src/todo_app/static"), name="static"
)


@app.get("/")
def test(request: Request):
    return RedirectResponse(
        url="/todos/todo-page", status_code=status.HTTP_302_FOUND
    )


@app.get("/healthy")
def health_check():
    return {"status": "healthy"}


app.include_router(auth.router)
app.include_router(todos.router)
app.include_router(admin.router)
app.include_router(users.router)
