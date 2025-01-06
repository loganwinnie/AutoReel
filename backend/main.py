from typing import Annotated
from fastapi import FastAPI, Query
from reddit_posts import get_posts_from_subreddit, save_post_to_db

tags_metadata = [{"name": "Posts", "description": "Routes for handling reddit posts"}]

app = FastAPI(openapi_tags=tags_metadata)


@app.get("/")
def root():
    return {"Hello": "World"}


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


@app.post("/posts", tags=["Posts"])
def save_post(post_id: str):
    post = save_post_to_db(post_id=post_id)
    return {"post": post}


# @app.post("/posts/save",)
