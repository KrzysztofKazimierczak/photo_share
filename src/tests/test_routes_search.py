import pytest
from fastapi.testclient import TestClient
from fastapi.templating import Jinja2Templates
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.database.models import Base, Tag, User, Comment, Picture, PictureTagsAssociation
from src.routes.search import search, search_pictures, search_users, search_users_with_photos, search_comments
from faker import Faker


# fake database session
fake = Faker("pl_PL")
engine = create_engine('sqlite:///:memory:', echo=False)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

# test data
user1 = User(username=fake.user_name(), email=fake.email(), password=fake.password())
user2 = User(username=fake.user_name(), email=fake.email(), password=fake.password())
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

#  test client
client = TestClient(app)