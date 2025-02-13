from typing import Annotated

from fastapi import FastAPI, Path, Query
from fastapi.concurrency import asynccontextmanager

from models import Post
from reddit_posts import (
    get_posts_from_subreddit,
    patch_post_audio_db,
    save_post_db,
    get_saved_posts_db,
    delete_saved_post_db,
    use_post_db,
)
from util import create_db_and_tables
from youtube_scrapper import get_videos_db, scrape_videos, save_video_to_db

# Metadata for OpenAPI docs.
tags_metadata = [
    {"name": "Reddit", "description": "Routes for handling reddit posts."},
    {"name": "Posts", "description": "Routes for posts."},
    {"name": "Videos", "description": "Video related routes."},
]

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load the Database
    create_db_and_tables()
    yield

app = FastAPI(openapi_tags=tags_metadata, lifespan=lifespan)

# Reddit Routes

@app.get("/reddit", tags=["Reddit"])
def get_posts(
    limit: Annotated[int, Query(title="Amount of posts to retrieve.")] = 15,
    subreddit: Annotated[str, Query(title="Subreddit to search for posts.")] = "Autoreel",
):
    posts = get_posts_from_subreddit(subreddit=subreddit, limit=limit)
    return {"posts": posts}

# Post Routes

@app.post("/posts", tags=["Posts"])
def save_post(post_id: str):
    post = save_post_db(post_id=post_id)
    return {"post": post}

@app.get("/posts", tags=["Posts"])
def get_saved_posts(
    limit: Annotated[int, Query(title="Amount of posts to retrieve.")] = 15,
    offset: Annotated[int, Query(title="Pagination offset.")] = 0,
):
    posts = get_saved_posts_db(offset=offset, limit=limit)
    return {"posts": posts}

@app.delete("/posts/{post_id}", tags=["Posts"])
def delete_saved_post(post_id: Annotated[str, Path(title="ID of the post to delete.")]):
    post = delete_saved_post_db(post_id=post_id)
    return {"deleted": post}

@app.patch("/posts/{post_id}", tags=["Posts"])
def patch_audio_saved_post(
    post_id: Annotated[str, Path(title="ID of the post to update audio url on.")],
    post: Post
):
    patched_post = patch_post_audio_db(post_id=post_id, post=post)
    return {"patched": patched_post}

@app.patch("/posts/{post_id}/use", tags=["Posts"])
def patch_used_post(
    post_id: Annotated[str, Path(title="ID of the post to change used status.")]
):
    used_post = use_post_db(post_id=post_id)
    return {"used": used_post}

# Video Routes

@app.post("/videos", tags=["Videos"])
def download_and_save_videos(
    game: Annotated[
        str,
        Query(
            title="Game to download footage of.",
        ),
    ] = "",
):  
    combined_info = scrape_videos(game=game)

    created_videos = []
    for item in combined_info:
        video_json = save_video_to_db(
            title=item["title"],
            file_path=item["gcs_path"],
            video_url=item["link"]
        )
        created_videos.append(video_json)

    return {
        "downloaded": [x["gcs_path"] for x in combined_info],
        "saved": created_videos,
    }

@app.get("/videos", tags=["Videos"])
def get_all_videos(
    limit: Annotated[int, Query(title="Amount of videos to retrieve.")] = 15,
    offset: Annotated[int, Query(title="Pagination offset.")] = 0,
):
    """
    Retrieve all saved videos in the database, with pagination.

    :param limit: Number of videos to retrieve.
    :param offset: Pagination offset.
    :return: A list of video records.
    """
    videos = get_videos_db(offset=offset, limit=limit)
    return {"videos": videos}