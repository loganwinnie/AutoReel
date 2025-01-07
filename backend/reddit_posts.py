import praw
import json
from fastapi import HTTPException
from prawcore.exceptions import NotFound, ResponseException
from sqlalchemy.exc import IntegrityError, NoResultFound
from config import (
    REDDIT_CLIENT_ID,
    REDDIT_CLIENT_SECRET,
    REDDIT_USER_AGENT,
    REDDIT_USERNAME,
    REDDIT_PASSWORD,
    engine,
)

from sqlmodel import Session, select
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
    try: 
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

            post_data.append(post_dict)

        jsonified_posts = json.dumps(post_data)

        return jsonified_posts
    except ResponseException:
        raise HTTPException(401, detail="Failed to authenticate Reddit Account.")
    except NotFound:
        raise HTTPException(404, detail="Subreddit not found.")
    except:
        raise HTTPException(500, detail="Failed to fetch post.")



def save_post_to_db(post_id: str):

    post = None

    try:
        post = reddit.submission(id=post_id)
    except NotFound:
        raise HTTPException(404, detail="Post not found.")
    except:
        raise HTTPException(500, detail="Problem retrieving post.")

    with Session(engine) as session:
        try:
            post_model = Post(
                id=post.id,
                title=post.title.strip(),
                url=post.url.strip(),
                content=post.selftext.strip(),
                subreddit=post.subreddit.display_name.strip(),
            )
            post_json = post_model.model_dump_json()
            session.add(post_model)
            session.commit()
            return post_json
        except IntegrityError:
            raise HTTPException(400, detail="Cannot save duplicate post.")
        except:
            raise HTTPException(500, "Failed to save post.")

def get_saved_posts_from_db(offset:int = 0, limit:int = 15):
    with Session(engine) as session:
        try:
           statement = select(Post).offset(offset=offset).limit(limit=limit)
           posts = session.exec(statement=statement).all()
           return posts
        except:
            raise HTTPException(500, "Failed to get posts.")


def delete_saved_post_from_db(post_id: str):
    with Session(engine) as session:
        try:
            statement = select(Post).where(Post.id == post_id)
            results = session.exec(statement)
            post = results.one()
            session.delete(post)
            session.commit()
            return post.id
        except NoResultFound:
            raise HTTPException(404, "Post not found.")
        except:
            raise HTTPException(500, "Failed to delete post.")