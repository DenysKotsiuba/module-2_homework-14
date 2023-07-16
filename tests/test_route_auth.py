from unittest.mock import MagicMock

from src.database.models import User
from src.services.auth import auth_service


def test_signup(client, user, monkeypatch):
    mock_send_email = MagicMock()
    monkeypatch.setattr("src.services.email.send_email", mock_send_email)
    response = client.post("/auth/signup", json=user)
    assert response.status_code == 201, response.text
    payload = response.json()
    assert payload["user"]["username"] == user["username"]
    assert payload["user"]["email"] == user["email"]
    assert payload["detail"] == "User successfully created"


def test_repeat_signup(client, user, monkeypatch):
    mock_send_email = MagicMock()
    monkeypatch.setattr("src.services.email.send_email", mock_send_email)
    response = client.post("/auth/signup", json=user)
    assert response.status_code == 409, response.text
    payload = response.json()
    assert payload["detail"] == "Account already exists"


def test_login_with_not_confirmed_user(client, user, session):
    current_user: User = session.query(User).filter_by(email=user["email"]).first()
    current_user.confirmed = False
    session.commit()
    current_user: User = session.query(User).filter_by(email=user["email"]).first()
    response = client.post("/auth/login", data={"username": user["email"], "password": user["password"]})
    assert response.status_code == 401, response.text
    payload = response.json()
    assert payload["detail"] == "Email not confirmed"


def test_login(client, user, session):
    current_user: User = session.query(User).filter_by(email=user["email"]).first()
    current_user.confirmed = True
    session.commit()
    response = client.post("/auth/login", data={"username": user["email"], "password": user["password"]})
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["token_type"] == "bearer"


def test_login_with_wrong_password(client, user, session):
    current_user: User = session.query(User).filter_by(email=user["email"]).first()
    current_user.confirmed = True
    session.commit()
    response = client.post("/auth/login", data={"username": user["email"], "password": "password"})
    assert response.status_code == 401, response.text
    payload = response.json()
    assert payload["detail"] == "Invalid password"


def test_login_with_wrong_email(client, user, session):
    current_user: User = session.query(User).filter_by(email=user["email"]).first()
    current_user.confirmed = True
    session.commit()
    response = client.post("/auth/login", data={"username": "email", "password": user["password"]})
    assert response.status_code == 401, response.text
    payload = response.json()
    assert payload["detail"] == "Invalid email"


def test_request_email(client, user, session):
    current_user: User = session.query(User).filter_by(email=user["email"]).first()
    current_user.confirmed = False
    session.commit()
    response = client.post("/auth/request_email", json={"email": user["email"]})
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["message"] == "Check your email for confirmation"


def test_request_email_user_confirmed(client, user, session):
    current_user: User = session.query(User).filter_by(email=user["email"]).first()
    current_user.confirmed = True
    session.commit()
    response = client.post("/auth/request_email", json={"email": user["email"]})
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["message"] == "Your email is already confirmed"


def test_confirmed_email(client, user, session):
    current_user: User = session.query(User).filter_by(email=user["email"]).first()
    current_user.confirmed = False
    session.commit()
    email_token = auth_service.create_email_token({"sub": current_user.email})
    response = client.get(f"/auth/confirmed_email/{email_token}")
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["message"] == "Email confirmed"


def test_confirmed_email_user_confirmed(client, user, session):
    current_user: User = session.query(User).filter_by(email=user["email"]).first()
    current_user.confirmed = True
    session.commit()
    email_token = auth_service.create_email_token({"sub": user["email"]})
    response = client.get(f"/auth/confirmed_email/{email_token}")
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["message"] == "Your email is already confirmed"


def test_confirmed_email_user_not_verificated(client):
    email_token = auth_service.create_email_token({"sub": "wrong@email.com"})
    response = client.get(f"/auth/confirmed_email/{email_token}")
    assert response.status_code == 400, response.text
    payload = response.json()
    assert payload["detail"] == "Verification error"