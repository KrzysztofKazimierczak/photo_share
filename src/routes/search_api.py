from datetime import datetime
from fastapi import FastAPI
from src.routes.search import search_pictures, search_users, search_comments
from typing import List
from src.services.auth import Auth


app = FastAPI()

@app.get("/search/pictures")
async def search_pictures_endpoint(query: str, tags: List[str] = None, rating: int = None, date_added: datetime = None):
    pictures = search_pictures(keywords_or_tags=query.split())
    if tags:
        pictures = [picture for picture in pictures if any(tag.name in tags for tag in picture.tags)]
    if rating is not None:
        pictures = [picture for picture in pictures if picture.rating == rating]
    if date_added is not None:
        start_date = datetime.combine(date_added, datetime.min.time())
        end_date = datetime.combine(date_added, datetime.max.time())
        pictures = [picture for picture in pictures if start_date <= picture.created_at <= end_date]
    return pictures


@app.get("/search/users")
async def search_users_endpoint(query: str, tags: List[str] = None, rating: int = None, date_added: datetime = None):
    users = search_users(keywords=query.split())
    if tags:
        users = [user for user in users if any(tag.name in tags for tag in user.tags)]
    if rating is not None:
        users = [user for user in users if user.rating == rating]
    if date_added is not None:
        start_date = datetime.combine(date_added, datetime.min.time())
        end_date = datetime.combine(date_added, datetime.max.time())
        users = [user for user in users if start_date <= user.created_at <= end_date]
    return users


@app.get("/search/comments")
async def search_comments_endpoint(query: str, tags: List[str] = None, rating: int = None, date_added: datetime = None):
    comments = search_comments(keywords=query.split())
    if tags:
        comments = [comment for comment in comments if any(tag.name in tags for tag in comment.tags)]
    if rating is not None:
        comments = [comment for comment in comments if comment.rating == rating]
    if date_added is not None:
        start_date = datetime.combine(date_added, datetime.min.time())
        end_date = datetime.combine(date_added, datetime.max.time())
        comments = [comment for comment in comments if start_date <= comment.created_at <= end_date]
    return comments