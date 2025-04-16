from datetime import timedelta
from fastapi import HTTPException

from jose import jwt

from test.utils import *
from todo_app.routers.auth import (
    ALGORITHM,
    SECRET_KEY,
    authenticate_user,
    create_access_token,
    get_current_user,
)


def test_authenticate_user(test_user):
    db = TestingSessionLocal()
    authenticated_user = authenticate_user(
        test_user.username, TEST_PASSWORD, db
    )
    assert authenticated_user is not None
    assert authenticated_user.username == test_user.username

    non_existent_user = authenticate_user(
        "non_existent_user", TEST_PASSWORD, db
    )

    assert non_existent_user is False

    wrong_password_user = authenticate_user(
        test_user.username, "wrong_password", db
    )

    assert wrong_password_user is False


def test_create_access_token(test_user):
    expires_delta = timedelta(days=1)
    token = create_access_token(
        username=test_user.username,
        user_id=test_user.id,
        role=test_user.role,
        expires_delta=expires_delta,
    )
    decoded_token = jwt.decode(
        token,
        SECRET_KEY,
        algorithms=[ALGORITHM],
        options={"verify_signature": False},
    )
    assert decoded_token["sub"] == test_user.username
    assert decoded_token["id"] == test_user.id
    assert decoded_token["role"] == test_user.role


@pytest.mark.asyncio
async def test_get_current_user(test_user):
    encode = {
        "sub": test_user.username,
        "id": test_user.id,
        "role": test_user.role,
    }
    token = jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)
    user = await get_current_user(token)

    assert user == {
        "username": test_user.username,
        "id": test_user.id,
        "user_role": test_user.role,
    }

@pytest.mark.asyncio
async def test_get_current_user_missing_payload():
    encode = {"role":"user"}
    token = jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)
    with pytest.raises(HTTPException) as excinfo:
        await get_current_user(token=token)
    assert excinfo.value.status_code == 401
    assert excinfo.value.detail == "Could not validate user."