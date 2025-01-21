from typing import Annotated
from fastapi import FastAPI, Path, Query, Body
from fastapi.concurrency import asynccontextmanager
from models import Post
from reddit_posts import get_posts_from_subreddit, patch_post_audio_db, save_post_db, get_saved_posts_db, delete_saved_post_db, use_post_db
from util import create_db_and_tables

tags_metadata = [{"name": "Reddit", "description": "Routes for handling reddit posts."},
                 {"name": "Posts", "description": "Routes for posts."}]


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load the Database
    create_db_and_tables()
    yield
    
app = FastAPI(openapi_tags=tags_metadata, lifespan=lifespan)

@app.get("/reddit", tags=["Reddit"])
def get_posts(
    limit: Annotated[
        int,
        Query(
            title="amount of posts to retrieve.",
        ),
    ] = 15,
    subreddit: Annotated[
        str,
        Query(
            title="Subreddit to search for post.",
        ),
    ] = "Autoreel",
):
    posts = get_posts_from_subreddit(subreddit=subreddit, limit=limit)
    return {"posts": posts}

@app.post("/posts", tags=["Posts"])
def save_post(post_id: str):
    post = save_post_db(post_id=post_id)
    return {"post": post}

@app.get("/posts", tags=["Posts"])
def get_saved_posts(
    limit: Annotated[
        int,
        Query(
            title="amount of posts to retrieve.",
        ),
    ] = 15,
    offset: Annotated[
    int,
    Query(
        title="amount of posts to retrieve.",
    ),
    ] = 0,
):
    posts = get_saved_posts_db(offset=offset,limit=limit)
    return {"posts": posts}

@app.delete("/posts/{post_id}", tags=["Posts"])
def delete_saved_post(post_id: Annotated[str, Path(title="Id of the post to delete.")], ):
    post = delete_saved_post_db(post_id=post_id)
    return {"deleted": post}

@app.patch("/posts/{post_id}", tags=["Posts"])
def patch_audio_saved_post(
    post_id: Annotated[str, Path(title="Id of the post to update audio url on.")],
    post: Post):
    post = patch_post_audio_db(post_id=post_id, post=post)
    return {"patched": post}

@app.patch("/posts/{post_id}/use", tags=["Posts"])
def patch_audio_saved_post(
    post_id: Annotated[str, Path(title="Id of the post to change used status.")]):
    post = use_post_db(post_id=post_id)
    return {"used": post}

