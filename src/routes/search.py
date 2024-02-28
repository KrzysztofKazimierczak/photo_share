from sqlalchemy import or_
from src.database.models import Base, Tag, User, Comment, Picture
from typing import List
from datetime import datetime


#Mother Function
def search(query: str, model: Base, fields: List[str]) -> List[Base]: # type: ignore
    pass

def search_pictures(keywords_or_tags: List[str]) -> List[Picture]:
    pass

def search_users(keywords: List[str]) -> List[User]:
    pass

def search_comments(keywords: List[str]) -> List[Comment]:
    pass



