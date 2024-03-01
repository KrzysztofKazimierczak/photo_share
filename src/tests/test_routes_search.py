import pytest
from fastapi.testclient import TestClient
from fastapi.templating import Jinja2Templates
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.database.models import Base, Tag, User, Comment, Picture, PictureTagsAssociation
from src.routes.search import search, search_pictures, search_users, search_users_with_photos, search_comments
from faker import Faker

