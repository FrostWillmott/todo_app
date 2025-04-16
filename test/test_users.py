from fastapi import status

from test.utils import *
from todo_app.routers.auth import bcrypt_context


def test_return_user(test_user):
    response = client.get("/user")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["username"] == "test_username"
    assert response.json()["first_name"] == "test_first_name"
    assert response.json()["last_name"] == "test_last_name"
    assert response.json()["email"] == "test@email.com"
    assert response.json()["role"] == "admin"
    assert response.json()["phone_number"] == "(111)-111-1111"
    assert response.json()["hashed_password"] == test_user.hashed_password


def test_change_password_success(test_user):
    response = client.put(
        "/user/password",
        json={"password": TEST_PASSWORD, "new_password": "new_password"},
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT
    db = TestingSessionLocal()
    model = db.query(Users).filter(Users.id == 1).first()
    assert bcrypt_context.verify("new_password", model.hashed_password)


def test_change_password_invalid_current_password(test_user):
    response = client.put(
        "/user/password",
        json={"password": "wrong_password", "new_password": "new_password"},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Wrong password!"}


def test_change_phone_number_success(test_user):
    response = client.put(
        "/user/phone_number", json={"new_phone_number": "(222)-222-2222"}
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT
    db = TestingSessionLocal()
    model = db.query(Users).filter(Users.id == 1).first()
    assert model.phone_number == "(222)-222-2222"
