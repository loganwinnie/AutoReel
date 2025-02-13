import json
import logging

import praw
from fastapi import HTTPException
from prawcore.exceptions import NotFound, ResponseException
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlmodel import Session, select

from config import (
    REDDIT_CLIENT_ID,
    REDDIT_CLIENT_SECRET,
    REDDIT_USER_AGENT,
    REDDIT_USERNAME,
    REDDIT_PASSWORD,
    engine,
)
from models import Post


reddit = praw.Reddit(
    client_id=REDDIT_CLIENT_ID,
    client_secret=REDDIT_CLIENT_SECRET,
    user_agent=REDDIT_USER_AGENT,
    username=REDDIT_USERNAME,
    password=REDDIT_PASSWORD,
)


def get_posts_from_subreddit(subreddit: str = "Autoreel", limit: int = 15) -> str:
    """
    Retrieve posts from a custom feed (multireddit) on Reddit.

    :param subreddit: Name of the multireddit to query.
    :param limit: Maximum number of posts to retrieve.
    :return: A JSON string representing an array of post data.
    """
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

        return json.dumps(post_data)
    except ResponseException:
        raise HTTPException(status_code=401, detail="Failed to authenticate Reddit Account.")
    except NotFound:
        raise HTTPException(status_code=404, detail="Subreddit not found.")
    except Exception as ex:
        logging.error("get_posts_from_subreddit error: %s", ex)
        raise HTTPException(status_code=500, detail="Failed to fetch post.")


def save_post_db(post_id: str) -> str:
    """
    Fetch a post by ID and persist it in the local database.

    :param post_id: The Reddit post ID.
    :return: JSON representation of the saved Post.
    """
    try:
        retrieved_post = reddit.submission(id=post_id)
    except NotFound:
        raise HTTPException(status_code=404, detail="Post not found.")
    except Exception as ex:
        logging.error("save_post_db error retrieving post: %s", ex)
        raise HTTPException(status_code=500, detail="Problem retrieving post.")

    with Session(engine) as session:
        try:
            post_model = Post(
                id=retrieved_post.id,
                title=retrieved_post.title.strip(),
                url=retrieved_post.url.strip(),
                content=retrieved_post.selftext.strip(),
                subreddit=retrieved_post.subreddit.display_name.strip(),
            )
            session.add(post_model)
            session.commit()
            return post_model.model_dump_json()
        except IntegrityError:
            raise HTTPException(status_code=400, detail="Cannot save duplicate post.")
        except Exception as ex:
            logging.error("save_post_db error saving post: %s", ex)
            raise HTTPException(status_code=500, detail="Failed to save post.")


def get_saved_posts_db(offset: int = 0, limit: int = 15) -> list[Post]:
    """
    Retrieve previously saved posts from the database.

    :param offset: Offset for pagination.
    :param limit: Maximum number of posts to retrieve.
    :return: List of Post objects.
    """
    with Session(engine) as session:
        try:
            statement = select(Post).offset(offset).limit(limit)
            posts = session.exec(statement).all()
            return posts
        except Exception as ex:
            logging.error("get_saved_posts_db error: %s", ex)
            raise HTTPException(status_code=500, detail="Failed to get posts.")


def delete_saved_post_db(post_id: str) -> str:
    """
    Delete a post from the database.

    :param post_id: The post's ID.
    :return: The deleted post's ID.
    """
    with Session(engine) as session:
        try:
            statement = select(Post).where(Post.id == post_id)
            post = session.exec(statement).one()
            session.delete(post)
            session.commit()
            return post.id
        except NoResultFound:
            raise HTTPException(status_code=404, detail="Post not found.")
        except Exception as ex:
            logging.error("delete_saved_post_db error: %s", ex)
            raise HTTPException(status_code=500, detail="Failed to delete post.")


def patch_post_audio_db(post_id: str, post: Post) -> Post:
    """
    Update the audio_file_url field of a specific post.

    :param post_id: The target post's ID.
    :param post: A Post object with the new audio_file_url.
    :return: The updated Post object.
    """
    with Session(engine) as session:
        try:
            statement = select(Post).where(Post.id == post_id)
            saved_post = session.exec(statement).one()
            saved_post.audio_file_url = post.audio_file_url
            session.add(saved_post)
            session.commit()
            session.refresh(saved_post)
            return saved_post
        except NoResultFound:
            raise HTTPException(status_code=404, detail="Post not found.")
        except Exception as ex:
            logging.error("patch_post_audio_db error: %s", ex)
            raise HTTPException(status_code=500, detail="Failed to update post audio url.")


def use_post_db(post_id: str) -> Post:
    """
    Mark a specific post's 'used' flag as True.

    :param post_id: The target post's ID.
    :return: The updated Post object.
    """
    with Session(engine) as session:
        try:
            statement = select(Post).where(Post.id == post_id)
            saved_post = session.exec(statement).one()

            if saved_post.used:
                raise HTTPException(status_code=400, detail="Post already used.")

            saved_post.used = True
            session.add(saved_post)
            session.commit()
            session.refresh(saved_post)
            return saved_post
        except HTTPException as err:
            raise err
        except NoResultFound:
            raise HTTPException(status_code=404, detail="Post not found.")
        except Exception as ex:
            logging.error("use_post_db error: %s", ex)
            raise HTTPException(status_code=500, detail="Failed to update post status.")
