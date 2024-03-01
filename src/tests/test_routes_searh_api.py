import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from fastapi.templating import Jinja2Templates
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.database.models import Base, Tag, User, Comment, Picture, PictureTagsAssociation, Auth
from src.routes.search import search, search_pictures, search_users, search_users_with_photos, search_comments, get_current_user
from faker import Faker
from datetime import datetime, timedelta

# fake database session
fake = Faker("pl_PL")
engine = create_engine('sqlite:///:memory:', echo=False)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()


# test data
user1 = User(username=fake.user_name(), email=fake.email(), password=fake.password(), rating=4, created_at=datetime.utcnow())
user2 = User(username=fake.user_name(), email=fake.email(), password=fake.password(), rating=3, created_at=datetime.utcnow())
session.add_all([user1, user2])
session.commit()
tag1 = Tag(name=fake.word())
tag2 = Tag(name=fake.word())
session.add_all([tag1, tag2])
session.commit()
picture1 = Picture(user_id=user1.id, tags=[tag1])
picture2 = Picture(user_id=user2.id, tags=[tag2])
session.add_all([picture1, picture2])
session.commit()
comment1 = Comment(user_id=user1.id, picture_id=picture1.id, content=fake.text())
comment2 = Comment(user_id=user2.id, picture_id=picture2.id, content=fake.text())
session.add_all([comment1, comment2])
session.commit()


# instance of the FastAPI application
app = FastAPI()


#  test client
client = TestClient(app)


def test_search_pictures_endpoint():
    # test searching for pictures by keywords
    response = client.get("/search/users/pictures", params={"query": "test picture"})
    pictures = response.json()
    assert len(pictures) == 1
    assert pictures[0]["id"] == picture1.id

    # test searching for pictures by tags
    response = client.get("/search/users/pictures", params={"tags": [tag1.name]})
    pictures = response.json()
    assert len(pictures) == 1
    assert pictures[0]["id"] == picture1.id

    # test searching for pictures by rating
    response = client.get("/search/users/pictures", params={"rating": 4})
    pictures = response.json()
    assert len(pictures) == 1
    assert pictures[0]["id"] == picture1.id

    # test searching for pictures by date added
    start_date = datetime.utcnow() - timedelta(days=10)
    end_date = datetime.utcnow() + timedelta(days=10)
    response = client.get("/search/users/pictures", params={"date_added": start_date})
    pictures = response.json()
    assert len(pictures) == 2
    