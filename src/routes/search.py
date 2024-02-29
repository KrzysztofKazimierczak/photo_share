from sqlalchemy import or_
from src.database.models import Base, Tag, User, Comment, Picture
from typing import List
from datetime import datetime


#Mother Function
def search(query: str, model: Base, fields: List[str]) -> List[Base]: # type: ignore
    query_parts = query.split()
    query = model.query
    for query_part in query_parts:
        query = query.filter(or_(*[getattr(model, field).contains(query_part) for field in fields]))
    return query.all()


def search_pictures(keywords_or_tags: List[str]) -> List[Picture]:
    return search(query=' '.join(keywords_or_tags), model=Picture, fields=('tags.name', 'description'))
    

def search_users(keywords: List[str]) -> List[User]:
    return search(query=' '.join(keywords), model=User, fields=('username', 'email'))


def search_comments(keywords: List[str]) -> List[Comment]:
    return search(query=' '.join(keywords), model=Comment, fields=('content',))




