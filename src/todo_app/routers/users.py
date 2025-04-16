from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from todo_app.dependencies import db_dependency
from todo_app.models import Users
from todo_app.routers.auth import bcrypt_context, get_current_user

router = APIRouter(
    prefix="/user",
    tags=["user"],
)

user_dependency = Annotated[dict, Depends(get_current_user)]


class UsersVerification(BaseModel):
    password: str
    new_password: str = Field(min_length=6, max_length=100)


class UsersPhoneVerification(BaseModel):
    new_phone_number: str = Field(min_length=6, max_length=50)


def get_authenticated_user(user: dict, db: Session):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed")
    user_model = db.query(Users).filter(Users.id == user.get("id")).first()
    if user_model is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user_model


@router.get("/", status_code=status.HTTP_200_OK)
async def get_user(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed")
    return db.query(Users).filter(Users.id == user.get("id")).first()


@router.put("/password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(
    user: user_dependency,
    db: db_dependency,
    user_verification: UsersVerification,
):
    user_model = get_authenticated_user(user, db)

    if not bcrypt_context.verify(
        user_verification.password, user_model.hashed_password
    ):
        raise HTTPException(status_code=401, detail="Wrong password!")

    user_model.hashed_password = bcrypt_context.hash(
        user_verification.new_password
    )
    db.add(user_model)
    db.commit()


@router.put("/phone_number", status_code=status.HTTP_204_NO_CONTENT)
async def change_phone_number(
    user: user_dependency,
    db: db_dependency,
    user_user_phone_number: UsersPhoneVerification,
):
    user_model = get_authenticated_user(user, db)

    user_model.phone_number = user_user_phone_number.new_phone_number
    db.add(user_model)
    db.commit()
