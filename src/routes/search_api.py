from datetime import datetime
from fastapi import FastAPI
from src.routes.search import search_pictures, search_users, search_comments
from typing import List

app = FastAPI()

@app.get("/search/pictures")
async def search_pictures_endpoint(query: str, tags: List[str] = None, rating: int = None, date_added: datetime = None):
    pass
