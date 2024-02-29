from datetime import datetime
from fastapi import FastAPI
from src.routes.search import search_pictures, search_users, search_comments
from typing import List

app = FastAPI()

@app.get("/search/pictures")
async def search_pictures_endpoint(query: str, tags: List[str] = None, rating: int = None, date_added: datetime = None):
    pass

@app.get("/search/users")
async def search_users_endpoint(query: str, tags: List[str] = None, rating: int = None, date_added: datetime = None):
    pass

@app.get("/search/comments")
async def search_comments_endpoint(query: str, tags: List[str] = None, rating: int = None, date_added: datetime = None):
    pass
