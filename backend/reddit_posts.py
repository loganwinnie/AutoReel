import praw
import json
from fastapi import HTTPException
from prawcore.exceptions import NotFound

from config import (
    REDDIT_CLIENT_ID,
    REDDIT_CLIENT_SECRET,
    REDDIT_USER_AGENT,
    REDDIT_USERNAME,
    REDDIT_PASSWORD,
    engine,
)

from sqlmodel import Session
from models import Post

client_id = REDDIT_CLIENT_ID
client_secret = REDDIT_CLIENT_SECRET
user_agent = REDDIT_USER_AGENT
username = REDDIT_USERNAME

reddit = praw.Reddit(
    client_id=client_id,
    client_secret=client_secret,
    user_agent=user_agent,
    username=REDDIT_USERNAME,
    password=REDDIT_PASSWORD,
)


def get_posts_from_subreddit(subreddit: str = "Autoreel", limit: int = 15):

    custom_feed = reddit.multireddit(REDDIT_USERNAME, subreddit)

    post_data = []

    for post in custom_feed.hot(limit=limit):

        post_dict = {
            "title": post.title.strip(),
            "url": post.url,
            "content": post.selftext.strip(),
            "subreddit": post.subreddit.display_name.strip(),
            "post_id": post.id,
        }

        print("SUBREDDIT", dir(post.subreddit))
        post_data.append(post_dict)

    jsonified_posts = json.dumps(post_data)

    return jsonified_posts


def save_post_to_db(post_id: str):

    post = None

    try:
        post = reddit.submission(id=post_id)
        print("POST", post)
    except NotFound:
        raise HTTPException(404, detail="Post not found.")
    except:
        raise HTTPException(500, detail="Problem retrieving post.")

    with Session(engine) as session:
        # try:
        post_model = Post(
            id=post.id,
            title=post.title.strip(),
            url=post.url.strip(),
            content=post.selftext.strip(),
            subreddit=post.subreddit.display_name.strip(),
        )
        session.add(post_model)
        session.commit()
        return post_model
    # except:
    #     raise HTTPException(500, detail="Unable to save post.")
