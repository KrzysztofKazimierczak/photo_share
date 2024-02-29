import json
from unittest.mock import MagicMock, AsyncMock
from fastapi.responses import HTMLResponse
from src.database.models import User
from src.services.auth import auth_service
from src.tests.conftest import login_user_token_created, create_user_db, \
    login_user_confirmed_true_and_hash_password


def test_create_user(client, user, monkeypatch):
    mock_send_email = MagicMock()
    monkeypatch.setattr("src.routes.auth.send_verification_email", mock_send_email)

    response = client.post("/api/auth/signup", json=user.dict())

    assert response.status_code == 201, response.text
    data = response.json()
    assert data["user"]["email"] == user.email
    assert "id" in data["user"]
    assert data['detail'] == "User successfully created. Check your email for confirmation."


def test_repeat_create_user(user, session, client):
    create_user_db(user, session)

    response = client.post("/api/auth/signup", json=user.dict())

    assert response.status_code == 409, response.text
    data = response.json()
    assert data["detail"] == "Account already exists."


def test_login_wrong_email(user, session, client):
    create_user_db(user, session)

    response = client.post(
        "/api/auth/login",
        data={"username": 'email', "password": user.password},
    )

    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Invalid email."


def test_login_user_not_confirmed(user, session, client):
    create_user_db(user, session)

    response = client.post(
        "/api/auth/login",
        data={"username": user.email, "password": user.password},
    )

    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Email not confirmed."


def test_login_wrong_password(user, session, client):
    login_user_confirmed_true_and_hash_password(user, session)

    response = client.post(
        "/api/auth/login",
        data={"username": user.email, "password": 'password'},
    )

    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Invalid password."


def test_login_user(user, session, client):
    login_user_confirmed_true_and_hash_password(user, session)

    response = client.post(
        "/api/auth/login",
        data={"username": user.email, "password": user.password},
    )

    assert response.status_code == 200, response.text
    data = response.json()
    assert 'access_token' in data
    assert 'refresh_token' in data
    assert data["token_type"] == "bearer"


def test_refresh_token_invalid_user(user, session, client, monkeypatch):
    login_user_token_created(user, session)

    async def mock_decode_refresh_token(token):
        return user.email

    monkeypatch.setattr(auth_service, "decode_refresh_token",
                        AsyncMock(side_effect=mock_decode_refresh_token))

    response = client.get(
        '/api/auth/refresh_token',
        headers={
            'Authorization': f'Bearer invalid_refresh_token'}
    )

    assert response.status_code == 401
    data = response.json()
    assert data['detail'] == 'Invalid refresh token.'


def test_refresh_token(user, session, client):
    login_user_token_created(user, session)
    user_authorization: User = session.query(User).filter(User.email == user.email).first()

    response = client.get(
        '/api/auth/refresh_token',
        headers={'Authorization': f"Bearer {user_authorization.refresh_token}"},
    )

    assert response.status_code == 200, response.text
    data = response.json()
    assert 'access_token' in data
    assert 'refresh_token' in data
    assert data["token_type"] == "bearer"


def test_confirmed_email_user_is_none(user, session, client, monkeypatch):
    create_user_db(user, session)

    async def mock_get_email_from_token(token):
        return None

    monkeypatch.setattr(auth_service, "get_email_from_token",
                        AsyncMock(side_effect=mock_get_email_from_token))

    response = client.get(f'/api/auth/confirmed_email/VALID_TOKEN')

    assert response.status_code == 400, response.text
    data = response.json()
    assert data['detail'] == 'Verification error.'


