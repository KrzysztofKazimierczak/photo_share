from sqlalchemy import or_
from src.database.models import Base, Tag, User, Comment, Picture
from typing import List
from datetime import datetime


#Mother Function
def search(query: str, model: Base, fields: List[str]) -> List[Base]: # type: ignore
    """
    Searches for records in the given model that match the provided query string.

    Args:
        query (str): The query string to search for.
        model (Base): The SQLAlchemy model to search in.
        fields (Tuple[str, ...]): The fields of the model to search in.

    Returns:
        List[model]: A list of records that match the search criteria.
    """
    query_parts = query.split()
    query = model.query
    for query_part in query_parts:
        query = query.filter(or_(*[getattr(model, field).contains(query_part) for field in fields]))
    return query.all()


def search_pictures(keywords_or_tags: List[str]) -> List[Picture]:
    """
    Searches for pictures that match the given keywords or tags.

    Args:
        keywords_or_tags (List[str]): A list of keywords or tags to search for.

    Returns:
        List[Picture]: A list of pictures that match the search criteria.
    """
    return search(query=' '.join(keywords_or_tags), model=Picture, fields=('tags.name', 'description'))
    

def search_users(keywords: List[str]) -> List[User]:
    """
    Searches for users that match the given keywords.

    Args:
        keywords (List[str]): A list of keywords to search for.

    Returns:
        List[User]: A list of users that match the search criteria.
    """
    return search(query=' '.join(keywords), model=User, fields=('username', 'email'))


def search_comments(keywords: List[str]) -> List[Comment]:
    """
    Searches for comments that match the given keywords.

    Args:
        keywords (List[str]): A list of keywords to search for.

    Returns:
        List[Comment]: A list of comments that match the search criteria.
    """
    return search(query=' '.join(keywords), model=Comment, fields=('content',))




