from dotenv import load_dotenv
from os import environ
from sqlmodel import SQLModel, create_engine


load_dotenv()

DATABASE_URL = environ.get("DATABASE_URL", None)
REDDIT_CLIENT_ID = environ.get("REDDIT_CLIENT_ID", None)
REDDIT_CLIENT_SECRET = environ.get("REDDIT_CLIENT_SECRET", None)
REDDIT_USER_AGENT = environ.get("REDDIT_USER_AGENT", None)
REDDIT_USERNAME = environ.get("REDDIT_USERNAME", None)
REDDIT_PASSWORD = environ.get("REDDIT_PASSWORD", None)

engine = create_engine(DATABASE_URL, echo=True)
SQLModel.metadata.create_all(engine)
