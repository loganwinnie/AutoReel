from sqlmodel import SQLModel, create_engine
import models

from config import DATABASE_URL

engine = create_engine(DATABASE_URL, echo=True)
SQLModel.metadata.create_all(engine)