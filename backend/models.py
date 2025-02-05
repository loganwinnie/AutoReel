from typing import Optional

from sqlmodel import Field, SQLModel


class Post(SQLModel, table=True):
    id: str = Field(primary_key=True)
    title: str
    url: str
    content: str
    subreddit: str
    audio_file_url: str | None = None
    used: bool = False


class Video(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    video_url: str
    file_url: str
