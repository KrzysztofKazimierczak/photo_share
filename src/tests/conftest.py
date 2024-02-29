import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.templating import Jinja2Templates

from main import app
from src.database.models import Base, User
from src.database.db import get_db
from src.services.auth import auth_service
from faker import Faker

fake = Faker("pl_PL")

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

templates = Jinja2Templates(directory="templates")

@pytest.fixture(scope="function", autouse=True)
def session():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture(scope="function")
def client(session):
    def override_get_db():
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db

    yield TestClient(app)

@pytest.fixture(scope="function")
def user():
    class UserTest:
        def __init__(self, id, username, email, password):
            self.id = id
            self.username = username
            self.email = email
            self.password = password

        def dict(self):
            return {
                "id": self.id,
                "username": self.username,
                "email": self.email,
                "password": self.password
            }
    return UserTest(id=1,
                    username="example",
                    email="example@example.com",
                    password="secret")


def create_user_db(body: user, db: session):
    new_user = User(**body.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)


def login_user_confirmed_true_and_hash_password(user, session):
    create_user_db(user, session)
    user_update: User = session.query(User).filter(User.email == user.email).first()
    user_update.password = auth_service.get_password_hash(user_update.password)
    user_update.confirmed = True
    session.commit()


def login_user_token_created(user, session):
    login_user_confirmed_true_and_hash_password(user, session)
    new_user: User = session.query(User).filter(User.email == user.email).first()

    access_token = auth_service.create_access_token(data={"sub": new_user.email})
    refresh_token_ = auth_service.create_refresh_token(data={"sub": new_user.email})

    new_user.refresh_token = refresh_token_
    session.commit()

    return {"access_token": access_token, "refresh_token": refresh_token_, "token_type": "bearer"}


@pytest.fixture
def fake_db_for_message_test():
    '''
    This fixture is used to fake db for message testing
    '''
    # Initialize the fake database structure
    db = {"users": {}, "messages": {}, "next_user_id": 1, "next_message_id": 1}

    def create_user(email, username, password):
        user_id = db["next_user_id"]
        db["users"][user_id] = {
            "id": user_id,
            "email": email,
            "username": username,
            "password": password
        }
        db["next_user_id"] += 1
        return db["users"][user_id]

    def create_message(sender_id, receiver_id, content):
        if sender_id not in db["users"] or receiver_id not in db["users"]:
            raise ValueError("Sender or Receiver does not exist.")
        message_id = db["next_message_id"]
        db["messages"][message_id] = {
            "id": message_id,
            "sender_id": sender_id,
            "receiver_id": receiver_id,
            "content": content
        }
        db["next_message_id"] += 1
        return db["messages"][message_id]

    def get_messages_for_user(user_id):
        if user_id not in db["users"]:
            raise ValueError("User does not exist.")
        return [msg for msg in db["messages"].values() if msg["sender_id"] == user_id or msg["receiver_id"] == user_id]

    db["create_user"] = create_user
    db["create_message"] = create_message
    db["get_messages_for_user"] = get_messages_for_user

    return db