def test_confirmed_email_user_confirmed(user, session, client, monkeypatch):
    login_user_confirmed_true_and_hash_password(user, session)

    async def mock_decode_confirmed_email_token(token):
        return user.email

    monkeypatch.setattr(auth_service, "get_email_from_token",
                        AsyncMock(side_effect=mock_decode_confirmed_email_token))

    response = client.get(
        f'/api/auth/confirmed_email/your_email_is_already_confirmed'
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data['message'] == 'Your email is already confirmed.'


def test_confirmed_email(user, session, client, monkeypatch):
    create_user_db(user, session)

    async def mock_decode_confirmed_email_token(token):
        return user.email

    monkeypatch.setattr(auth_service, "get_email_from_token",
                        AsyncMock(side_effect=mock_decode_confirmed_email_token))

    response = client.get(
        '/api/auth/confirmed_email/email_confirmed'
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data['message'] == 'Email confirmed.'


def test_request_email_confirmed(user, session, client, monkeypatch):
    login_user_confirmed_true_and_hash_password(user, session)

    response = client.post(
        "/api/auth/request_email",
        data=json.dumps({"email": user.email}),
    )

    assert response.status_code == 200, response.text
    data = response.json()
    assert data["message"] == "Your email is already confirmed."


def test_request_email(user, session, client):
    create_user_db(user, session)

    response = client.post(
        "/api/auth/request_email",
        data=json.dumps({"email": user.email}),
    )

    assert response.status_code == 200, response.text
    data = response.json()
    assert data["message"] == "Check your email for confirmation."


def test_request_password_reset_user_not_found(user, session, client):
    create_user_db(user, session)

    response = client.post(
        "api/auth/reset_password/request",
        data=json.dumps({"email": "user_not_found@example.com"})
    )

    assert response.status_code == 400, response.text
    data = response.json()
    assert data["detail"] == "Verification error."


def test_request_password_reset(user, session, client):
    create_user_db(user, session)

    response = client.post(
        "api/auth/reset_password/request",
        data=json.dumps({"email": user.email})
    )

    assert response.status_code == 200, response.text
    data = response.json()
    assert data["message"] == "Password reset email sent."


def test_reset_password_token_get(user, session, client, monkeypatch):
    create_user_db(user, session)

    async def mock_reset_password_token(token):
        return user.email

    monkeypatch.setattr(auth_service,
                        "get_email_from_token",
                        AsyncMock(side_effect=mock_reset_password_token))

    response = client.get("api/auth/reset_password/reset_password_token")

    assert response.status_code == 200
    assert isinstance(response, HTMLResponse)


def test_reset_password_token_push_user_is_none(user, session, client, monkeypatch):
    create_user_db(user, session)

    async def mock_reset_password_token(token):
        return user.email

    monkeypatch.setattr(auth_service,
                        "get_email_from_token",
                        AsyncMock(side_effect=mock_reset_password_token))

    post_data = {"new_password": "NoweHaslo123"}
    response = client.post("api/auth/reset_password/reset_password_token",
                           json=post_data,
                           headers={"Content-Type": "application/json"})

    assert response.status_code == 400, response.text
    data = response.json()
    assert data["detail"] == "Verification error."


def test_reset_password_token_push(user, session, client, monkeypatch):
    create_user_db(user, session)

    async def mock_reset_password_token(token):
        return user.email

    monkeypatch.setattr(auth_service,
                        "get_email_from_token",
                        AsyncMock(side_effect=mock_reset_password_token))

    response = client.post("api/auth/reset_password/reset_password_token",
                           json={"new_password": "Secret0"})

    assert response.status_code == 200, response.text
    data = response.json()
    assert data["massage"] == "Password reset successfully."


def test_change_password_password_is_incorrect(user, session, client):
    new_user = login_user_token_created(user, session)

    response = client.post("api/auth/change_password",
                           headers={"Authorization": f"Bearer {new_user.get('access_token')}"},
                           json={"current_password": "example",
                                 "new_password": "secret1",
                                 "confirm_password": "secret1"})

    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Current password is incorrect."


def test_change_password_password_not_match(user, session, client):
    new_user = login_user_token_created(user, session)

    response = client.post("api/auth/change_password",
                           headers={"Authorization": f"Bearer {new_user.get('access_token')}"},
                           json={"current_password": "secret",
                                 "new_password": "secret1",
                                 "confirm_password": "secret2"})

    assert response.status_code == 400, response.text
    data = response.json()
    assert data["message"] == "The provided passwords do not match."


def test_change_password_password(user, session, client):
    new_user = login_user_token_created(user, session)

    response = client.post(
        "api/auth/change_password",
        headers={"Authorization": f"Bearer {new_user.get('access_token')}"},
        json={
            "current_password": "secret",
            "new_password": "secret1",
            "confirm_password": "secret1"
        }
    )

    assert response.status_code == 200, response.text
    data = response.json()
    assert data["message"] == "Password changed successfully."
