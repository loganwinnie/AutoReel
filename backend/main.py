from typing import Annotated
from fastapi import FastAPI, Query
from fastapi.concurrency import asynccontextmanager
from reddit_posts import get_posts_from_subreddit, save_post_to_db, get_saved_posts_from_db, delete_saved_post_from_db
from util import create_db_and_tables

tags_metadata = [{"name": "Posts", "description": "Routes for handling reddit posts."},
                 {"name": "Save", "description": "Routes for saving posts."}]


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load the Database
    create_db_and_tables()
    yield
    
app = FastAPI(openapi_tags=tags_metadata, lifespan=lifespan)


@app.get("/posts", tags=["Posts"])
def get_posts(
    limit: Annotated[
        int,
        Query(
            title="amount of posts to retrieve",
        ),
    ] = 15,
    subreddit: Annotated[
        str,
        Query(
            title="Subreddit to search for post",
        ),
    ] = "Autoreel",
):
    posts = get_posts_from_subreddit(subreddit=subreddit, limit=limit)
    return {"posts": posts}


@app.post("/save", tags=["Save"])
def save_post(post_id: str):
    post = save_post_to_db(post_id=post_id)
    return {"post": post}


@app.get("/save", tags=["Save"])
def get_saved_posts(
    limit: Annotated[
        int,
        Query(
            title="amount of posts to retrieve",
        ),
    ] = 15,
    offset: Annotated[
    int,
    Query(
        title="amount of posts to retrieve",
    ),
    ] = 0,
):
    posts = get_saved_posts_from_db(offset=offset,limit=limit)
    return {"posts": posts}

@app.delete("/save", tags=["Save"])
def delete_saved_post(post_id:str):
    post = delete_saved_post_from_db(post_id=post_id)
    return {"deleted": post}

